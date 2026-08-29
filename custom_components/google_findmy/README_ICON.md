# Integration Icon

This directory contains icon source files for the Google Find My Device integration.

> **⚠️ These files are NOT automatically picked up by Home Assistant.** The icon
> shown on the Devices & Services page comes exclusively from the public
> [home-assistant/brands](https://github.com/home-assistant/brands) repository,
> keyed by domain - not from local files in a custom integration's folder. See
> [`../../ICON_INSTRUCTIONS.md`](../../ICON_INSTRUCTIONS.md) for the actual process
> (a PR to that repo). Until that PR is merged, expect "icon not available" in the
> HA UI regardless of what's in this folder - it's cosmetic only.

## Available Files

- **`logo.svg`** - Static vector logo (recommended)
- **`icon.svg`** - Animated icon with radar waves
- **`icon.png`** - PNG icon 256x256 (generated from SVG)
- **`icon@2x.png`** - PNG icon 512x512 for retina displays (generated from SVG)

## Usage

These are source assets for a future `home-assistant/brands` submission (see the
warning above) - not files Home Assistant itself reads.

## Generate PNG from SVG

If you need to regenerate the PNG files:

```bash
# Option 1: Use the Python script
cd homeassistant-integration
pip install cairosvg pillow
python generate_icon.py

# Option 2: Use ImageMagick
convert -background none -resize 256x256 logo.svg icon.png
convert -background none -resize 512x512 logo.svg icon@2x.png

# Option 3: Use rsvg-convert
rsvg-convert -w 256 -h 256 logo.svg -o icon.png
rsvg-convert -w 512 -h 512 logo.svg -o icon@2x.png
```

## Design

The icon represents:

- **Blue location pin**: Main tracking functionality
- **Google colors**: Brand identity (#4285F4, #34A853)
- **Signal waves**: "Find My" / location capability
- **Device icons**: Multiple types of trackable devices

## Customization

To customize the icon:

1. Edit `logo.svg` with a vector editor (Inkscape, Illustrator, Figma)
2. Regenerate the PNGs using the script or conversion tools
3. Update the `home-assistant/brands` PR (see the warning at the top) with the new
   PNGs - restarting Home Assistant alone won't show any change here

## License

The icons are designed for use with this Home Assistant integration.
Colors and style follow Google's brand guidelines.
