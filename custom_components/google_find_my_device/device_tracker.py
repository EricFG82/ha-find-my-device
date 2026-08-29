"""Device tracker platform for Google Find My Device integration."""

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GoogleFindMyDataUpdateCoordinator
from .const import (
    DOMAIN,
    ATTR_DEVICE_ID,
    ATTR_DEVICE_TYPE,
    ATTR_MODEL,
    ATTR_BATTERY_LEVEL,
    ATTR_ACCURACY,
    ATTR_LOCATION_TIMESTAMP,
    ATTR_STATUS,
    ATTR_IMAGE_URL,
    ATTR_IDENTIFIER_TYPE,
    ATTR_MODEL_ID,
    ATTR_OWNER_KEY_VERSION,
    ATTR_GOOGLE_MAPS_LINK,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Google Find My Device trackers."""
    coordinator: GoogleFindMyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_device_ids: set[str] = set()

    @callback
    def _async_add_new_trackers() -> None:
        """Add trackers for devices that have gained location data since the last check.

        Devices only get a tracker once they have a location - a brand new device,
        or one whose first location fetch hasn't completed yet (e.g. right after a
        restart of the REST API), won't have one immediately. Without this listener
        that device would never get a tracker at all, since entities are otherwise
        only created once at setup time.
        """
        new_entities = []
        for device_id, device_data in coordinator.data.items():
            if device_id in known_device_ids:
                continue
            if device_data.get("location"):
                known_device_ids.add(device_id)
                new_entities.append(
                    GoogleFindMyDeviceTracker(coordinator, device_id, device_data)
                )
        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_trackers()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_trackers))


class GoogleFindMyDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Device tracker for Google Find My Device."""

    _attr_icon = "mdi:map-marker"
    _attr_should_poll = False  # Use coordinator for updates

    def __init__(
        self,
        coordinator: GoogleFindMyDataUpdateCoordinator,
        device_id: str,
        device_data: dict,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_data.get("name", "Unknown Device")
        self._device_type = device_data.get("device_type", "UNKNOWN")
        self._model = device_data.get("model")

        self._attr_unique_id = f"{device_id}_tracker"
        self._attr_name = f"{self._device_name}"

        _LOGGER.debug(
            "Initialized device tracker for %s (ID: %s)",
            self._device_name,
            device_id
        )
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Google Find My Device",
            model=self._model or self._device_type,
        )
    
    @property
    def device_data(self) -> dict:
        """Get the latest device data from coordinator."""
        return self.coordinator.data.get(self._device_id, {})
    
    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS
    
    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        location = self.device_data.get("location")
        if location:
            return location.get("latitude")
        return None
    
    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        location = self.device_data.get("location")
        if location:
            return location.get("longitude")
        return None
    
    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        location = self.device_data.get("location")
        if location and location.get("accuracy"):
            return int(location["accuracy"])
        return 0
    
    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        return self.device_data.get("battery_level")

    @property
    def entity_picture(self) -> str | None:
        """Return the entity picture to use in the frontend."""
        data = self.device_data

        # Try to get imageUrl from additional_info first
        additional_info = data.get("additional_info", {})
        if additional_info and "imageUrl" in additional_info:
            return additional_info["imageUrl"]

        # Fallback to imageUrl at root level
        if "imageUrl" in data:
            return data["imageUrl"]

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data = self.device_data
        location = data.get("location", {})

        attrs = {
            ATTR_DEVICE_ID: self._device_id,
            ATTR_DEVICE_TYPE: data.get("device_type"),
            ATTR_STATUS: data.get("status"),
        }

        if data.get("model"):
            attrs[ATTR_MODEL] = data["model"]

        if data.get("battery_level") is not None:
            attrs[ATTR_BATTERY_LEVEL] = data["battery_level"]

        if location.get("accuracy") is not None:
            attrs[ATTR_ACCURACY] = location["accuracy"]

        if location.get("timestamp"):
            attrs[ATTR_LOCATION_TIMESTAMP] = location["timestamp"]

        # Add all additional_info properties as attributes
        additional_info = data.get("additional_info", {})
        if additional_info:
            # Map additional_info keys to attribute constants
            key_mapping = {
                "imageUrl": ATTR_IMAGE_URL,
                "identifierType": ATTR_IDENTIFIER_TYPE,
                "modelId": ATTR_MODEL_ID,
                "ownerKeyVersion": ATTR_OWNER_KEY_VERSION,
                "google_maps_link": ATTR_GOOGLE_MAPS_LINK,
            }

            for key, value in additional_info.items():
                # Use mapped constant if available, otherwise use the original key
                attr_name = key_mapping.get(key, key)
                attrs[attr_name] = value

        # Fallback: Add image URL from top-level data if not in additional_info
        if ATTR_IMAGE_URL not in attrs and "imageUrl" in data:
            attrs[ATTR_IMAGE_URL] = data["imageUrl"]

        return attrs
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.device_data.get("location") is not None
            and self.latitude is not None
            and self.longitude is not None
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "Coordinator update received for device %s - Lat: %s, Lon: %s",
            self._device_id,
            self.latitude,
            self.longitude
        )
        super()._handle_coordinator_update()

