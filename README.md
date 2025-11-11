# Google Find My Device - Home Assistant Integration Project

A complete two-part solution for integrating Google Find My Device functionality with Home Assistant.

## 🎯 Project Overview

This project provides:

1. **REST API Service**: A Python FastAPI service that exposes Google Find My Device functionality through a REST API
2. **Home Assistant Integration**: A custom component that connects to the REST API to provide device tracking and monitoring in Home Assistant

## ✨ Features

### REST API Service

- List all Google Find My devices
- Get detailed device information (location, battery, status)
- Automatic caching to reduce API calls
- Health check endpoint for monitoring
- Interactive API documentation (Swagger/ReDoc)
- Docker support for easy deployment

### Home Assistant Integration

- Device tracker entities showing device locations on the map
- Battery level sensors for monitoring device power
- Last seen timestamp sensors
- Automatic updates with configurable polling
- Rich device attributes (type, model, accuracy, status)
- Easy UI-based configuration

## 📋 Prerequisites

- **Google Account** with Find My Device enabled
- **Docker & Docker Compose** (for containerized deployment)
- **Home Assistant** (version 2023.1 or newer)
- **Chromium/Chrome** (for initial authentication - Chromium is included in Docker image)

## 🚀 Quick Start

### Step 1: Set Up the REST API Service

1. **Navigate to the REST API directory**:

   ```bash
   cd rest-api
   ```

2. **Create auth data directory**:

   ```bash
   mkdir -p auth_data
   ```

3. **Authenticate with Google** (Choose one method):

   > 📖 **Detailed Authentication Guide**: See [AUTHENTICATION.md](AUTHENTICATION.md) for comprehensive step-by-step instructions and troubleshooting.

   #### Method 1: Authenticate Outside Docker (Recommended) ⭐

   This method is easier and more reliable as it allows you to use your Mac's Chrome browser for authentication:

   ```bash
   # Navigate to the project root
   cd ..

   # Install Python dependencies (one-time setup)
   pip3 install -r GoogleFindMyTools/requirements.txt

   # Run authentication script (will open Chrome on your Mac)
   cd GoogleFindMyTools
   python3 main.py
   ```

   Follow the on-screen instructions:

   - Press Enter when prompted
   - Chrome will open automatically
   - Log in to your Google account
   - Grant permissions to the application
   - Complete any 2FA if enabled
   - Wait for the script to complete

   After successful authentication, copy the secrets file to the Docker volume:

   ```bash
   # Copy authentication file to Docker volume
   cp Auth/secrets.json ../rest-api/auth_data/

   # Return to rest-api directory
   cd ../rest-api
   ```

   #### Method 2: Authenticate Inside Docker (Advanced)

   This method runs authentication in a headless browser inside Docker:

   ```bash
   docker compose build
   docker compose run --rm -w /app/GoogleFindMyTools google-findmy-api python main.py
   ```

   **Note**: This method uses headless Chrome inside Docker, which may have limitations with certain authentication flows (e.g., CAPTCHA, advanced 2FA). If you encounter issues, use Method 1 instead.

4. **Start the service**:

   ```bash
   docker-compose up -d
   ```

5. **Verify the service is running**:

   ```bash
   curl http://localhost:8000/health
   ```

   You should see: `{"status":"healthy","message":"Service is running normally"}`

6. **Test the API**:

   ```bash
   # List all devices
   curl http://localhost:8000/api/v1/devices

   # View API documentation
   open http://localhost:8000/docs
   ```

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
├── rest-api/                          # REST API Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   ├── models.py                  # Data models
│   │   └── services/
│   │       └── device_service.py      # Device service logic
│   ├── auth_data/                     # Docker volume (exposed folder)
│   │   └── secrets.json               # Authentication file (copy here)
│   ├── Dockerfile                     # Clones GoogleFindMyTools during build
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── README.md                      # Detailed API documentation
│
├── GoogleFindMyTools/                 # Git repo (for Method 1 auth)
│   ├── main.py                        # Authentication script
│   ├── Auth/
│   │   └── secrets.json               # Generated here, copy to rest-api/auth_data/
│   └── requirements.txt
│
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
├── AUTHENTICATION.md                  # Comprehensive authentication guide
├── QUICKSTART.md                      # Quick start guide
└── README.md                          # This file
```

### Understanding GoogleFindMyTools

**GoogleFindMyTools** is the underlying Python library from https://github.com/leonboe1/GoogleFindMyTools that provides Google Find My Device functionality.

- **Inside Docker**: Automatically cloned during `docker compose build`
- **On Your Mac** (for Method 1 auth): Clone manually to run authentication with your system's Chrome browser
- **Purpose**: Provides the authentication script and API access to Google Find My Device

## 🔧 Configuration

### REST API Service

The REST API service can be configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  - LOG_LEVEL=INFO # Logging level
  - CACHE_TTL=60 # Cache time-to-live in seconds
```

### Home Assistant Integration

Configuration is done through the UI:

- **API URL**: The URL where your REST API service is running
- **Update Interval**: Default is 60 seconds (can be changed in code)

## 📊 API Endpoints

### REST API Service

| Endpoint                      | Method | Description                    |
| ----------------------------- | ------ | ------------------------------ |
| `/`                           | GET    | API information                |
| `/health`                     | GET    | Health check                   |
| `/api/v1/devices`             | GET    | List all devices               |
| `/api/v1/devices/{device_id}` | GET    | Get device details             |
| `/docs`                       | GET    | Interactive API docs (Swagger) |
| `/redoc`                      | GET    | Alternative API docs (ReDoc)   |

## 🏠 Home Assistant Entities

For each device, the following entities are created:

| Entity Type    | Entity ID                        | Description         |
| -------------- | -------------------------------- | ------------------- |
| Device Tracker | `device_tracker.{device_name}`   | Device location     |
| Sensor         | `sensor.{device_name}_battery`   | Battery level (%)   |
| Sensor         | `sensor.{device_name}_last_seen` | Last seen timestamp |

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

### Script: Get Device Location

```python
import requests

response = requests.get('http://localhost:8000/api/v1/devices')
devices = response.json()

for device in devices:
    device_id = device['device_id']
    detail = requests.get(f'http://localhost:8000/api/v1/devices/{device_id}').json()

    if detail.get('location'):
        print(f"{detail['name']}: {detail['location']['latitude']}, {detail['location']['longitude']}")
```

## 🐛 Troubleshooting

### Authentication Issues

**Authentication fails in Docker (headless mode)**:

- **Solution**: Use Method 1 (authenticate outside Docker) instead
- The headless browser in Docker may not support all authentication flows
- CAPTCHA and advanced 2FA may not work in headless mode

**"ModuleNotFoundError" when running authentication outside Docker**:

```bash
# Install required dependencies
pip3 install -r GoogleFindMyTools/requirements.txt

# Or install specific packages
pip3 install selenium undetected-chromedriver gpsoauth requests beautifulsoup4 pyscrypt cryptography
```

**Chrome/Chromium not found when running outside Docker**:

- **macOS**: Install Chrome from https://www.google.com/chrome/
- **Linux**: Install Chromium: `sudo apt-get install chromium-browser`
- Ensure Chrome/Chromium is in your PATH

**Authentication completes but secrets.json not created**:

- Check the `GoogleFindMyTools/Auth/` directory for `secrets.json`
- Ensure you have write permissions in the directory
- Look for error messages in the terminal output

**"Your encryption data is locked on your device"**:

1. Login to an Android device with your Google Account
2. Go to Settings > Google > All Services > Find My Device
3. Enable "Find your offline devices"

### REST API Service

**Service won't start**:

- Check logs: `docker-compose logs -f google-findmy-api`
- Verify authentication: Ensure `auth_data/secrets.json` exists
- Check port availability: `netstat -an | grep 8000`
- Rebuild the image: `docker compose build --no-cache`

### Home Assistant Integration

**Integration not found**:

- Verify files are in `/config/custom_components/google_findmy/`
- Restart Home Assistant
- Clear browser cache

**Cannot connect to API**:

- Test API: `curl http://YOUR_API_URL/health`
- Check firewall settings
- Verify network connectivity

**Entities unavailable**:

- Check integration logs in Home Assistant
- Verify API service is running
- Reload the integration

## 📚 Documentation

- [Authentication Guide](AUTHENTICATION.md) - **Comprehensive authentication setup and troubleshooting**
- [REST API Documentation](rest-api/README.md) - Detailed API service documentation
- [Home Assistant Integration Documentation](homeassistant-integration/README.md) - Detailed integration documentation
- [GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools) - Underlying library documentation

## 🔒 Security Considerations

- This solution is designed for **local network use only**
- No authentication is implemented in the REST API (add for production)
- The `secrets.json` file contains sensitive data - keep it secure
- Consider using HTTPS with a reverse proxy for remote access
- Use strong passwords and 2FA on your Google Account

## 🛠️ Development

### Running Locally (Without Docker)

**REST API**:

```bash
cd rest-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Home Assistant**:

- Copy integration to `/config/custom_components/`
- Restart Home Assistant in development mode

### Testing

```bash
# Test REST API
curl http://localhost:8000/api/v1/devices

# Test Home Assistant integration
# Use Home Assistant's built-in integration testing tools
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project uses the GoogleFindMyTools library which is licensed under GPL-3.0.

## 🙏 Credits

- [GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools) by leonboe1 - The underlying library that makes this possible
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation platform

## 📞 Support

For issues and questions:

- Check the documentation in each component's README
- Review the troubleshooting sections
- Check logs for error messages
- Open an issue on GitHub

## 🗺️ Roadmap

Future enhancements:

- [ ] Add authentication to REST API
- [ ] Support for device actions (ring, lock, etc.)
- [ ] Historical location tracking
- [ ] Geofencing capabilities
- [ ] MQTT support
- [ ] HACS integration
- [ ] Multi-account support
- [ ] Webhook support for real-time updates

---

**Note**: This is an unofficial project and is not affiliated with Google. Use at your own risk.
