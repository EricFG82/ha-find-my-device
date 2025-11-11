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
    print("🎨 Google Find My Device - Icon Generator")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get script directory
    script_dir = Path(__file__).parent
    integration_dir = script_dir / "custom_components" / "google_findmy"
    
    # Check if integration directory exists
    if not integration_dir.exists():
        print(f"❌ Integration directory not found: {integration_dir}")
        sys.exit(1)
    
    # Define file paths
    logo_svg = integration_dir / "logo.svg"
    icon_svg = integration_dir / "icon.svg"
    icon_png = integration_dir / "icon.png"
    icon_2x_png = integration_dir / "icon@2x.png"
    
    # Check if SVG files exist
    if not logo_svg.exists() and not icon_svg.exists():
        print(f"❌ No SVG files found in {integration_dir}")
        sys.exit(1)
    
    # Prefer logo.svg over icon.svg for static icon
    source_svg = logo_svg if logo_svg.exists() else icon_svg
    
    print(f"\n📂 Working directory: {integration_dir}")
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
    print("1. Copy the integration to Home Assistant:")
    print(f"   cp -r {integration_dir} /config/custom_components/")
    print()
    print("2. Restart Home Assistant")
    print()
    print("3. Check Settings > Devices & Services for the new icon")

if __name__ == "__main__":
    main()

