"""Sensor entities for vehicle attributes, diagnostics, and raw data."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import MAX_LENGTH_STATE_STATE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VegvesenConfigEntry
from .const import (
    SUPPORTED_ATTRIBUTES,
    AttributeDefinition,
    safe_get,
)
from .coordinator import VegvesenCoordinator
from .entity import build_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VegvesenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = entry.runtime_data.coordinator

    entities: list[SensorEntity] = []

    # Vehicle attribute sensors
    for attr_key, attr_def in SUPPORTED_ATTRIBUTES.items():
        entities.append(VegvesenAttributeSensor(coordinator, entry, attr_key, attr_def))

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
        entry: VegvesenConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = build_device_info(entry.entry_id)


# ---------------------------------------------------------------------------
# Vehicle attribute sensor
# ---------------------------------------------------------------------------


class VegvesenAttributeSensor(_VegvesenSensorBase):
    """Sensor for a single curated vehicle attribute."""

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: VegvesenConfigEntry,
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
        # Free-text fields can exceed the maximum length of a state
        if isinstance(value, str) and len(value) > MAX_LENGTH_STATE_STATE:
            return value[: MAX_LENGTH_STATE_STATE - 1] + "…"
        return value


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
        entry: VegvesenConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_status"

    @property
    def native_value(self) -> str:
        return self.coordinator.last_status

    @property
    def available(self) -> bool:
        """Keep diagnostics visible when the latest request failed."""
        return True


# ---------------------------------------------------------------------------
# Diagnostic: Last updated timestamp
# ---------------------------------------------------------------------------


class VegvesenLastUpdatedSensor(_VegvesenSensorBase):
    """Diagnostic sensor showing when data was last updated."""

    _attr_name = "Last Updated"
    _attr_icon = "mdi:clock-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: VegvesenConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_updated"

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.last_updated_ts is None:
            return None
        return dt_util.parse_datetime(self.coordinator.last_updated_ts)

    @property
    def available(self) -> bool:
        """Keep diagnostics visible when the latest request failed."""
        return True


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
    # The response can be large; keep it out of the recorder database
    _unrecorded_attributes = frozenset({"raw_response"})

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: VegvesenConfigEntry,
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
