"""DataUpdateCoordinator for Vegvesen Vehicle Lookup."""

from __future__ import annotations

import json
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
import homeassistant.util.dt as dt_util

from .api import (
    VegvesenApi,
    VegvesenApiError,
    VegvesenAuthError,
    VegvesenConnectionError,
    VegvesenNotFoundError,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_RAW_JSON_SIZE = 16384  # 16 KB


class VegvesenCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that fetches vehicle data on demand (no polling)."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: VegvesenApi,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # manual refresh only
        )
        self.api = api
        self.config_entry = entry

        # Runtime state
        self.regnr: str | None = None
        self.last_status: str = "idle"
        self.last_updated_ts: str | None = None
        self.raw_json: str | None = None

    # ------------------------------------------------------------------
    # Core update
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        """Fetch vehicle data from the API.

        Called by async_request_refresh().
        """
        if not self.regnr:
            _LOGGER.debug("No registration number set – skipping lookup")
            return self.data or {}

        _LOGGER.debug("Looking up vehicle: %s", self.regnr)

        try:
            data = await self.api.async_lookup(self.regnr)
        except VegvesenAuthError as err:
            self.last_status = "auth_error"
            _LOGGER.error("Authentication error during lookup: %s", err)
            raise UpdateFailed(f"Authentication error: {err}") from err
        except VegvesenNotFoundError:
            self.last_status = "not_found"
            self.last_updated_ts = dt_util.utcnow().isoformat()
            _LOGGER.info("Vehicle not found for registration number: %s", self.regnr)
            # Return empty dict – not an UpdateFailed (user mistake, not infra)
            self.raw_json = None
            return {}
        except VegvesenConnectionError as err:
            self.last_status = "connection_error"
            _LOGGER.warning("Connection error during lookup: %s", err)
            raise UpdateFailed(f"Connection error: {err}") from err
        except VegvesenApiError as err:
            self.last_status = f"error"
            _LOGGER.error("API error during lookup: %s", err)
            raise UpdateFailed(str(err)) from err

        self.last_status = "success"
        self.last_updated_ts = dt_util.utcnow().isoformat()

        # Store truncated raw JSON for the diagnostic entity
        try:
            raw = json.dumps(data, ensure_ascii=False)
            self.raw_json = raw[:MAX_RAW_JSON_SIZE]
        except (TypeError, ValueError):
            self.raw_json = None

        _LOGGER.debug("Lookup successful for %s", self.regnr)
        return data
