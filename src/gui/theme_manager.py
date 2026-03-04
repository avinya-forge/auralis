"""
Auralis - Theme Manager

Handles loading and applying UI themes.
"""

import json
import logging
import os
from typing import Dict, List, Optional, TypedDict

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class ThemeColors(TypedDict, total=False):
    window: str
    window_text: str
    base: str
    alternate_base: str
    text: str
    button: str
    button_text: str
    bright_text: str
    link: str
    highlight: str
    highlighted_text: str


class Theme(TypedDict, total=False):
    name: str
    palette: ThemeColors
    stylesheet: str


class ThemeManager:
    """
    Singleton class for managing UI themes.
    """

    _instance = None
    _initialized: bool = False

    def __new__(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.themes: Dict[str, Theme] = {}
        self.current_theme_name: Optional[str] = None

        # Load themes directory
        # Assuming resources/themes is relative to project root
        # We can find it relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.themes_dir = os.path.join(base_dir, "resources", "themes")

        self.load_themes()
        self._initialized = True

    def load_themes(self) -> None:
        """Load all themes from the themes directory."""
        if not os.path.exists(self.themes_dir):
            self.logger.warning(f"Themes directory not found: {self.themes_dir}")
            return

        for filename in os.listdir(self.themes_dir):
            if filename.endswith(".json"):
                theme_path = os.path.join(self.themes_dir, filename)
                try:
                    with open(theme_path, "r") as f:
                        theme_data = json.load(f)
                        if "name" in theme_data:
                            self.themes[theme_data["name"]] = theme_data
                except Exception as e:
                    self.logger.error(f"Error loading theme {filename}: {e}")

    def apply_theme(self, app: QApplication, theme_name: str) -> bool:
        """
        Apply a theme to the application.

        Args:
            app (QApplication): The Qt application instance.
            theme_name (str): The name of the theme to apply.

        Returns:
            bool: True if theme was applied, False otherwise.
        """
        if theme_name not in self.themes:
            self.logger.error(f"Theme not found: {theme_name}")
            return False

        theme = self.themes[theme_name]

        # Apply Palette
        if "palette" in theme:
            palette = QPalette()
            colors = theme["palette"]

            color_roles = {
                "window": QPalette.ColorRole.Window,
                "window_text": QPalette.ColorRole.WindowText,
                "base": QPalette.ColorRole.Base,
                "alternate_base": QPalette.ColorRole.AlternateBase,
                "text": QPalette.ColorRole.Text,
                "button": QPalette.ColorRole.Button,
                "button_text": QPalette.ColorRole.ButtonText,
                "bright_text": QPalette.ColorRole.BrightText,
                "link": QPalette.ColorRole.Link,
                "highlight": QPalette.ColorRole.Highlight,
                "highlighted_text": QPalette.ColorRole.HighlightedText,
            }

            for key, role in color_roles.items():
                if key in colors:
                    palette.setColor(role, QColor(colors[key]))  # type: ignore

            app.setPalette(palette)

        # Apply Stylesheet
        if "stylesheet" in theme:
            app.setStyleSheet(theme["stylesheet"])
        else:
            app.setStyleSheet("")

        self.current_theme_name = theme_name
        self.logger.info(f"Applied theme: {theme_name}")
        return True

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
