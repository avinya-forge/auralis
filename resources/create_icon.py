#!/usr/bin/env python3
"""
Script to create application icons for Auralis
"""

from PIL import Image, ImageDraw
import os

def create_app_icon():
    """Create application icons in different formats"""
    # Create a base icon image
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw a circular background
    circle_center = (size // 2, size // 2)
    circle_radius = size // 2 - 10
    draw.ellipse(
        [
            (circle_center[0] - circle_radius, circle_center[1] - circle_radius),
            (circle_center[0] + circle_radius, circle_center[1] + circle_radius)
        ],
        fill=(50, 50, 120, 255)
    )

    # Draw a smaller inner circle
    inner_radius = circle_radius * 0.8
    draw.ellipse(
        [
            (circle_center[0] - inner_radius, circle_center[1] - inner_radius),
            (circle_center[0] + inner_radius, circle_center[1] + inner_radius)
        ],
        fill=(70, 70, 140, 255)
    )

    # Draw a simple music note symbol
    note_color = (230, 230, 255, 255)

    # Note head
    note_head_center = (size // 2 + 20, size // 2 - 20)
    note_head_radius = size // 12
    draw.ellipse(
        [
            (note_head_center[0] - note_head_radius, note_head_center[1] - note_head_radius),
            (note_head_center[0] + note_head_radius, note_head_center[1] + note_head_radius)
        ],
        fill=note_color
    )

    # Note stem
    stem_width = size // 25
    draw.rectangle(
        [
            (note_head_center[0] - stem_width // 2, note_head_center[1]),
            (note_head_center[0] + stem_width // 2, note_head_center[1] + size // 3)
        ],
        fill=note_color
    )

    # Flag on the stem
    flag_points = [
        (note_head_center[0] + stem_width // 2, note_head_center[1] + size // 10),
        (note_head_center[0] + size // 6, note_head_center[1] + size // 6),
        (note_head_center[0] + stem_width // 2, note_head_center[1] + size // 4)
    ]
    draw.polygon(flag_points, fill=note_color)

    # Create resources/icons directory if it doesn't exist
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    # Save in different formats
    # PNG (all platforms)
    png_path = os.path.join(icons_dir, "auralis.png")
    image.save(png_path)

    # ICO (Windows)
    ico_path = os.path.join(icons_dir, "auralis.ico")
    # For ICO, we need to save with different sizes
    image.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    print(f"Created application icons in {icons_dir}")
    return icons_dir

if __name__ == "__main__":
    create_app_icon()