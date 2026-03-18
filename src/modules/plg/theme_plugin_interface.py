"""
Auralis - Theme Plugin Interface

Defines the `ThemePluginInterface` specializing the base `PluginInterface`.
"""

from abc import abstractmethod
from typing import Dict, Any
from src.plugins.plugin_interface import PluginInterface


class ThemePluginInterface(PluginInterface):
    """
    Abstract Base Class for Auralis Theme Plugins.
    Requires implementation of `get_stylesheet` and `get_palette`.
    """

    @abstractmethod
    def get_stylesheet(self) -> str:
        """
        Returns the Qt Stylesheet string.

        Returns:
            str: The QSS styles to be applied.
        """
        pass

    @abstractmethod
    def get_palette(self) -> Dict[str, Any]:
        """
        Returns a dictionary representing the color palette.
        This could be used by internal QPalette logic or custom drawing.

        Returns:
            Dict[str, Any]: The color palette mapped by color roles/names.
        """
        pass
