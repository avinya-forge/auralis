import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.ui_factory import UIFactory, get_ui_framework

class TestUIFactory:

    def test_get_ui_framework_default(self):
        # Ensure environment variable is not set for this test
        with patch.dict(os.environ, {}, clear=True):
            assert get_ui_framework() == 'pyqt6'

    def test_get_ui_framework_custom(self):
        with patch.dict(os.environ, {'UI_FRAMEWORK': 'wxpython'}):
            assert get_ui_framework() == 'wxpython'

    @patch('src.gui.ui_factory.get_ui_framework')
    @patch('PyQt6.QtWidgets.QApplication')
    def test_create_app_pyqt6(self, mock_qapp, mock_framework):
        mock_framework.return_value = 'pyqt6'
        UIFactory.create_app([])
        mock_qapp.assert_called_once()

    @patch('src.gui.ui_factory.get_ui_framework')
    def test_create_app_wxpython_not_installed(self, mock_framework):
        mock_framework.return_value = 'wxpython'
        # Simulate wx not being installed
        with patch.dict('sys.modules', {'wx': None}):
             with pytest.raises(ImportError):
                UIFactory.create_app([])

    @patch('src.gui.ui_factory.get_ui_framework')
    def test_create_app_invalid(self, mock_framework):
        mock_framework.return_value = 'invalid'
        with pytest.raises(ValueError):
            UIFactory.create_app([])

    @patch('src.gui.ui_factory.get_ui_framework')
    @patch('src.gui.pyqt.main_window.MainWindow')
    def test_create_main_window_pyqt6(self, mock_mw, mock_framework):
        mock_framework.return_value = 'pyqt6'
        UIFactory.create_main_window()
        mock_mw.assert_called_once()

    @patch('src.gui.ui_factory.get_ui_framework')
    def test_create_main_window_wxpython(self, mock_framework):
        mock_framework.return_value = 'wxpython'
        with pytest.raises(NotImplementedError):
            UIFactory.create_main_window()

    def test_get_icon_path(self):
        path = UIFactory.get_icon_path("test")
        assert isinstance(path, str)
        assert "test" in path
