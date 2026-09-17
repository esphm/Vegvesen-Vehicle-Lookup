"""Tests for the Vegvesen Vehicle Lookup config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vegvesen_vehicle_lookup.const import CONF_API_KEY, DOMAIN


async def test_user_flow_creates_entry(hass) -> None:
    """A valid API key creates a config entry."""
    with patch(
        "custom_components.vegvesen_vehicle_lookup.config_flow."
        "VegvesenApi.async_validate_api_key",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_API_KEY: " secret "},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_API_KEY: "secret"}


async def test_user_flow_rejects_invalid_key(hass) -> None:
    """An invalid API key leaves the form open with an error."""
    with patch(
        "custom_components.vegvesen_vehicle_lookup.config_flow."
        "VegvesenApi.async_validate_api_key",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={CONF_API_KEY: "bad-key"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_only_one_entry_is_allowed(hass) -> None:
    """A second API key is unnecessary because one entry can look up any plate."""
    MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "first"}).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_reauthentication_updates_key(hass) -> None:
    """A replacement API key updates the existing entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "old-key"},
        unique_id="existing-id",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )
    assert result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.vegvesen_vehicle_lookup.config_flow."
        "VegvesenApi.async_validate_api_key",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_API_KEY: "new-key"},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data == {CONF_API_KEY: "new-key"}
