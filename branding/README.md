# Branding

Icon source assets for the `find_my_device` integration.

## Why these files aren't enough on their own

Since Home Assistant introduced the brands system (~2021), the icon shown on
the Devices & Services / integrations list page is fetched exclusively from
the public **[home-assistant/brands](https://github.com/home-assistant/brands)**
repository, keyed by domain (`find_my_device`) - the actual HA UI never reads
icon files from a custom integration's own repo, no matter where they live.

`custom_components/find_my_device/brand/` (generated from the SVGs here)
satisfies **HACS's own automated "brands" check** - HACS falls back to
checking for local assets there before checking the real brands repo, so
having them there is enough for HACS to list this integration. It does
**not** make the icon show up in Home Assistant's own UI, though - that
still needs the real fix below.

**For the icon to actually show up in HA**: submit `icon.png` (256×256) and
optionally `icon@2x.png` (512×512) / `logo.png` to
`custom_integrations/find_my_device/` in the home-assistant/brands repo via
a PR (see their `CONTRIBUTING.md` for the exact submission format), and wait
for it to be reviewed and merged. Until then, expect "icon not available" in
the HA UI - it's cosmetic only and doesn't affect functionality.

## Available Files

- **`logo.svg`** - Simple static logo (recommended source for PNGs)
- **`icon.svg`** - Animated icon with radar waves (more dynamic, alternative source)
- **`generate_icon.py`** - Renders the SVGs to PNG at the required sizes
- **`../custom_components/find_my_device/brand/`** - the generated `icon.png`/`icon@2x.png` HACS checks for locally (see above)

## Generate PNG from SVG

```bash
# Option 1: the included Python script
cd branding
pip install cairosvg pillow
python generate_icon.py

# Option 2: ImageMagick
convert -background none -resize 256x256 logo.svg icon.png
convert -background none -resize 512x512 logo.svg icon@2x.png

# Option 3: rsvg-convert
rsvg-convert -w 256 -h 256 logo.svg -o icon.png
rsvg-convert -w 512 -h 512 logo.svg -o icon@2x.png
```

## Design

- **Blue location pin** with gradient, containing a generic "you are here"
  crosshair/target dot - no third-party logo marks
- **Signal waves** indicating "Find My" / tracking
- **Device icons** at the bottom (phone, tablet, tracker)

**Colors**: Blue `#3B82F6` → `#1D4ED8` (pin gradient), Teal `#0EA5B7`
(signal waves), Slate Gray `#64748B` (devices), Background `#EFF3F8` (light
gray-blue). Deliberately distinct from Google's own brand palette (which the
original version of this icon reused, along with a recreation of Google's
"G" logomark - both replaced for trademark-safety reasons).

## Customization

1. Edit `logo.svg` / `icon.svg` with a vector editor (Inkscape, Illustrator, Figma)
2. Regenerate the PNGs using `generate_icon.py` or a conversion tool above
3. Update the `home-assistant/brands` PR with the new PNGs - restarting Home
   Assistant alone won't show any change here
