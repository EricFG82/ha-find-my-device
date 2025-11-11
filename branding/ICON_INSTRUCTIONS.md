# Instructions for Adding Icon to Integration

## Created Files

I've created two SVG files for the integration:

1. **`icon.svg`** - Animated icon with radar waves (more dynamic)
2. **`logo.svg`** - Simple static logo (recommended for integration list)

## Option 1: Use SVG Directly (Recommended)

Home Assistant supports SVG directly. You just need to:

1. **Copy the SVG files** to the integration directory:
   ```bash
   cp homeassistant-integration/custom_components/google_findmy/*.svg \
      /config/custom_components/google_findmy/
   ```

2. **Restart Home Assistant**

3. The icon should appear automatically in the integrations list

## Option 2: Convert SVG to PNG

If you prefer to use PNG (256x256 pixels), you can convert the SVG:

### Method A: Using ImageMagick (Linux/Mac)

```bash
# Install ImageMagick if you don't have it
# Mac: brew install imagemagick
# Ubuntu/Debian: sudo apt-get install imagemagick

# Convert logo.svg to PNG
convert -background none -resize 256x256 \
  homeassistant-integration/custom_components/google_findmy/logo.svg \
  homeassistant-integration/custom_components/google_findmy/icon.png

# Copy to Home Assistant
cp homeassistant-integration/custom_components/google_findmy/icon.png \
   /config/custom_components/google_findmy/
```

### Method B: Using Inkscape (All platforms)

```bash
# Install Inkscape: https://inkscape.org/

# Convert logo.svg to PNG
inkscape logo.svg --export-type=png --export-filename=icon.png \
  --export-width=256 --export-height=256
```

### Method C: Using an Online Service

1. Go to https://cloudconvert.com/svg-to-png
2. Upload the `logo.svg` file
3. Set the size to 256x256 pixels
4. Download the resulting PNG
5. Rename it to `icon.png`
6. Copy it to `/config/custom_components/google_findmy/`

### Method D: Using Python (rsvg-convert)

```bash
# Install librsvg
# Mac: brew install librsvg
# Ubuntu/Debian: sudo apt-get install librsvg2-bin

# Convert
rsvg-convert -w 256 -h 256 logo.svg -o icon.png
```

## Final File Structure

Your directory should look like this:

```
/config/custom_components/google_findmy/
├── __init__.py
├── config_flow.py
├── const.py
├── device_tracker.py
├── sensor.py
├── manifest.json
├── strings.json
├── translations/
│   └── en.json
├── icon.svg          ← Animated icon (optional)
├── logo.svg          ← Static logo (recommended)
└── icon.png          ← PNG if you prefer (optional)
```

## Icon Priority in Home Assistant

Home Assistant looks for icons in this order:

1. `icon.png` (256x256 pixels)
2. `icon@2x.png` (512x512 pixels, for retina displays)
3. `logo.png` (256x256 pixels)
4. `icon.svg`
5. `logo.svg`

**Recommendation**: Use `logo.svg` (already created) or convert it to `icon.png`.

## Design Description

### Main Logo
- **Blue location pin** with gradient (Google colors: #4285F4 → #1967D2)
- **White circle** in the center with a blue dot (representing simplified Google logo)
- **Subtle signal waves** around (indicating "Find My" / tracking)
- **Device icons** at the bottom (phone, tablet, tracker)

### Colors Used
- **Google Blue**: #4285F4 (primary)
- **Dark Blue**: #1967D2 (shadows)
- **Google Green**: #34A853 (signal waves)
- **Gray**: #5F6368 (devices)
- **Background**: #F1F3F4 (light gray)

### Features
- ✅ Clean and professional design
- ✅ Google brand colors
- ✅ Clearly represents functionality (location + devices)
- ✅ Scalable (vector SVG)
- ✅ Compatible with Home Assistant light and dark themes

## Verification

After copying the icon:

1. **Restart Home Assistant**
2. Go to **Settings** > **Devices & Services**
3. Look for **Google Find My Device** in the list
4. You should see the new icon next to the integration name

## Troubleshooting

### Icon doesn't appear

1. **Verify the file exists**:
   ```bash
   ls -la /config/custom_components/google_findmy/icon.*
   # or
   ls -la /config/custom_components/google_findmy/logo.*
   ```

2. **Check permissions**:
   ```bash
   chmod 644 /config/custom_components/google_findmy/icon.*
   ```

3. **Clear browser cache**:
   - Ctrl+Shift+R (Windows/Linux)
   - Cmd+Shift+R (Mac)

4. **Restart Home Assistant completely**:
   - Settings > System > Restart

5. **Check the logs**:
   ```bash
   # In Home Assistant
   Settings > System > Logs
   # Look for errors related to the integration
   ```

### Icon looks pixelated

- Make sure to use the correct size: 256x256 pixels
- If using PNG, consider also creating `icon@2x.png` (512x512) for retina displays

### I want to customize the icon

You can edit the SVG files with any vector editor:
- **Inkscape** (free): https://inkscape.org/
- **Adobe Illustrator**
- **Figma** (online): https://figma.com/
- **Text editor** (SVGs are XML)

## Alternative: Use a Material Design Icon

If you prefer to use a simple Material Design Icons icon, you can specify it in the code:

```python
# In __init__.py or config_flow.py
DOMAIN = "google_findmy"
ICON = "mdi:google-maps"  # or "mdi:map-marker-radius" or "mdi:crosshairs-gps"
```

But this only affects entities, not the integration icon in the list.

## Additional Resources

- **Material Design Icons**: https://materialdesignicons.com/
- **Google Brand Guidelines**: https://about.google/brand-resource-center/
- **Home Assistant Integration Icons**: https://www.home-assistant.io/docs/configuration/customizing-devices/#icon

## Expected Result

After following these instructions, you'll see:

```
Settings > Devices & Services

┌─────────────────────────────────────────┐
│  🔍 Google Find My Device               │  ← Your new icon here
│  1 device                                │
│  Configure                               │
└─────────────────────────────────────────┘
```

The icon will show a blue location pin with Google's style, making the integration easily recognizable in the list.

