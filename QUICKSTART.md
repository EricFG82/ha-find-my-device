# Quick Start Guide

Get up and running with Google Find My Device integration in Home Assistant in under 10 minutes!

## Prerequisites Checklist

- [ ] Google Account with Find My Device enabled
- [ ] The [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) REST API service running somewhere reachable from Home Assistant
- [ ] Home Assistant running (version 2023.1+)

## Step-by-Step Setup

### 1. Clone or Download This Repository

```bash
git clone <repository-url>
cd ha_google_find_my_device
```

Or download and extract the ZIP file.

### 2. Get the REST API Running First (5 minutes)

This integration is just the Home Assistant side - it needs the REST API
service running somewhere it can reach over the network. Follow
[google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)'s own
Quick Start (Docker, authenticate via the in-browser VNC flow - no local
Chrome needed) to get it up, then come back here. Once it's running:

```bash
curl http://YOUR_API_HOST:8000/health
```

Expected output:

```json
{ "status": "healthy", "message": "Service is running normally" }
```

### 3. Install Home Assistant Integration (3 minutes)

**Option A: Using Home Assistant File Editor Add-on**

1. Install the File Editor add-on if you haven't already
2. Navigate to `/config/custom_components/`
3. Create a new folder called `google_find_my_device`
4. Copy all files from this repo's `custom_components/google_find_my_device/` to this folder

**Option B: Using SSH or Terminal**

```bash
# SSH into your Home Assistant instance
ssh root@homeassistant.local

# Navigate to config directory
cd /config

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Copy the integration (adjust path as needed)
cp -r /path/to/custom_components/google_find_my_device custom_components/
```

**Option C: Using Samba/SMB Share**

1. Connect to your Home Assistant via network share
2. Navigate to the `config` folder
3. Create `custom_components` folder if it doesn't exist
4. Copy the `google_find_my_device` folder into `custom_components`

### 4. Restart Home Assistant (1 minute)

- Go to **Settings** > **System** > **Restart**
- Wait for Home Assistant to restart (usually 1-2 minutes)

### 5. Add the Integration (2 minutes)

1. Go to **Settings** > **Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"Google Find My Device"**
4. Click on it
5. Enter the configuration:
   - **Name**: `Google Find My Device` (or any name you prefer)
   - **API URL**:
     - If Home Assistant and API are on the same machine: `http://localhost:8000`
     - If on different machines: `http://YOUR_API_SERVER_IP:8000`
     - If using Docker on same host: `http://host.docker.internal:8000` (Mac/Windows) or `http://172.17.0.1:8000` (Linux)
6. Click **Submit**

### 6. Verify Everything Works

1. Go to **Settings** > **Devices & Services** > **Google Find My Device**
2. You should see your devices listed
3. Click on a device to see its entities:
   - `device_tracker.{device_name}` - Location tracker (appears once the device has a location)
   - `sensor.{device_name}_battery` - Battery level (**currently not created for any
     device** - Google's Find My Device network doesn't expose battery percentage
     for these trackers today)
   - `sensor.{device_name}_last_seen` - Last seen timestamp

### 7. Add Devices to Your Dashboard

**Add to Map Card:**

1. Go to your dashboard
2. Click **Edit Dashboard** (top right)
3. Click **+ ADD CARD**
4. Search for **"Map"**
5. In the entities section, add your device trackers
6. Click **Save**

**Add Status Card:**

1. Click **+ ADD CARD**
2. Search for **"Entities"**
3. Add your device entities:
   - Device tracker
   - Battery sensor
   - Last seen sensor
4. Click **Save**

## Verification Checklist

- [ ] REST API service is running (`curl http://YOUR_API_HOST:8000/health`)
- [ ] API returns devices (`curl http://YOUR_API_HOST:8000/api/v1/devices`)
- [ ] Home Assistant shows the integration in Devices & Services
- [ ] Device entities are created and available
- [ ] Device location shows on the map
- [ ] Last seen sensor shows data (battery sensor won't - see note below)

## Common Issues and Quick Fixes

> 📖 **For REST API / authentication issues**, see
> [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)'s
> [AUTHENTICATION.md](https://github.com/EricFG82/google-find-my-device-rest-api/blob/main/AUTHENTICATION.md)

### Issue: "Cannot connect to API"

**Fix:**

```bash
# Check if the API is reachable from Home Assistant
curl http://YOUR_API_HOST:8000/health
```

- Verify the API URL is correct (include `http://` or `https://`)
- Check firewall/network settings between Home Assistant and the API host
- Check the API service's own logs (see its repo's README)

### Issue: "Integration not found in Home Assistant"

**Fix:**

1. Verify files are in `/config/custom_components/google_find_my_device/`
2. Check file permissions
3. Restart Home Assistant
4. Clear browser cache (Ctrl+F5)

### Issue: Entities show as "Unavailable"

**Fix:**

```bash
# Verify API is accessible from Home Assistant
# From Home Assistant terminal:
curl http://YOUR_API_URL/health

# Check integration logs in Home Assistant
# Settings > System > Logs > Filter for "google_find_my_device"

# Reload the integration
# Settings > Devices & Services > Google Find My Device > ⋮ > Reload
```

## Next Steps

Now that everything is set up, you can:

1. **Create Automations**: Set up alerts for low battery, device arrivals, etc.
2. **Customize Dashboard**: Add more cards to visualize your devices
3. **Set Up Zones**: Define home, work, etc. for presence detection
4. **Create Scripts**: Automate actions based on device locations

See the main [README.md](README.md) for examples and advanced configuration.

## Getting Help

If you encounter issues:

1. Check the logs:
   - REST API: see [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)
   - Home Assistant: Settings > System > Logs
2. Review the detailed documentation:
   - [google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) - **For REST API / authentication issues**
   - [README.md](README.md#-troubleshooting)
3. Verify all prerequisites are met
4. Check the troubleshooting sections in the documentation

## Success! 🎉

You now have Google Find My Device integrated with Home Assistant! Your devices should appear on the map and you can track their location, battery level, and status.

Enjoy your new device tracking capabilities!
