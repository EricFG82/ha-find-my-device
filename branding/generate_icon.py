#!/usr/bin/env python3
"""
Script to generate PNG icon from SVG for Home Assistant integration.

Requirements:
    pip install cairosvg pillow

Usage:
    python generate_icon.py
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import cairosvg
        from PIL import Image
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install required packages:")
        print("  pip install cairosvg pillow")
        return False

def generate_png_from_svg(svg_path: Path, png_path: Path, size: int = 256):
    """
    Convert SVG to PNG with specified size.
    
    Args:
        svg_path: Path to input SVG file
        png_path: Path to output PNG file
        size: Output size in pixels (width and height)
    """
    try:
        import cairosvg
        from PIL import Image
        import io
        
        print(f"📄 Reading SVG: {svg_path}")
        
        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size
        )
        
        # Open with PIL to ensure proper format
        img = Image.open(io.BytesIO(png_data))
        
        # Ensure RGBA mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Save as PNG
        img.save(png_path, 'PNG', optimize=True)
        
        print(f"✅ Generated PNG: {png_path} ({size}x{size})")
        return True
        
    except Exception as e:
        print(f"❌ Error generating PNG: {e}")
        return False

def main():
    """Main function to generate icon files."""
    print("🎨 Find My Device - Icon Generator")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # SVGs live alongside this script; PNGs go into the integration's
    # brand/ folder (which HACS checks for locally - see branding/README.md).
    script_dir = Path(__file__).parent
    brand_dir = script_dir.parent / "custom_components" / "find_my_device" / "brand"
    brand_dir.mkdir(parents=True, exist_ok=True)

    # Define file paths
    logo_svg = script_dir / "logo.svg"
    icon_svg = script_dir / "icon.svg"
    icon_png = brand_dir / "icon.png"
    icon_2x_png = brand_dir / "icon@2x.png"

    # Check if SVG files exist
    if not logo_svg.exists() and not icon_svg.exists():
        print(f"❌ No SVG files found in {script_dir}")
        sys.exit(1)

    # Prefer logo.svg over icon.svg for static icon
    source_svg = logo_svg if logo_svg.exists() else icon_svg

    print(f"\n📂 Output directory: {brand_dir}")
    print(f"📄 Source SVG: {source_svg.name}")
    print()
    
    # Generate standard icon (256x256)
    print("Generating standard icon (256x256)...")
    if generate_png_from_svg(source_svg, icon_png, 256):
        file_size = icon_png.stat().st_size / 1024
        print(f"   Size: {file_size:.1f} KB")
    
    print()
    
    # Generate retina icon (512x512)
    print("Generating retina icon (512x512)...")
    if generate_png_from_svg(source_svg, icon_2x_png, 512):
        file_size = icon_2x_png.stat().st_size / 1024
        print(f"   Size: {file_size:.1f} KB")
    
    print()
    print("=" * 50)
    print("✅ Icon generation complete!")
    print()
    print("Next steps:")
    print("1. These PNGs satisfy HACS's own local 'brands' check - commit them.")
    print("2. For the icon to show up in Home Assistant's own UI, submit them")
    print("   to home-assistant/brands (see branding/README.md).")

if __name__ == "__main__":
    main()

