"""API client for Statens vegvesen vehicle data lookup."""

from __future__ import annotations

import asyncio
import logging

import aiohttp

from .const import API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class VegvesenApiError(Exception):
    """Base exception for Vegvesen API errors."""


class VegvesenAuthError(VegvesenApiError):
    """Authentication / authorisation error (401/403)."""


class VegvesenNotFoundError(VegvesenApiError):
    """Vehicle not found (404)."""


class VegvesenConnectionError(VegvesenApiError):
    """Network / timeout error."""


class VegvesenApi:
    """Async client for the Vegvesen enkeltoppslag API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    # -- public ----------------------------------------------------------------

    async def async_lookup(self, regnr: str) -> dict:
        """Look up vehicle data by registration number.

        Returns the first vehicle object from kjoretoydataListe.
        Raises typed exceptions on error.
        """
        url = f"{API_BASE_URL}?kjennemerke={regnr}"
        headers = {
            "Accept": "application/json",
            "SVV-Authorization": f"Apikey {self._api_key}",
        }

        resp = await self._request(url, headers)

        # Parse JSON
        try:
            data = await resp.json()
        except (ValueError, aiohttp.ContentTypeError) as err:
            raise VegvesenApiError(
                f"Failed to parse JSON response: {err}"
            ) from err

        # Extract vehicle from wrapper
        return self._extract_vehicle(data, regnr)

    async def async_validate_api_key(self) -> bool:
        """Validate the API key by issuing a test request.

        Returns True when the key is accepted (any 2xx/4xx except 401/403).
        Returns False on 401/403.
        Raises VegvesenConnectionError on network problems.
        """
        url = f"{API_BASE_URL}?kjennemerke=AA00000"
        headers = {
            "Accept": "application/json",
            "SVV-Authorization": f"Apikey {self._api_key}",
        }

        try:
            async with asyncio.timeout(API_TIMEOUT):
                resp = await self._session.get(url, headers=headers)
        except asyncio.TimeoutError as err:
            raise VegvesenConnectionError("Validation request timed out") from err
        except aiohttp.ClientError as err:
            raise VegvesenConnectionError(
                f"Connection error during validation: {err}"
            ) from err

        if resp.status in (401, 403):
            return False

        # 200, 404, 400 etc. all indicate the key itself is valid.
        return True

    # -- private ---------------------------------------------------------------

    async def _request(
        self, url: str, headers: dict
    ) -> aiohttp.ClientResponse:
        """Execute an HTTP GET with timeout and translate errors."""
        try:
            async with asyncio.timeout(API_TIMEOUT):
                resp = await self._session.get(url, headers=headers)
        except asyncio.TimeoutError as err:
            raise VegvesenConnectionError("Request timed out") from err
        except aiohttp.ClientError as err:
            raise VegvesenConnectionError(
                f"Connection error: {err}"
            ) from err

        if resp.status in (401, 403):
            raise VegvesenAuthError(
                f"Authentication failed (HTTP {resp.status}). "
                "Check your API key."
            )
        if resp.status == 400:
            _LOGGER.warning(
                "HTTP 400 from Vegvesen API – the registration number "
                "may be invalid"
            )
            raise VegvesenApiError(
                "Invalid request (HTTP 400). Check registration number format."
            )
        if resp.status == 404:
            raise VegvesenNotFoundError("Vehicle not found (HTTP 404)")
        if resp.status >= 500:
            _LOGGER.error("Vegvesen API server error: HTTP %s", resp.status)
            raise VegvesenApiError(f"Server error (HTTP {resp.status})")
        if resp.status != 200:
            raise VegvesenApiError(f"Unexpected HTTP status: {resp.status}")

        return resp

    @staticmethod
    def _extract_vehicle(data: dict, regnr: str) -> dict:
        """Extract the vehicle dict from a KjoretoydataResponse."""
        if isinstance(data, dict):
            # Standard response: { kjoretoydataListe: [ … ] }
            if "kjoretoydataListe" in data:
                items = data["kjoretoydataListe"]
                if not items:
                    raise VegvesenNotFoundError(
                        f"No vehicle data returned for {regnr}"
                    )
                return items[0]
            # Possible direct vehicle object (fallback)
            if "kjoretoyId" in data:
                return data
        _LOGGER.warning(
            "Unexpected API response structure – returning raw data"
        )
        return data if isinstance(data, dict) else {}
