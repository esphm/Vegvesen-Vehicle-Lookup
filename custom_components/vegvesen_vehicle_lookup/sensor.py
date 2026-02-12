"""Sensor entities for vehicle attributes, diagnostics, and raw data."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SUPPORTED_ATTRIBUTES,
    AttributeDefinition,
    safe_get,
)
from .coordinator import VegvesenCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: VegvesenCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = []

    # Vehicle attribute sensors
    for attr_key, attr_def in SUPPORTED_ATTRIBUTES.items():
        entities.append(
            VegvesenAttributeSensor(coordinator, entry, attr_key, attr_def)
        )

    # Diagnostic sensors (always created)
    entities.append(VegvesenLastStatusSensor(coordinator, entry))
    entities.append(VegvesenLastUpdatedSensor(coordinator, entry))
    entities.append(VegvesenRawResponseSensor(coordinator, entry))

    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Base device-info mixin
# ---------------------------------------------------------------------------

class _VegvesenSensorBase(CoordinatorEntity[VegvesenCoordinator], SensorEntity):
    """Base class that shares device info and coordinator wiring."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Vegvesen Vehicle Lookup",
            manufacturer="Statens vegvesen",
            model="Kjøretøydata API",
            entry_type=DeviceEntryType.SERVICE,
        )


# ---------------------------------------------------------------------------
# Vehicle attribute sensor
# ---------------------------------------------------------------------------

class VegvesenAttributeSensor(_VegvesenSensorBase):
    """Sensor for a single curated vehicle attribute."""

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
        attr_key: str,
        attr_def: AttributeDefinition,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_key = attr_key
        self._attr_def = attr_def
        self._attr_unique_id = f"{entry.entry_id}_{attr_key}"
        self._attr_name = attr_def.name
        self._attr_icon = attr_def.icon
        self._attr_entity_registry_enabled_default = attr_def.enabled_default
        if attr_def.unit:
            self._attr_native_unit_of_measurement = attr_def.unit

    @property
    def native_value(self) -> Any | None:
        """Return the attribute value from the latest lookup data."""
        data = self.coordinator.data
        if not data:
            return None
        value = safe_get(data, *self._attr_def.path)
        # Convert numeric types to a string-safe representation
        if value is not None:
            return value
        return None


# ---------------------------------------------------------------------------
# Diagnostic: Last lookup status
# ---------------------------------------------------------------------------

class VegvesenLastStatusSensor(_VegvesenSensorBase):
    """Diagnostic sensor showing the last lookup status."""

    _attr_name = "Last Lookup Status"
    _attr_icon = "mdi:list-status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_status"

    @property
    def native_value(self) -> str:
        return self.coordinator.last_status


# ---------------------------------------------------------------------------
# Diagnostic: Last updated timestamp
# ---------------------------------------------------------------------------

class VegvesenLastUpdatedSensor(_VegvesenSensorBase):
    """Diagnostic sensor showing when data was last updated."""

    _attr_name = "Last Updated"
    _attr_icon = "mdi:clock-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_updated"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.last_updated_ts


# ---------------------------------------------------------------------------
# Diagnostic: Raw JSON response
# ---------------------------------------------------------------------------

class VegvesenRawResponseSensor(_VegvesenSensorBase):
    """Diagnostic sensor that exposes the raw API response for troubleshooting.

    State = "Available" / "No data".
    The truncated JSON is in extra_state_attributes.
    """

    _attr_name = "Raw Response"
    _attr_icon = "mdi:code-json"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False  # disabled by default

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_raw_response"

    @property
    def native_value(self) -> str:
        return "Available" if self.coordinator.raw_json else "No data"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        if self.coordinator.raw_json:
            attrs["raw_response"] = self.coordinator.raw_json
        return attrs
