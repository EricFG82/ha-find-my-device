"""
Google Find My Device Integration for Home Assistant.

This integration connects to the Google Find My Device REST API service
to provide device tracking and monitoring capabilities.
"""

import logging
from datetime import timedelta

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_URL,
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Find My Device from a config entry."""
    api_url = entry.data[CONF_API_URL]
    
    # Create API client
    session = async_get_clientsession(hass)
    api_client = GoogleFindMyAPIClient(api_url, session)
    
    # Test the connection
    try:
        await api_client.test_connection()
    except Exception as err:
        _LOGGER.error("Failed to connect to Google Find My API: %s", err)
        raise ConfigEntryNotReady from err
    
    # Create update coordinator
    coordinator = GoogleFindMyDataUpdateCoordinator(
        hass,
        api_client,
        entry,
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class GoogleFindMyAPIClient:
    """API client for Google Find My Device REST API."""
    
    def __init__(self, api_url: str, session: aiohttp.ClientSession):
        """Initialize the API client."""
        self.api_url = api_url.rstrip('/')
        self.session = session
    
    async def test_connection(self) -> bool:
        """Test the connection to the API."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(f"{self.api_url}/health") as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("status") == "healthy"
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            raise
    
    async def get_devices(self) -> list:
        """Get all devices."""
        try:
            async with async_timeout.timeout(30):
                async with self.session.get(
                    f"{self.api_url}/api/v1/devices"
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching devices: %s", err)
            raise UpdateFailed(f"Error fetching devices: {err}") from err
    
    async def get_device_detail(self, device_id: str) -> dict:
        """Get detailed information for a specific device."""
        try:
            async with async_timeout.timeout(30):
                async with self.session.get(
                    f"{self.api_url}/api/v1/devices/{device_id}"
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching device detail for %s: %s", device_id, err)
            raise UpdateFailed(f"Error fetching device detail: {err}") from err


class GoogleFindMyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Google Find My Device data."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api_client: GoogleFindMyAPIClient,
        entry: ConfigEntry,
    ):
        """Initialize the coordinator."""
        self.api_client = api_client
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            always_update=True,  # Force updates even if data hasn't changed
        )
        _LOGGER.info(
            "Initialized coordinator with update interval of %d seconds",
            DEFAULT_SCAN_INTERVAL
        )
    
    async def _async_update_data(self):
        """Fetch data from API."""
        _LOGGER.debug("Starting data update for Google Find My Device")
        try:
            # Get list of devices
            devices = await self.api_client.get_devices()
            _LOGGER.debug("Fetched %d devices from API", len(devices))

            # Get detailed information for each device
            device_details = {}
            for device in devices:
                device_id = device["device_id"]
                try:
                    detail = await self.api_client.get_device_detail(device_id)
                    device_details[device_id] = detail
                    _LOGGER.debug(
                        "Updated device %s - Location: %s",
                        device_id,
                        detail.get("location")
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to fetch detail for device %s: %s",
                        device_id,
                        err
                    )
                    # Use basic device info if detail fetch fails
                    device_details[device_id] = device

            _LOGGER.info("Successfully updated %d devices", len(device_details))
            return device_details

        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

