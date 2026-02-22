"""
Unit tests for ThemeManager
"""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.gui.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):
    """Test cases for ThemeManager"""

    def setUp(self):
        # Reset singleton instance
        ThemeManager._instance = None

        # Create patches
        self.patcher_listdir = patch("os.listdir")
        self.mock_listdir = self.patcher_listdir.start()

        self.patcher_exists = patch("os.path.exists")
        self.mock_exists = self.patcher_exists.start()

        # We need to mock open, but it's tricky with json.load
        # Instead of mocking open and json.load separately, mocking json.load is easier
        # but ThemeManager uses open().
        # Let's mock builtins.open
        self.patcher_open = patch("builtins.open", new_callable=mock_open)
        self.mock_open = self.patcher_open.start()

        self.patcher_json = patch("json.load")
        self.mock_json_load = self.patcher_json.start()

        # Setup default mocks
        self.mock_listdir.return_value = ["test_theme.json"]
        self.mock_exists.return_value = True

        # Setup json content
        self.mock_json_load.return_value = {
            "name": "Test Theme",
            "palette": {"window": "#000000"},
            "stylesheet": "QWidget { color: red; }",
        }

    def tearDown(self):
        self.patcher_listdir.stop()
        self.patcher_exists.stop()
        self.patcher_open.stop()
        self.patcher_json.stop()
        ThemeManager._instance = None

    def test_singleton(self):
        """Test singleton pattern"""
        tm1 = ThemeManager()
        tm2 = ThemeManager()
        self.assertIs(tm1, tm2)

    def test_load_themes(self):
        """Test loading themes from directory"""
        tm = ThemeManager()
        self.assertIn("Test Theme", tm.themes)
        self.assertEqual(tm.themes["Test Theme"]["palette"]["window"], "#000000")

        # Verify open was called
        self.mock_open.assert_called()

    def test_apply_theme(self):
        """Test applying theme to application"""
        tm = ThemeManager()
        mock_app = MagicMock()

        success = tm.apply_theme(mock_app, "Test Theme")
        self.assertTrue(success)
        mock_app.setPalette.assert_called_once()
        mock_app.setStyleSheet.assert_called_with("QWidget { color: red; }")
        self.assertEqual(tm.current_theme_name, "Test Theme")

    def test_apply_theme_not_found(self):
        """Test applying non-existent theme"""
        tm = ThemeManager()
        mock_app = MagicMock()

        success = tm.apply_theme(mock_app, "NonExistent")
        self.assertFalse(success)
        mock_app.setPalette.assert_not_called()

    def test_get_available_themes(self):
        """Test getting available themes"""
        tm = ThemeManager()
        themes = tm.get_available_themes()
        self.assertIn("Test Theme", themes)
