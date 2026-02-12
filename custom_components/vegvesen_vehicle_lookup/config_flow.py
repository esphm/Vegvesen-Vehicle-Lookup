"""Config flow and options flow for Vegvesen Vehicle Lookup."""

from __future__ import annotations

import hashlib
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VegvesenApi, VegvesenAuthError, VegvesenConnectionError
from .const import (
    CONF_API_KEY,
    CONF_DEBOUNCE_SECONDS,
    CONF_FALLBACK_LOOKUP_SECONDS,
    DEFAULT_DEBOUNCE_SECONDS,
    DEFAULT_FALLBACK_LOOKUP_SECONDS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)


class VegvesenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vegvesen Vehicle Lookup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step – API key entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()

            # Unique ID = truncated hash of the key (prevents duplicates)
            unique_id = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Validate the key against the API
            session = async_get_clientsession(self.hass)
            api = VegvesenApi(session, api_key)

            try:
                valid = await api.async_validate_api_key()
                if not valid:
                    errors["base"] = "invalid_auth"
            except VegvesenAuthError:
                errors["base"] = "invalid_auth"
            except VegvesenConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during API key validation")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="Vegvesen Vehicle Lookup",
                    data={CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VegvesenOptionsFlowHandler:
        """Create the options flow."""
        return VegvesenOptionsFlowHandler(config_entry)


class VegvesenOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Vegvesen Vehicle Lookup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DEBOUNCE_SECONDS,
                    default=current.get(
                        CONF_DEBOUNCE_SECONDS, DEFAULT_DEBOUNCE_SECONDS
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=300)),
                vol.Optional(
                    CONF_FALLBACK_LOOKUP_SECONDS,
                    default=current.get(
                        CONF_FALLBACK_LOOKUP_SECONDS,
                        DEFAULT_FALLBACK_LOOKUP_SECONDS,
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=600)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
