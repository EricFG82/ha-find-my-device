# Branding

Icon source assets for the `google_find_my_device` integration.

## Why these files aren't enough on their own

Since Home Assistant introduced the brands system (~2021), the icon shown on
the Devices & Services / integrations list page is fetched exclusively from
the public **[home-assistant/brands](https://github.com/home-assistant/brands)**
repository, keyed by domain (`google_find_my_device`) - files in
`custom_components/google_find_my_device/` are never read for that purpose, and
neither are the files in this folder. Until a PR there is merged, expect
"icon not available" in the HA UI regardless of what's here - it's cosmetic
only and doesn't affect functionality.

**The actual fix**: submit `icon.png` (256×256) and optionally
`icon@2x.png` (512×512) / `logo.png` to `custom_integrations/google_find_my_device/`
in the home-assistant/brands repo via a PR (see their `CONTRIBUTING.md` for
the exact submission format), and wait for it to be reviewed and merged.

## Available Files

- **`logo.svg`** - Simple static logo (recommended source for the brands PR)
- **`icon.svg`** - Animated icon with radar waves (more dynamic, alternative source)
- **`generate_icon.py`** - Renders the SVGs to PNG at the required sizes

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

- **Blue location pin** with gradient (Google colors: #4285F4 → #1967D2), a
  simplified Google-style dot in the center
- **Signal waves** indicating "Find My" / tracking
- **Device icons** at the bottom (phone, tablet, tracker)

**Colors**: Google Blue `#4285F4` (primary), Dark Blue `#1967D2` (shadows),
Google Green `#34A853` (signal waves), Gray `#5F6368` (devices), Background
`#F1F3F4` (light gray).

## Customization

1. Edit `logo.svg` / `icon.svg` with a vector editor (Inkscape, Illustrator, Figma)
2. Regenerate the PNGs using `generate_icon.py` or a conversion tool above
3. Update the `home-assistant/brands` PR with the new PNGs - restarting Home
   Assistant alone won't show any change here
