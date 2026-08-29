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
- Battery level sensors for monitoring device power
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

1. **Copy the integration to Home Assistant**:

   ```bash
   # SSH into your Home Assistant instance or use the File Editor add-on
   cd /config
   mkdir -p custom_components
   cp -r /path/to/homeassistant-integration/custom_components/google_findmy custom_components/
   ```

2. **Restart Home Assistant**:

   - Go to Settings > System > Restart

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
├── homeassistant-integration/         # Home Assistant Integration
│   ├── custom_components/
│   │   └── google_findmy/
│   │       ├── __init__.py            # Integration setup
│   │       ├── config_flow.py         # UI configuration
│   │       ├── const.py               # Constants
│   │       ├── device_tracker.py      # Device tracker platform
│   │       ├── sensor.py              # Sensor platform
│   │       ├── manifest.json          # Integration manifest
│   │       ├── strings.json           # UI strings
│   │       └── translations/
│   │           └── en.json
│   └── README.md                      # Detailed integration documentation
│
├── ARCHITECTURE.md                    # Technical architecture
├── QUICKSTART.md                      # Quick start guide
└── README.md                          # This file
```

## 🔧 Configuration

Configuration is done through the UI:

- **API URL**: The URL where your [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) service is running
- **Update Interval**: Default is 60 seconds (can be changed in code)

## 🏠 Home Assistant Entities

For each device, the following entities are created:

| Entity Type    | Entity ID                        | Description         |
| -------------- | -------------------------------- | ------------------- |
| Device Tracker | `device_tracker.{device_name}`   | Device location     |
| Sensor         | `sensor.{device_name}_battery`   | Battery level (%) - see note below |
| Sensor         | `sensor.{device_name}_last_seen` | Last seen timestamp |

> **Battery level is currently not available for any device.** Google's Find My
> Device network (as exposed by the underlying `GoogleFindMyTools` library) doesn't
> expose a battery percentage for `SPOT_DEVICE` trackers (Fast Pair tags, etc.). The
> `battery_level` field/sensor exist for when that data becomes available, but expect
> it to stay `null` today. Entities are created dynamically as data becomes
> available, not all at once at integration setup.

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

### Lovelace Card: Device Map

```yaml
type: map
entities:
  - device_tracker.my_tracker
  - device_tracker.my_phone
default_zoom: 15
```

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

## 📚 Documentation

- [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) - REST API service (setup, authentication, endpoint reference)
- [Home Assistant Integration Documentation](homeassistant-integration/README.md) - Detailed integration documentation
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
