"""Constants for the Google Find My Device integration."""

from homeassistant.const import Platform

# Domain
DOMAIN = "google_findmy"

# Platforms
PLATFORMS = [Platform.SENSOR, Platform.DEVICE_TRACKER]

# Configuration
CONF_API_URL = "api_url"
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Attributes
ATTR_DEVICE_ID = "device_id"
ATTR_DEVICE_TYPE = "device_type"
ATTR_MODEL = "model"
ATTR_LAST_SEEN = "last_seen"
ATTR_BATTERY_LEVEL = "battery_level"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_ACCURACY = "accuracy"
ATTR_LOCATION_TIMESTAMP = "location_timestamp"
ATTR_STATUS = "status"
ATTR_IMAGE_URL = "image_url"
ATTR_IDENTIFIER_TYPE = "identifier_type"
ATTR_MODEL_ID = "model_id"
ATTR_OWNER_KEY_VERSION = "owner_key_version"
ATTR_GOOGLE_MAPS_LINK = "google_maps_link"

