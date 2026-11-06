"""Shared entity helpers for Vegvesen Vehicle Lookup."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN


def build_device_info(entry_id: str) -> DeviceInfo:
    """Return the service device that groups all entities of an entry."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Vegvesen Vehicle Lookup",
        manufacturer="Statens vegvesen",
        model="Kjøretøydata API",
        entry_type=DeviceEntryType.SERVICE,
    )
