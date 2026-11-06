"""Tests for setup, the lookup action, and entities."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import MAX_LENGTH_STATE_STATE
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vegvesen_vehicle_lookup.const import (
    CONF_API_KEY,
    DOMAIN,
    SERVICE_LOOKUP,
    SUPPORTED_ATTRIBUTES,
)
from custom_components.vegvesen_vehicle_lookup.sensor import VegvesenAttributeSensor

VEHICLE = {
    "kjoretoyId": {"kjennemerke": "AB 12345"},
    "godkjenning": {"kjoretoymerknad": [{"merknad": "x" * 400}]},
}


@pytest.fixture
async def setup_entry(hass):
    """Set up a loaded config entry with a mocked API."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "secret"})
    entry.add_to_hass(hass)
    with patch(
        "custom_components.vegvesen_vehicle_lookup.VegvesenApi.async_lookup",
        new=AsyncMock(return_value=VEHICLE),
    ) as lookup:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry, lookup


async def test_setup_and_unload(hass, setup_entry) -> None:
    """The entry loads, stores runtime data, and unloads cleanly."""
    entry, _ = setup_entry
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.text_entity is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
    # The action is registered in async_setup and survives unloading
    assert hass.services.has_service(DOMAIN, SERVICE_LOOKUP)


async def test_lookup_action_updates_entities(hass, setup_entry) -> None:
    """The action normalizes the plate, looks it up, and updates the text entity."""
    entry, lookup = setup_entry

    await hass.services.async_call(
        DOMAIN, SERVICE_LOOKUP, {"regnr": "ab 12345"}, blocking=True
    )
    await hass.async_block_till_done()

    lookup.assert_awaited_once_with("AB12345")
    assert entry.runtime_data.coordinator.last_status == "success"
    text_state = hass.states.get(
        "text.vegvesen_vehicle_lookup_vehicle_registration_number"
    )
    assert text_state.state == "AB12345"
    assert (
        hass.states.get("sensor.vegvesen_vehicle_lookup_registration_number").state
        == "AB 12345"
    )


async def test_lookup_action_rejects_invalid_plate(hass, setup_entry) -> None:
    """An invalid plate raises a translated validation error."""
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, SERVICE_LOOKUP, {"regnr": "123"}, blocking=True
        )
    assert err.value.translation_key == "invalid_regnr"


async def test_lookup_action_without_plate(hass, setup_entry) -> None:
    """Calling the action with no plate set raises a validation error."""
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(DOMAIN, SERVICE_LOOKUP, {}, blocking=True)
    assert err.value.translation_key == "no_regnr"


async def test_lookup_action_without_entry(hass) -> None:
    """The action explains that the integration is not loaded."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "secret"})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await hass.config_entries.async_unload(entry.entry_id)

    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, SERVICE_LOOKUP, {"regnr": "AB12345"}, blocking=True
        )
    assert err.value.translation_key == "not_loaded"


async def test_long_text_is_truncated(hass, setup_entry) -> None:
    """Free-text values longer than a state allows are truncated."""
    entry, _ = setup_entry
    coordinator = entry.runtime_data.coordinator
    coordinator.regnr = "AB12345"
    await coordinator.async_refresh()

    # The remarks sensor is disabled by default, so test the entity directly
    sensor = VegvesenAttributeSensor(
        coordinator,
        entry,
        "vehicle_remarks",
        SUPPORTED_ATTRIBUTES["vehicle_remarks"],
    )
    assert len(sensor.native_value) == MAX_LENGTH_STATE_STATE
    assert sensor.native_value.endswith("…")
