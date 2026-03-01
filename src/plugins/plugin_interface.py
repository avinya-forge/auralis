"""
Auralis - Plugin Interface

This module defines the abstract base class for all Auralis plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PluginInterface(ABC):
    """
    Abstract Base Class for all Auralis plugins.
    Any custom plugin must inherit from this class and implement its abstract methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """The version string of the plugin (e.g., '1.0.0')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A short description of what the plugin does."""
        pass

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """
        Called when the plugin is loaded.

        Args:
            context (Dict[str, Any]): A dictionary containing the application context
                                      (e.g., 'app', 'config', 'services').

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Called when the plugin is being unloaded or the application is closing."""
        pass
