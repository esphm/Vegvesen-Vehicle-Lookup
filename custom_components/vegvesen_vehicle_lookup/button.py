"""Button entity to trigger an immediate vehicle lookup."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VegvesenCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button entity."""
    coordinator: VegvesenCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([VegvesenLookupButton(coordinator, entry)])


class VegvesenLookupButton(ButtonEntity):
    """Button that triggers an immediate vehicle data lookup."""

    _attr_has_entity_name = True
    _attr_name = "Lookup Now"
    _attr_icon = "mdi:magnify"

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_lookup_now"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Vegvesen Vehicle Lookup",
            manufacturer="Statens vegvesen",
            model="Kjøretøydata API",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press – trigger immediate lookup."""
        if not self.coordinator.regnr:
            _LOGGER.warning(
                "Lookup button pressed but no registration number is set"
            )
            return
        _LOGGER.debug("Lookup button pressed – refreshing data")
        await self.coordinator.async_request_refresh()
