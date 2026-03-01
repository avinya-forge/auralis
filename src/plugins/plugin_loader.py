"""
Auralis - Plugin Loader

This module manages the discovery, loading, and lifecycle of Auralis plugins.
"""

import importlib
import importlib.util
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from src.plugins.plugin_interface import PluginInterface

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Manages loading and initialization of external plugins via importlib.
    """

    def __init__(self, plugin_dir: str = "plugins") -> None:
        """
        Initialize the PluginLoader.

        Args:
            plugin_dir (str): Relative or absolute path to the plugins directory.
        """
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.context: Dict[str, Any] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set the application context to be passed to plugins on initialization."""
        self.context = context

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory.
        A plugin is considered available if it's a python file or a directory
        with an __init__.py file inside the plugin directory.

        Returns:
            List[str]: List of discovered plugin names (module names).
        """
        if not os.path.exists(self.plugin_dir):
            return []

        plugin_names = []
        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)

            # Skip hidden files or __pycache__
            if item.startswith("__") or item.startswith("."):
                continue

            # Python file (e.g., my_plugin.py)
            if os.path.isfile(item_path) and item.endswith(".py"):
                plugin_names.append(item[:-3])

            # Directory with __init__.py
            elif os.path.isdir(item_path) and os.path.isfile(
                os.path.join(item_path, "__init__.py")
            ):
                plugin_names.append(item)

        return plugin_names

    def load_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Load a specific plugin by name.

        Args:
            plugin_name (str): The name of the plugin module.

        Returns:
            Optional[PluginInterface]: The loaded plugin instance, or None if failed.
        """
        if plugin_name in self.plugins:
            logger.info(f"Plugin '{plugin_name}' is already loaded.")
            return self.plugins[plugin_name]

        # Add the plugin directory to sys.path temporarily to resolve imports
        plugin_path_abs = os.path.abspath(self.plugin_dir)
        if plugin_path_abs not in sys.path:
            sys.path.insert(0, plugin_path_abs)

        try:
            # Dynamically import the module
            module = importlib.import_module(plugin_name)

            # Find a class that inherits from PluginInterface
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginInterface)
                    and attr is not PluginInterface
                ):
                    plugin_class = attr
                    break

            if plugin_class is None:
                logger.error(f"No valid PluginInterface found in plugin '{plugin_name}'.")
                return None

            # Instantiate the plugin
            plugin_instance = plugin_class()

            # Initialize the plugin
            if not plugin_instance.initialize(self.context):
                logger.error(f"Plugin '{plugin_name}' failed to initialize.")
                return None

            self.plugins[plugin_name] = plugin_instance
            logger.info(
                f"Successfully loaded plugin: {plugin_instance.name} v{plugin_instance.version}"
            )
            return plugin_instance

        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return None
        finally:
            # Clean up sys.path
            if plugin_path_abs in sys.path:
                sys.path.remove(plugin_path_abs)

    def load_all(self) -> None:
        """Discover and load all available plugins in the plugin directory."""
        discovered = self.discover_plugins()
        for name in discovered:
            self.load_plugin(name)

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a specific plugin.

        Args:
            plugin_name (str): The name of the plugin module.

        Returns:
            bool: True if unloaded successfully, False otherwise.
        """
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].shutdown()
                del self.plugins[plugin_name]

                # Also remove from sys.modules to allow reloading if needed
                if plugin_name in sys.modules:
                    del sys.modules[plugin_name]

                logger.info(f"Successfully unloaded plugin '{plugin_name}'.")
                return True
            except Exception as e:
                logger.error(f"Error shutting down plugin '{plugin_name}': {e}")
                return False
        return False

    def unload_all(self) -> None:
        """Unload all currently loaded plugins."""
        # Create a list of keys to avoid dict size change during iteration
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
