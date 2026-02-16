"""
Splash screen generator
"""

import os

from PIL import Image, ImageDraw, ImageFont


def create_splash(path, width=600, height=400):
    """
    Create a splash screen image
    """
    # Create image
    img = Image.new("RGB", (width, height), (44, 62, 80))
    draw = ImageDraw.Draw(img)

    # Draw title
    title = "AURALIS"
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    draw.text((width / 2, height / 3), title, font=font, fill=(236, 240, 241), anchor="mm")

    # Draw subtitle
    subtitle = "Music Library Manager"
    try:
        sub_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        sub_font = ImageFont.load_default()

    draw.text((width / 2, height / 2), subtitle, font=sub_font, fill=(189, 195, 199), anchor="mm")

    # Draw version
    version = "v0.1.0"
    try:
        ver_font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        ver_font = ImageFont.load_default()

    draw.text((width - 20, height - 20), version, font=ver_font, fill=(149, 165, 166), anchor="rb")

    # Save
    img.save(path)
    print(f"Splash screen created at {path}")


if __name__ == "__main__":
    # Ensure resources/images directory exists
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # Create splash
    splash_path = os.path.join(img_dir, "splash.png")
    create_splash(splash_path)
