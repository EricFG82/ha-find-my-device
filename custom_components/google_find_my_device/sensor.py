"""Sensor platform for Google Find My Device integration."""

from datetime import datetime, timezone
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
    ATTR_LAST_SEEN,
    ATTR_STATUS,
    ATTR_LOCATION_TIMESTAMP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Google Find My Device sensors."""
    coordinator: GoogleFindMyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_last_seen_ids: set[str] = set()
    known_battery_ids: set[str] = set()

    @callback
    def _async_add_new_sensors() -> None:
        """Add sensors for devices new to the coordinator, or that just gained battery data.

        Entities are otherwise only created once at setup time, so a device added to
        the Google account later - or one whose battery data wasn't available yet on
        the first refresh (e.g. right after a restart of the REST API) - would never
        get a sensor without this listener.
        """
        new_entities = []
        for device_id, device_data in coordinator.data.items():
            if device_id not in known_last_seen_ids:
                known_last_seen_ids.add(device_id)
                new_entities.append(
                    GoogleFindMyLastSeenSensor(coordinator, device_id, device_data)
                )

            if (
                device_id not in known_battery_ids
                and device_data.get("battery_level") is not None
            ):
                known_battery_ids.add(device_id)
                new_entities.append(
                    GoogleFindMyBatterySensor(coordinator, device_id, device_data)
                )

        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_sensors()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_sensors))


class GoogleFindMyBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Google Find My Device sensors."""

    _attr_should_poll = False  # Use coordinator for updates

    def __init__(
        self,
        coordinator: GoogleFindMyDataUpdateCoordinator,
        device_id: str,
        device_data: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_data.get("name", "Unknown Device")
        self._device_type = device_data.get("device_type", "UNKNOWN")
        self._model = device_data.get("model")
    
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
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data = self.device_data
        attrs = {
            ATTR_DEVICE_ID: self._device_id,
            ATTR_DEVICE_TYPE: data.get("device_type"),
            ATTR_STATUS: data.get("status"),
        }

        if data.get("model"):
            attrs[ATTR_MODEL] = data["model"]

        return attrs

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "Coordinator update received for sensor %s",
            self._device_id
        )
        super()._handle_coordinator_update()


class GoogleFindMyBatterySensor(GoogleFindMyBaseSensor):
    """Battery level sensor for Google Find My Device."""
    
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    
    def __init__(
        self,
        coordinator: GoogleFindMyDataUpdateCoordinator,
        device_id: str,
        device_data: dict,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, device_id, device_data)
        self._attr_unique_id = f"{device_id}_battery"
        self._attr_name = f"{self._device_name} Battery"
    
    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        return self.device_data.get("battery_level")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.device_data.get("battery_level") is not None
        )


class GoogleFindMyLastSeenSensor(GoogleFindMyBaseSensor):
    """Last seen sensor for Google Find My Device."""
    
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    
    def __init__(
        self,
        coordinator: GoogleFindMyDataUpdateCoordinator,
        device_id: str,
        device_data: dict,
    ) -> None:
        """Initialize the last seen sensor."""
        super().__init__(coordinator, device_id, device_data)
        self._attr_unique_id = f"{device_id}_last_seen"
        self._attr_name = f"{self._device_name} Last Seen"
    
    @property
    def native_value(self) -> datetime | None:
        """Return the last seen timestamp."""
        last_seen = self.device_data.get("last_seen")
        if last_seen:
            if isinstance(last_seen, str):
                try:
                    dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    # Ensure timezone is set
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except (ValueError, AttributeError):
                    return None
            elif isinstance(last_seen, datetime):
                # Ensure timezone is set
                if last_seen.tzinfo is None:
                    return last_seen.replace(tzinfo=timezone.utc)
                return last_seen
        return None
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = super().extra_state_attributes
        
        # Add location timestamp if available
        location = self.device_data.get("location")
        if location and location.get("timestamp"):
            attrs[ATTR_LOCATION_TIMESTAMP] = location["timestamp"]
        
        return attrs

