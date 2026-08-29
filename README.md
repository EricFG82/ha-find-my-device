# Google Find My Device - Home Assistant Integration

A custom Home Assistant integration for Google Find My Device tracking.

> This repo holds the **Home Assistant integration**. It talks over HTTP to a
> separate REST API service - **[google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)**
> (which wraps the GoogleFindMyTools library and handles Google authentication)
> - you'll need that running first. The two used to live in one repo; they were
> split so each can be versioned/released independently, and so this
> integration can eventually be submitted to HACS.

## Table of Contents

- [🎯 Project Overview](#-project-overview)
- [✨ Features](#-features)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🏠 Home Assistant Entities](#-home-assistant-entities)
- [💡 Usage Examples](#-usage-examples)
- [🐛 Troubleshooting](#-troubleshooting)
- [🗑️ Uninstallation](#️-uninstallation)
- [📚 Documentation](#-documentation)
- [🔒 Security Considerations](#-security-considerations)
- [⚠️ Disclaimer](#️-disclaimer)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Credits](#-credits)

## 🎯 Project Overview

This is a custom Home Assistant component that connects to the
[google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) REST API to
provide Google Find My Device tracking and monitoring in Home Assistant.

## ✨ Features

- Device tracker entities showing device locations on the map
- Battery level sensors for monitoring device power *(currently inactive -
  see note under [Home Assistant Entities](#-home-assistant-entities);
  Google's network doesn't expose battery data for these trackers today)*
- Last seen timestamp sensors
- Automatic updates with configurable polling
- Rich device attributes (type, model, accuracy, status)
- Easy UI-based configuration

## 📋 Prerequisites

- The [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) REST
  API service running and reachable from Home Assistant (see its own Quick
  Start - Docker, in-browser authentication, no local Chrome needed)
- **Home Assistant** (version 2023.1 or newer)

## 🚀 Quick Start

### Step 1: Get the REST API Running

This integration needs [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)
running somewhere reachable from Home Assistant. Follow its own Quick Start,
then come back here once `curl http://YOUR_API_HOST:8000/health` returns
`{"status":"healthy",...}`.

### Step 2: Install the Home Assistant Integration

**Not yet available via HACS** - install manually for now:

1. **Copy the integration to Home Assistant**:

   ```bash
   # SSH into your Home Assistant instance or use the File Editor add-on
   cd /config
   mkdir -p custom_components
   cp -r /path/to/custom_components/google_find_my_device custom_components/
   ```

2. **Restart Home Assistant**:

   - Go to Settings > System > Restart (or `ha core restart` over SSH)

3. **Add the integration**:

   - Go to Settings > Devices & Services
   - Click "+ ADD INTEGRATION"
   - Search for "Google Find My Device"
   - Enter your API URL (e.g., `http://192.168.1.100:8000`)
   - Click Submit

4. **View your devices**:
   - Go to Settings > Devices & Services > Google Find My Device
   - Click on the integration to see all discovered devices
   - Add device trackers to your map card

## 📁 Project Structure

```
.
├── custom_components/
│   └── google_find_my_device/
│       ├── __init__.py            # Integration setup
│       ├── config_flow.py         # UI configuration
│       ├── const.py               # Constants
│       ├── device_tracker.py      # Device tracker platform
│       ├── sensor.py              # Sensor platform
│       ├── manifest.json          # Integration manifest
│       ├── strings.json           # UI strings
│       └── translations/
│           └── en.json
├── branding/                      # Icon source assets (for a future
│                                   # home-assistant/brands PR - see its README)
├── docs/
│   └── example_configuration.yaml # Extra automation/card examples
├── ARCHITECTURE.md                # Technical architecture
├── QUICKSTART.md                  # Quick start guide
└── README.md                      # This file
```

## 🔧 Configuration

Configuration is done through the UI:

- **API URL**: The URL where your [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) service is running
- **Update Interval**: Default is 60 seconds; to change it, edit
  `custom_components/google_find_my_device/const.py`:

  ```python
  DEFAULT_SCAN_INTERVAL = 120  # Change to desired seconds
  ```

  then restart Home Assistant.

### Home Assistant and the API in separate Docker containers

**Option 1: Same Docker network**

```yaml
# docker-compose.yml
services:
  homeassistant:
    # ... your HA config
    networks:
      - findmy-network

  google-find-my-device-rest-api:
    # ... API config
    networks:
      - findmy-network

networks:
  findmy-network:
    driver: bridge
```

Use API URL: `http://google-find-my-device-rest-api:8000`

**Option 2: Host network**

```yaml
services:
  homeassistant:
    network_mode: host
```

Use API URL: `http://localhost:8000`

**Remote API service** (different machine): use its IP address
(`http://192.168.1.100:8000`), ensure port 8000 is reachable, and consider
HTTPS behind a reverse proxy for anything beyond your local network.

## 🏠 Home Assistant Entities

Entities are created **dynamically, per device, as data becomes available** -
not all at once when the integration is set up. A device tracker only
appears once that device has a location; a battery sensor only appears once
`battery_level` data exists for it. If a tracker doesn't have a location yet
on the very first refresh (e.g. right after the REST API restarts), it'll
still get its tracker as soon as the location shows up in a later update -
it isn't stuck waiting for a reload.

> **Battery level is currently not available for any device.** Google's Find My
> Device network (as exposed by the underlying `GoogleFindMyTools` library) doesn't
> expose a battery percentage for `SPOT_DEVICE` trackers (Fast Pair tags, etc.). The
> `battery_level` field/sensor exist for when that data becomes available, but expect
> it to stay `null` today.

Devices that stop being reported by the API (e.g. a tracker re-paired after a
battery change gets issued a new ID by Google) are removed from Home
Assistant's device registry automatically on integration setup/reload - you
won't end up with duplicate/unavailable "ghost" devices after re-pairing
something.

| Entity Type    | Entity ID                        | Created                                   |
| -------------- | --------------------------------- | ------------------------------------------ |
| Device Tracker | `device_tracker.{device_name}`    | Once the device has a location             |
| Sensor         | `sensor.{device_name}_battery`    | Once `battery_level` is available (never today, see note above) |
| Sensor         | `sensor.{device_name}_last_seen`  | Immediately for every known device         |

The device tracker's attributes include Device ID, Device Type, Model,
Battery Level, Location Accuracy, Location Timestamp, and Status.

## 💡 Usage Examples

### Automation: Low Battery Alert

```yaml
automation:
  - alias: "Alert on Low Battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.my_tracker_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Tracker battery is low: {{ states('sensor.my_tracker_battery') }}%"
```

### Automation: Device Arrived Home

```yaml
automation:
  - alias: "Device Arrived Home"
    trigger:
      - platform: zone
        entity_id: device_tracker.my_tracker
        zone: zone.home
        event: enter
    action:
      - service: notify.mobile_app
        data:
          title: "Device Home"
          message: "Your tracker has arrived home"
```

### Lovelace Card: Device Map

```yaml
type: map
entities:
  - device_tracker.my_tracker
  - device_tracker.my_phone
default_zoom: 15
```

### Lovelace Card: Device Status

```yaml
type: entities
title: Device Status
entities:
  - entity: device_tracker.my_tracker
    secondary_info: last-changed
  - entity: sensor.my_tracker_battery
  - entity: sensor.my_tracker_last_seen
```

More examples (glance cards, scripts, template/binary sensors) are in
[`docs/example_configuration.yaml`](docs/example_configuration.yaml).

### Querying the REST API Directly

For automations or scripts that want raw data instead of going through entity
state:

```python
import requests

response = requests.get('http://YOUR_API_HOST:8000/api/v1/devices')
devices = response.json()

for device in devices:
    device_id = device['device_id']
    detail = requests.get(f'http://YOUR_API_HOST:8000/api/v1/devices/{device_id}').json()

    if detail.get('location'):
        print(f"{detail['name']}: {detail['location']['latitude']}, {detail['location']['longitude']}")
```

See [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) for the
full endpoint reference.

## 🐛 Troubleshooting

### Integration Not Found

Can't find "Google Find My Device" when adding the integration:

1. Verify the files are in the correct location: `/config/custom_components/google_find_my_device/`
2. Restart Home Assistant
3. Clear browser cache (Ctrl+F5)

### Cannot Connect to API

"Failed to connect to the API" during setup:

1. Verify the REST API service is running: `curl http://YOUR_API_HOST:8000/health`
2. Check the API URL is correct (include `http://` or `https://`)
3. Ensure Home Assistant can reach the API service (firewall, network settings)
4. If using Docker, make sure both containers are on the same network or use host networking

### No Entities Created

Integration added successfully but no entities appear:

1. Check the integration logs: Settings > System > Logs
2. Verify the REST API service has devices: `curl http://YOUR_API_HOST:8000/api/v1/devices`
3. Reload the integration: Settings > Devices & Services > Google Find My Device > ⋮ > Reload

### Entities Unavailable

1. Check if the REST API service is running
2. Verify network connectivity between Home Assistant and the API
3. Check the integration logs for errors
4. Try reloading the integration

### Location Not Updating

1. Check if the device has recent location data in the API: `curl http://YOUR_API_HOST:8000/api/v1/devices/{device_id}`
2. Verify the device is online and reporting location
3. Check the update interval (default: 60 seconds)
4. Ensure the device has location permissions enabled

## 🗑️ Uninstallation

1. Go to **Settings** > **Devices & Services**
2. Find **Google Find My Device**
3. Click the **⋮** menu → **Delete**
4. Optionally, remove the integration files: `rm -rf /config/custom_components/google_find_my_device`
5. Restart Home Assistant

## 📚 Documentation

- [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) - REST API service (setup, authentication, endpoint reference)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools) - Underlying library used by the REST API

## 🔒 Security Considerations

- This integration has no authentication of its own - it just calls the REST
  API's URL, so securing that connection is the REST API's concern (see its
  own Security Considerations)
- Designed for **local network use only**
- Use strong passwords and 2FA on your Google Account (on the API side)

## ⚠️ Disclaimer

This project is provided **"as is", with no warranty of any kind** (see
[LICENSE](LICENSE) for the full disclaimer) - the author(s) are not
liable for any damages, data loss, account restrictions, or other issues
arising from its use.

It's an **unofficial, reverse-engineered integration**, not affiliated with,
endorsed by, or supported by Google. The underlying REST API accesses
Google's Find My Device network through undocumented APIs that Google could
change, block, or restrict at any time, and use may be subject to Google's
Terms of Service. Use at your own risk, with your own Google account.

## 🛠️ Development

**Home Assistant integration**:

- Copy integration to `/config/custom_components/`
- Restart Home Assistant in development mode

### Testing

```bash
# Test the REST API directly
curl http://YOUR_API_HOST:8000/api/v1/devices

# Test Home Assistant integration
# Use Home Assistant's built-in integration testing tools
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

By submitting a contribution, you agree it's licensed under the same terms as
the rest of the project (MIT - see below).

## 📄 License

**MIT** - see [LICENSE](LICENSE) for the full text.

This integration talks to the REST API over plain HTTP - it doesn't import or
link any of its code, so unlike [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)
(GPL-3.0, since it imports GoogleFindMyTools directly), this repo isn't bound
by GPL-3.0's "combined work" rules and can use a permissive license instead.

## 🙏 Credits

- [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) - The REST API service this integration talks to
- [GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools) by leonboe1 - The underlying library that makes this possible
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation platform
