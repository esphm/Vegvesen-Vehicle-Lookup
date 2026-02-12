"""Text entity for entering a vehicle registration number."""

from __future__ import annotations

import logging
import re

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_DEBOUNCE_SECONDS,
    CONF_FALLBACK_LOOKUP_SECONDS,
    DEFAULT_DEBOUNCE_SECONDS,
    DEFAULT_FALLBACK_LOOKUP_SECONDS,
    DOMAIN,
    REGNR_PATTERN,
)
from .coordinator import VegvesenCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the text entity."""
    coordinator: VegvesenCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entity = VegvesenRegnrText(coordinator, entry)
    async_add_entities([entity])

    # Register the text entity so the service handler can reach it
    hass.data[DOMAIN][entry.entry_id]["text_entity"] = entity


class VegvesenRegnrText(TextEntity, RestoreEntity):
    """Editable text entity for the vehicle registration number."""

    _attr_has_entity_name = True
    _attr_name = "Vehicle Registration Number"
    _attr_icon = "mdi:card-text-outline"
    _attr_mode = TextMode.TEXT
    _attr_native_min = 7
    _attr_native_max = 7
    _attr_pattern = r"[A-Za-z]{2}\d{5}"

    def __init__(
        self,
        coordinator: VegvesenCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_regnr_input"
        self._attr_native_value: str | None = None
        self._debounce_unsub: CALLBACK_TYPE | None = None
        self._fallback_unsub: CALLBACK_TYPE | None = None

    # -- Device info -----------------------------------------------------------

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Vegvesen Vehicle Lookup",
            manufacturer="Statens vegvesen",
            model="Kjøretøydata API",
            entry_type=DeviceEntryType.SERVICE,
        )

    # -- Lifecycle -------------------------------------------------------------

    async def async_added_to_hass(self) -> None:
        """Restore previous value and trigger initial lookup."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable", ""):
            restored = last_state.state.upper().replace(" ", "")
            if re.match(REGNR_PATTERN, restored):
                self._attr_native_value = restored
                self.coordinator.regnr = restored
                _LOGGER.debug("Restored regnr: %s – triggering lookup", restored)
                # Schedule initial lookup shortly after startup
                async_call_later(
                    self.hass, 5, self._startup_lookup
                )

    async def async_will_remove_from_hass(self) -> None:
        """Cancel pending timers."""
        self._cancel_debounce()
        self._cancel_fallback()

    # -- Public API for TextEntity ---------------------------------------------

    async def async_set_value(self, value: str) -> None:
        """Called when the user sets a new value from the UI."""
        normalized = value.upper().replace(" ", "")
        self._attr_native_value = normalized
        self.async_write_ha_state()

        if re.match(REGNR_PATTERN, normalized):
            self.coordinator.regnr = normalized
            self._schedule_debounced_lookup()
        else:
            _LOGGER.debug("Value '%s' does not match regnr pattern – no lookup", value)

    def set_regnr_from_service(self, value: str) -> None:
        """Set the displayed value *without* triggering debounce.

        Used by the service handler to keep the text entity in sync.
        """
        self._attr_native_value = value
        self._cancel_debounce()
        self._cancel_fallback()
        self.async_write_ha_state()

    # -- Debounce logic --------------------------------------------------------

    def _schedule_debounced_lookup(self) -> None:
        """(Re)start the debounce timer. Also start the fallback timer if needed."""
        debounce = self._entry.options.get(
            CONF_DEBOUNCE_SECONDS, DEFAULT_DEBOUNCE_SECONDS
        )
        fallback = self._entry.options.get(
            CONF_FALLBACK_LOOKUP_SECONDS, DEFAULT_FALLBACK_LOOKUP_SECONDS
        )

        # Restart debounce
        self._cancel_debounce()
        if debounce > 0:
            self._debounce_unsub = async_call_later(
                self.hass, debounce, self._debounce_fire
            )
        else:
            # No debounce – trigger immediately
            self.hass.async_create_task(self._trigger_lookup())
            return

        # Start fallback timer (only if not already running)
        if self._fallback_unsub is None and fallback > 0:
            self._fallback_unsub = async_call_later(
                self.hass, fallback, self._fallback_fire
            )

    @callback
    def _debounce_fire(self, _now) -> None:
        """Debounce timer expired – perform lookup."""
        self._debounce_unsub = None
        self._cancel_fallback()
        self.hass.async_create_task(self._trigger_lookup())

    @callback
    def _fallback_fire(self, _now) -> None:
        """Fallback timer expired – force lookup regardless of debounce."""
        _LOGGER.debug("Fallback timer expired – forcing lookup")
        self._fallback_unsub = None
        self._cancel_debounce()
        self.hass.async_create_task(self._trigger_lookup())

    @callback
    def _startup_lookup(self, _now) -> None:
        """Initial lookup after HA start."""
        self.hass.async_create_task(self._trigger_lookup())

    async def _trigger_lookup(self) -> None:
        """Request a refresh from the coordinator."""
        await self.coordinator.async_request_refresh()

    def _cancel_debounce(self) -> None:
        if self._debounce_unsub is not None:
            self._debounce_unsub()
            self._debounce_unsub = None

    def _cancel_fallback(self) -> None:
        if self._fallback_unsub is not None:
            self._fallback_unsub()
            self._fallback_unsub = None
