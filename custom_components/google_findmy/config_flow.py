"""Config flow for Google Find My Device integration."""

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_URL, DEFAULT_API_URL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Google Find My Device"): str,
        vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
    }
)


async def validate_api_connection(hass: HomeAssistant, api_url: str) -> dict[str, Any]:
    """Validate the API connection."""
    session = async_get_clientsession(hass)
    
    try:
        async with async_timeout.timeout(10):
            async with session.get(f"{api_url.rstrip('/')}/health") as response:
                response.raise_for_status()
                data = await response.json()
                
                if data.get("status") != "healthy":
                    raise ConnectionError("API is not healthy")
                
                return {"title": "Google Find My Device"}
                
    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)
        raise ConnectionError(f"Cannot connect to API: {err}") from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise


class GoogleFindMyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Find My Device."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_api_connection(
                    self.hass, user_input[CONF_API_URL]
                )
                
                # Create unique ID based on API URL
                await self.async_set_unique_id(user_input[CONF_API_URL])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_API_URL: user_input[CONF_API_URL],
                    },
                )
                
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

