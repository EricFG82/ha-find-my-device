"""Button platform for Find My Device integration."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GoogleFindMyDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Find My Device locate buttons."""
    coordinator: GoogleFindMyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_device_ids: set[str] = set()

    @callback
    def _async_add_new_buttons() -> None:
        """Add a locate button for devices new to the coordinator.

        Unlike the tracker/sensors, this isn't gated on already having a
        location - locating a device that doesn't have a fix yet is the whole
        point of the button.
        """
        new_entities = []
        for device_id, device_data in coordinator.data.items():
            if device_id in known_device_ids:
                continue
            known_device_ids.add(device_id)
            new_entities.append(
                GoogleFindMyLocateButton(coordinator, device_id, device_data)
            )
        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_buttons()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_buttons))


class GoogleFindMyLocateButton(CoordinatorEntity, ButtonEntity):
    """Button that forces a fresh location fetch for a single device.

    Bypasses the background update cache (`?force=true`) and can take up to
    ~30s to respond - meant for an occasional, explicit "where is it right
    now" check, not for repeated/automated use. Because it only re-fetches
    this one device rather than triggering a full coordinator refresh, it
    doesn't slow down polling for the rest of your devices.
    """

    _attr_icon = "mdi:crosshairs-gps"
    _attr_should_poll = False  # Use coordinator for updates
    _attr_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator: GoogleFindMyDataUpdateCoordinator,
        device_id: str,
        device_data: dict,
    ) -> None:
        """Initialize the locate button."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_data.get("name", "Unknown Device")
        self._device_type = device_data.get("device_type", "UNKNOWN")
        self._model = device_data.get("model")

        self._attr_unique_id = f"{device_id}_locate"
        self._attr_name = f"{self._device_name} Locate"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Find My Device",
            model=self._model or self._device_type,
        )

    async def async_press(self) -> None:
        """Request a fresh location for this device."""
        _LOGGER.info("Requesting a fresh location for device %s", self._device_id)
        try:
            await self.coordinator.async_locate_device(self._device_id)
        except Exception as err:
            _LOGGER.error(
                "Failed to locate device %s: %s", self._device_id, err
            )
            raise
