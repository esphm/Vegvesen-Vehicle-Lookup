"""Tests for the Vegvesen data update coordinator."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vegvesen_vehicle_lookup.api import (
    VegvesenAuthError,
    VegvesenNotFoundError,
)
from custom_components.vegvesen_vehicle_lookup.const import CONF_API_KEY, DOMAIN
from custom_components.vegvesen_vehicle_lookup.coordinator import VegvesenCoordinator


def create_coordinator(hass, api) -> VegvesenCoordinator:
    """Create a coordinator for a test."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "secret"})
    return VegvesenCoordinator(hass, api, entry)


async def test_successful_update_records_diagnostics(hass) -> None:
    """Successful lookups update data and diagnostic fields."""
    api = AsyncMock()
    api.async_lookup.return_value = {"kjoretoyId": {"kjennemerke": "AB12345"}}
    coordinator = create_coordinator(hass, api)
    coordinator.regnr = "AB12345"

    result = await coordinator._async_update_data()

    assert result == {"kjoretoyId": {"kjennemerke": "AB12345"}}
    assert coordinator.last_status == "success"
    assert coordinator.last_updated_ts is not None
    assert '"kjennemerke": "AB12345"' in coordinator.raw_json


async def test_not_found_clears_previous_data(hass) -> None:
    """A missing vehicle is a valid empty result rather than an outage."""
    api = AsyncMock()
    api.async_lookup.side_effect = VegvesenNotFoundError
    coordinator = create_coordinator(hass, api)
    coordinator.regnr = "AB12345"
    coordinator.raw_json = "stale"

    assert await coordinator._async_update_data() == {}
    assert coordinator.last_status == "not_found"
    assert coordinator.raw_json is None


async def test_authentication_failure_starts_reauthentication(hass) -> None:
    """Rejected credentials are surfaced as a config-entry auth failure."""
    api = AsyncMock()
    api.async_lookup.side_effect = VegvesenAuthError
    coordinator = create_coordinator(hass, api)
    coordinator.regnr = "AB12345"

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()

    assert coordinator.last_status == "auth_error"
    assert coordinator.last_updated_ts is not None
