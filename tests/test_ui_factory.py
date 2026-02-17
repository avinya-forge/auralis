import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.gui.ui_factory import UIFactory, get_ui_framework

# Add project root to path if needed, but usually pytest handles this.
# If we must keep it, we can put it in a try/except or just assume environment is set.
# To satisfy E402, we can put this after imports if we suppress the error,
# or we can assume that we don't need it if running via `python -m pytest`.


class TestUIFactory:

    @pytest.fixture(autouse=True)
    def mock_gui_modules(self):
        """Mock GUI modules to avoid ImportError in CI environment"""
        with patch.dict(
            "sys.modules",
            {
                "PyQt6": MagicMock(),
                "PyQt6.QtWidgets": MagicMock(),
                "src.gui.pyqt.main_window": MagicMock(),
                "wx": MagicMock(),
                "src.gui.wx.main_window": MagicMock(),
            },
        ):
            yield

    def test_get_ui_framework_default(self):
        # Ensure environment variable is not set for this test
        with patch.dict(os.environ, {}, clear=True):
            assert get_ui_framework() == "pyqt6"

    def test_get_ui_framework_custom(self):
        with patch.dict(os.environ, {"UI_FRAMEWORK": "wxpython"}):
            assert get_ui_framework() == "wxpython"

    @patch("src.gui.ui_factory.get_ui_framework")
    def test_create_app_pyqt6(self, mock_framework):
        mock_framework.return_value = "pyqt6"

        # We need to patch where it's imported in the function,
        # BUT since we masked sys.modules in the fixture,
        # the import inside create_app will get the Mock from sys.modules.

        # We can configure that mock to return what we want.
        mock_qapp_cls = sys.modules["PyQt6.QtWidgets"].QApplication

        UIFactory.create_app([])
        mock_qapp_cls.assert_called_once()

    @patch("src.gui.ui_factory.get_ui_framework")
    def test_create_app_wxpython_not_installed(self, mock_framework):
        mock_framework.return_value = "wxpython"
        # Simulate wx not being installed by patching import inside the function?
        # Since sys.modules is patched globally by the fixture, "import wx" returns the mock.
        # To simulate ImportError, we need to override the fixture for this test
        # or verify if we can raise ImportError when accessing the mock.

        # We can temporarily unpatch 'wx' in sys.modules or set side_effect.
        # But sys.modules lookup happens at import time.
        # Since UIFactory.create_app does 'import wx' inside the function,
        # we can control it via sys.modules.

        with patch.dict("sys.modules", {"wx": None}):
            with pytest.raises(ImportError):
                UIFactory.create_app([])

    @patch("src.gui.ui_factory.get_ui_framework")
    def test_create_app_invalid(self, mock_framework):
        mock_framework.return_value = "invalid"
        with pytest.raises(ValueError):
            UIFactory.create_app([])

    @patch("src.gui.ui_factory.get_ui_framework")
    def test_create_main_window_pyqt6(self, mock_framework):
        mock_framework.return_value = "pyqt6"

        # Access the mock from sys.modules
        mock_mw_cls = sys.modules["src.gui.pyqt.main_window"].MainWindow

        UIFactory.create_main_window()
        mock_mw_cls.assert_called_once()

    @patch("src.gui.ui_factory.get_ui_framework")
    def test_create_main_window_wxpython(self, mock_framework):
        mock_framework.return_value = "wxpython"

        # Access the mock from sys.modules
        mock_mw_cls = sys.modules["src.gui.wx.main_window"].MainWindow

        UIFactory.create_main_window()
        mock_mw_cls.assert_called_once()

    def test_get_icon_path(self):
        path = UIFactory.get_icon_path("test")
        assert isinstance(path, str)
        assert "test" in path
