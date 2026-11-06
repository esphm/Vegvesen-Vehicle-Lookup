"""The Vegvesen Vehicle Lookup integration."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

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

if TYPE_CHECKING:
    from .text import VegvesenRegnrText

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_REGNR): cv.string,
    }
)


@dataclass
class VegvesenRuntimeData:
    """Runtime objects shared by the platforms of one config entry."""

    coordinator: VegvesenCoordinator
    api: VegvesenApi
    text_entity: VegvesenRegnrText | None = None


type VegvesenConfigEntry = ConfigEntry[VegvesenRuntimeData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the integration's actions."""

    async def _handle_lookup(call: ServiceCall) -> None:
        """Handle the lookup action."""
        entries: list[VegvesenConfigEntry] = [
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.state is ConfigEntryState.LOADED
        ]
        if not entries:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_loaded",
            )

        runtime = entries[0].runtime_data
        coordinator = runtime.coordinator
        text_entity = runtime.text_entity

        if regnr_raw := call.data.get(ATTR_REGNR):
            normalized = regnr_raw.upper().replace(" ", "")
            if not re.fullmatch(REGNR_PATTERN, normalized):
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="invalid_regnr",
                    translation_placeholders={"regnr": regnr_raw},
                )
            coordinator.regnr = normalized
            # Keep the text entity in sync without triggering its debounce
            if text_entity is not None:
                text_entity.set_regnr_from_service(normalized)
        else:
            if not coordinator.regnr:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="no_regnr",
                )
            if text_entity is not None:
                text_entity.cancel_pending_lookup()

        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_LOOKUP, _handle_lookup, schema=SERVICE_SCHEMA
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: VegvesenConfigEntry) -> bool:
    """Set up Vegvesen Vehicle Lookup from a config entry."""
    api = VegvesenApi(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    coordinator = VegvesenCoordinator(hass, api, entry)
    entry.runtime_data = VegvesenRuntimeData(coordinator=coordinator, api=api)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload integration when options change
    entry.async_on_unload(entry.add_update_listener(_async_update_options))

    return True


async def _async_update_options(
    hass: HomeAssistant, entry: VegvesenConfigEntry
) -> None:
    """Reload integration when options are changed."""
    _LOGGER.debug("Options changed – reloading integration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: VegvesenConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
