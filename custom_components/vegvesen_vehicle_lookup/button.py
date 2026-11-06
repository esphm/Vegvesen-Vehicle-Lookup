"""Button entity to trigger an immediate vehicle lookup."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VegvesenConfigEntry
from .const import DOMAIN
from .entity import build_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VegvesenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button entity."""
    async_add_entities([VegvesenLookupButton(entry)])


class VegvesenLookupButton(ButtonEntity):
    """Button that triggers an immediate vehicle data lookup."""

    _attr_has_entity_name = True
    _attr_name = "Lookup Now"
    _attr_icon = "mdi:magnify"

    def __init__(self, entry: VegvesenConfigEntry) -> None:
        self._entry = entry
        self.coordinator = entry.runtime_data.coordinator
        self._attr_unique_id = f"{entry.entry_id}_lookup_now"
        self._attr_device_info = build_device_info(entry.entry_id)

    async def async_press(self) -> None:
        """Handle the button press – trigger immediate lookup."""
        if not self.coordinator.regnr:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_regnr",
            )
        if (text_entity := self._entry.runtime_data.text_entity) is not None:
            text_entity.cancel_pending_lookup()
        _LOGGER.debug("Lookup button pressed – refreshing data")
        await self.coordinator.async_request_refresh()
