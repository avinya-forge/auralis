#!/usr/bin/env python3
"""
Script to create a splash screen image for Auralis
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_splash_image():
    """Create a simple splash screen image"""
    # Create a new image with a dark background
    width, height = 600, 400
    image = Image.new('RGBA', (width, height), (40, 40, 45, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple gradient background
    for y in range(height):
        # Create a subtle gradient
        r = int(40 + (y / height) * 40)
        g = int(40 + (y / height) * 30)
        b = int(45 + (y / height) * 50)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    # Add title text
    try:
        # Try to load a font, fall back to default if not available
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        # Use default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    title_text = "AURALIS"
    subtitle_text = "Music File Management"
    version_text = "v1.0"
    
    # Get text sizes
    title_width = draw.textlength(title_text, font=font_large) if hasattr(draw, 'textlength') else 250
    subtitle_width = draw.textlength(subtitle_text, font=font_small) if hasattr(draw, 'textlength') else 180
    
    # Draw texts
    draw.text(
        (width // 2 - title_width // 2, height // 3), 
        title_text, 
        font=font_large, 
        fill=(240, 240, 255, 255)
    )
    
    draw.text(
        (width // 2 - subtitle_width // 2, height // 2), 
        subtitle_text, 
        font=font_small, 
        fill=(200, 200, 220, 255)
    )
    
    draw.text(
        (width - 70, height - 40), 
        version_text, 
        font=font_small, 
        fill=(180, 180, 200, 255)
    )
    
    # Create resources directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"), exist_ok=True)
    
    # Save the image
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "splash.png")
    image.save(output_path)
    print(f"Created splash screen image at {output_path}")
    return output_path

if __name__ == "__main__":
    create_splash_image() 