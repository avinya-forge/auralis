"""
Resource generation script for Auralis icons
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(path, size=256):
    """
    Create a simple icon for the application
    """
    # Create a new image with a transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a circle
    draw.ellipse((10, 10, size - 10, size - 10), fill=(41, 128, 185), outline=(52, 152, 219), width=5)

    # Draw text "A" in the center
    try:
        # Try to load a font
        font = ImageFont.truetype("arial.ttf", int(size / 2))
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text size
    text = "A"
    # text_width, text_height = draw.textsize(text, font=font)
    # text_x = (size - text_width) / 2
    # text_y = (size - text_height) / 2

    # Draw text
    draw.text((size / 2, size / 2), text, font=font, fill=(255, 255, 255), anchor="mm")

    # Save the image
    img.save(path)
    print(f"Icon created at {path}")


if __name__ == "__main__":
    # Ensure resources/icons directory exists
    icon_dir = os.path.join(os.path.dirname(__file__), "icons")
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)

    # Create icon
    icon_path = os.path.join(icon_dir, "auralis.png")
    create_icon(icon_path)
