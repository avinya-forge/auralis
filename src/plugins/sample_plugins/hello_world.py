"""
Auralis - Hello World Sample Plugin

This is a minimal example of an Auralis plugin demonstrating the required
methods and properties of the PluginInterface.
"""

import logging
from typing import Any, Dict

from src.plugins.plugin_interface import PluginInterface

logger = logging.getLogger(__name__)


class HelloWorldPlugin(PluginInterface):
    """
    A simple "Hello World" plugin for demonstration purposes.
    """

    @property
    def name(self) -> str:
        """The display name of the plugin."""
        return "Hello World Plugin"

    @property
    def version(self) -> str:
        """The version string of the plugin."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """A short description of what the plugin does."""
        return "A sample plugin that logs a greeting upon initialization."

    def initialize(self, context: Dict[str, Any]) -> bool:
        """
        Called when the plugin is loaded.

        Args:
            context (Dict[str, Any]): The application context.

        Returns:
            bool: True if initialization was successful.
        """
        app_name = context.get("app_name", "Auralis")
        logger.info(f"[{self.name}] Hello World! Initialized within context: {app_name}")
        return True

    def shutdown(self) -> None:
        """Called when the plugin is being unloaded."""
        logger.info(f"[{self.name}] Goodbye World! Shutting down.")
