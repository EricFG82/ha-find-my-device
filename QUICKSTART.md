# Quick Start Guide

Get up and running with Google Find My Device integration in Home Assistant in under 10 minutes!

## Prerequisites Checklist

- [ ] Google Account with Find My Device enabled
- [ ] Docker and Docker Compose installed
- [ ] Home Assistant running (version 2023.1+)
- [ ] Chromium/Chrome browser (Chromium is included in Docker image)

## Step-by-Step Setup

### 1. Clone or Download This Repository

```bash
git clone <repository-url>
cd GoogleFindMyTools
```

Or download and extract the ZIP file.

### 2. Set Up the REST API Service (5 minutes)

> 📖 **Need help with authentication?** See the detailed [Authentication Guide](AUTHENTICATION.md)

```bash
# Navigate to the REST API directory
cd rest-api

# Create directory for authentication data
mkdir -p auth_data
```

**Authenticate with Google (Method 1 - Recommended):**

> **Note**: GoogleFindMyTools is the Python library that provides authentication. We'll clone it **on your Mac** to run authentication with your system's Chrome browser.

```bash
# Go back to project root
cd ..

# Clone GoogleFindMyTools if not already cloned
if [ ! -d "GoogleFindMyTools" ]; then
    git clone https://github.com/leonboe1/GoogleFindMyTools.git
fi

# Install Python dependencies (one-time)
pip3 install -r GoogleFindMyTools/requirements.txt

# Run authentication (Chrome will open)
cd GoogleFindMyTools
python3 main.py
```

**During authentication:**

1. Press Enter when prompted
2. Chrome browser will open automatically
3. Log in to your Google Account
4. Complete any 2FA if required
5. Wait for success message

**Copy authentication file:**

```bash
# Copy secrets to Docker volume
cp Auth/secrets.json ../rest-api/auth_data/

# Return to rest-api directory
cd ../rest-api
```

**Build and start the service:**

```bash
# Build the Docker image
docker compose build

# Start the API service
docker compose up -d

# Verify it's running
curl http://localhost:8000/health
```

Expected output:

```json
{ "status": "healthy", "message": "Service is running normally" }
```

### 3. Test the API (1 minute)

```bash
# List your devices
curl http://localhost:8000/api/v1/devices

# Open the interactive API documentation
open http://localhost:8000/docs
# Or visit: http://localhost:8000/docs in your browser
```

### 4. Install Home Assistant Integration (3 minutes)

**Option A: Using Home Assistant File Editor Add-on**

1. Install the File Editor add-on if you haven't already
2. Navigate to `/config/custom_components/`
3. Create a new folder called `google_findmy`
4. Copy all files from `homeassistant-integration/custom_components/google_findmy/` to this folder

**Option B: Using SSH or Terminal**

```bash
# SSH into your Home Assistant instance
ssh root@homeassistant.local

# Navigate to config directory
cd /config

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Copy the integration (adjust path as needed)
cp -r /path/to/homeassistant-integration/custom_components/google_findmy custom_components/
```

**Option C: Using Samba/SMB Share**

1. Connect to your Home Assistant via network share
2. Navigate to the `config` folder
3. Create `custom_components` folder if it doesn't exist
4. Copy the `google_findmy` folder into `custom_components`

### 5. Restart Home Assistant (1 minute)

- Go to **Settings** > **System** > **Restart**
- Wait for Home Assistant to restart (usually 1-2 minutes)

### 6. Add the Integration (2 minutes)

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

### 7. Verify Everything Works

1. Go to **Settings** > **Devices & Services** > **Google Find My Device**
2. You should see your devices listed
3. Click on a device to see its entities:
   - `device_tracker.{device_name}` - Location tracker
   - `sensor.{device_name}_battery` - Battery level
   - `sensor.{device_name}_last_seen` - Last seen timestamp

### 8. Add Devices to Your Dashboard

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

- [ ] REST API service is running (`docker-compose ps` shows "Up")
- [ ] Health check returns healthy (`curl http://localhost:8000/health`)
- [ ] API returns devices (`curl http://localhost:8000/api/v1/devices`)
- [ ] Home Assistant shows the integration in Devices & Services
- [ ] Device entities are created and available
- [ ] Device location shows on the map
- [ ] Battery and last seen sensors show data

## Common Issues and Quick Fixes

> 📖 **For authentication issues**, see the comprehensive [Authentication Guide](AUTHENTICATION.md)

### Issue: Authentication fails or Chrome doesn't open

**Fix:**

1. Make sure Chrome is installed
2. Check that Python dependencies are installed: `pip3 install -r GoogleFindMyTools/requirements.txt`
3. See [Authentication Guide](AUTHENTICATION.md) for detailed troubleshooting

### Issue: "Cannot connect to API"

**Fix:**

```bash
# Check if API is running
docker-compose ps

# Check API logs
docker-compose logs -f google-findmy-api

# Restart API if needed
docker-compose restart
```

### Issue: "Integration not found in Home Assistant"

**Fix:**

1. Verify files are in `/config/custom_components/google_findmy/`
2. Check file permissions
3. Restart Home Assistant
4. Clear browser cache (Ctrl+F5)

### Issue: "Your encryption data is locked on your device"

**Fix:**

1. Get an Android device
2. Log in with your Google Account
3. Go to Settings > Google > All Services > Find My Device
4. Enable "Find your offline devices"
5. If option not available, install Find My Device app from Play Store

### Issue: Entities show as "Unavailable"

**Fix:**

```bash
# Verify API is accessible from Home Assistant
# From Home Assistant terminal:
curl http://YOUR_API_URL/health

# Check integration logs in Home Assistant
# Settings > System > Logs > Filter for "google_findmy"

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
   - REST API: `docker-compose logs -f google-findmy-api`
   - Home Assistant: Settings > System > Logs
2. Review the detailed documentation:
   - [Authentication Guide](AUTHENTICATION.md) - **For authentication issues**
   - [REST API README](rest-api/README.md)
   - [Home Assistant Integration README](homeassistant-integration/README.md)
3. Verify all prerequisites are met
4. Check the troubleshooting sections in the documentation

## Success! 🎉

You now have Google Find My Device integrated with Home Assistant! Your devices should appear on the map and you can track their location, battery level, and status.

Enjoy your new device tracking capabilities!
