"""The Vegvesen Vehicle Lookup integration."""

from __future__ import annotations

import logging
import re

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VegvesenApi
from .const import (
    ATTR_REGNR,
    CONF_API_KEY,
    DOMAIN,
    PLATFORMS,
    REGNR_PATTERN,
    SERVICE_LOOKUP,
)
from .coordinator import VegvesenCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_REGNR): str,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vegvesen Vehicle Lookup from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_key = entry.data[CONF_API_KEY]
    session = async_get_clientsession(hass)
    api = VegvesenApi(session, api_key)

    coordinator = VegvesenCoordinator(hass, api, entry)

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "text_entity": None,  # populated by text.py
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register domain-level service (once)
    _register_services(hass)

    # Reload integration when options change (rebuild sensors)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))

    return True


async def _async_update_options(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Reload integration when options are changed."""
    _LOGGER.debug("Options changed – reloading integration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    # Remove service if no remaining entries
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_LOOKUP)

    return unload_ok


def _register_services(hass: HomeAssistant) -> None:
    """Register the vegvesen_vehicle_lookup.lookup service (idempotent)."""
    if hass.services.has_service(DOMAIN, SERVICE_LOOKUP):
        return

    async def _handle_lookup(call: ServiceCall) -> None:
        """Handle the lookup service call."""
        regnr_raw: str | None = call.data.get(ATTR_REGNR)

        # Find the first available coordinator
        for entry_id, entry_data in hass.data.get(DOMAIN, {}).items():
            if not isinstance(entry_data, dict):
                continue
            coordinator: VegvesenCoordinator = entry_data["coordinator"]

            if regnr_raw:
                normalized = regnr_raw.upper().replace(" ", "")
                if not re.match(REGNR_PATTERN, normalized):
                    _LOGGER.warning(
                        "Service call with invalid regnr format: %s",
                        regnr_raw,
                    )
                    return

                coordinator.regnr = normalized

                # Keep text entity in sync (without triggering debounce)
                text_entity = entry_data.get("text_entity")
                if text_entity is not None:
                    text_entity.set_regnr_from_service(normalized)

            await coordinator.async_request_refresh()
            break  # service affects first entry only

    hass.services.async_register(
        DOMAIN, SERVICE_LOOKUP, _handle_lookup, schema=SERVICE_SCHEMA
    )
