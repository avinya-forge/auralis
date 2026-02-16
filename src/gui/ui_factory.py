"""
Auralis - UI Factory Module

This module provides a factory for creating UI components, supporting multiple backends.
"""

import os

from src.utils.config import is_macos, is_windows

# Default UI framework
DEFAULT_FRAMEWORK = "pyqt6"


def get_ui_framework():
    """Get the configured UI framework"""
    return os.environ.get("UI_FRAMEWORK", DEFAULT_FRAMEWORK).lower()


class UIFactory:
    """Factory class for creating UI components"""

    @staticmethod
    def create_app(*args, **kwargs):
        """Create application instance"""
        framework = get_ui_framework()
        if framework == "pyqt6":
            from PyQt6.QtWidgets import QApplication

            return QApplication(*args, **kwargs)
        elif framework == "wxpython":
            try:
                import wx  # type: ignore

                return wx.App(*args, **kwargs)
            except ImportError:
                raise ImportError(
                    "wxPython is not installed. Please install it with 'pip install wxPython'."
                )
        else:
            raise ValueError(f"Unsupported UI framework: {framework}")

    @staticmethod
    def create_main_window():
        """Create main window"""
        framework = get_ui_framework()
        if framework == "pyqt6":
            from src.gui.pyqt.main_window import MainWindow

            return MainWindow()
        elif framework == "wxpython":
            # Placeholder for wxPython support
            raise NotImplementedError("wxPython backend is not yet implemented.")
        else:
            raise ValueError(f"Unsupported UI framework: {framework}")

    @staticmethod
    def get_icon_path(icon_name):
        """Get platform-specific icon path"""
        # Base path for icons
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "resources",
            "icons",
        )

        # Platform-specific formats
        if is_windows():
            return os.path.join(base_path, f"{icon_name}.ico")
        elif is_macos():
            return os.path.join(base_path, f"{icon_name}.icns")
        else:  # Linux and others
            return os.path.join(base_path, f"{icon_name}.png")

    @staticmethod
    def set_app_id():
        """Set application ID for proper taskbar grouping on Windows"""
        if is_windows():
            try:
                import ctypes

                app_id = "PatternSeekers.Auralis.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass


def create_app(*args, **kwargs):
    """Create application instance"""
    return UIFactory.create_app(*args, **kwargs)


def create_main_window():
    """Create main window"""
    return UIFactory.create_main_window()


def get_icon_path(icon_name):
    """Get platform-specific icon path"""
    return UIFactory.get_icon_path(icon_name)


def set_app_id():
    """Set application ID for proper taskbar grouping on Windows"""
    UIFactory.set_app_id()
