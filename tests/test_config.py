import unittest
from unittest.mock import patch, mock_open
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config import Config, DEFAULT_CONFIG  # noqa: E402


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Reset Singleton state before each test
        Config._instance = None
        Config._config = {}

    def tearDown(self):
        # Clean up
        Config._instance = None
        Config._config = {}

    def test_singleton(self):
        """Test that Config follows Singleton pattern"""
        c1 = Config()
        c2 = Config()
        self.assertIs(c1, c2)
        self.assertEqual(c1._config, c2._config)

    def test_defaults_loaded(self):
        """Test that default values are loaded"""
        config = Config()
        self.assertEqual(config.get("MAX_THREADS"), DEFAULT_CONFIG["MAX_THREADS"])
        self.assertEqual(config.get("UI_FRAMEWORK"), DEFAULT_CONFIG["UI_FRAMEWORK"])

    @patch("src.utils.config.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"MAX_THREADS": 12}')
    def test_json_override(self, mock_file, mock_exists):
        """Test that config.json overrides defaults"""

        # Simulate config.json exists
        def exists_side_effect(path):
            if "config.json" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        config = Config()
        self.assertEqual(config.get("MAX_THREADS"), 12)

    @patch("src.utils.config.os.path.exists")
    @patch("src.utils.config.load_dotenv")
    @patch("src.utils.config.os.getenv")
    def test_env_override(self, mock_getenv, mock_load_dotenv, mock_exists):
        """Test that environment variables override everything"""

        # Simulate .env exists
        def exists_side_effect(path):
            if ".env" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        # Mock getenv
        def getenv_side_effect(key):
            if key == "MAX_THREADS":
                return "16"
            return None

        mock_getenv.side_effect = getenv_side_effect

        config = Config()
        self.assertEqual(config.get("MAX_THREADS"), 16)
        mock_load_dotenv.assert_called()

    def test_type_conversion(self):
        """Test type conversion for environment variables"""
        config = Config()
        # Ensure defaults are loaded so types are known

        # Test bool conversion
        config._set_env_value("OPTIMIZE_SYSTEM", "false")
        self.assertFalse(config.get("OPTIMIZE_SYSTEM"))
        config._set_env_value("OPTIMIZE_SYSTEM", "1")
        self.assertTrue(config.get("OPTIMIZE_SYSTEM"))

        # Test int conversion
        config._set_env_value("MAX_THREADS", "32")
        self.assertEqual(config.get("MAX_THREADS"), 32)

        # Test invalid int conversion (should retain previous value)
        config._set_env_value("MAX_THREADS", "invalid")
        self.assertEqual(config.get("MAX_THREADS"), 32)

    def test_get_set(self):
        """Test get and set methods"""
        config = Config()
        config.set("NEW_KEY", "NEW_VALUE")
        self.assertEqual(config.get("NEW_KEY"), "NEW_VALUE")
        self.assertEqual(config.get("NON_EXISTENT", "DEFAULT"), "DEFAULT")

    @patch("src.utils.config.CONFIG_FILE_PATH", "/tmp/mock_config.json")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_save(self, mock_makedirs, mock_file):
        """Test saving configuration"""
        config = Config()
        config.set("TEST", "value")
        self.assertTrue(config.save())
        mock_file.assert_called_with("/tmp/mock_config.json", "w")
        mock_makedirs.assert_called()

    @patch("src.utils.config.APP_DIR", "/tmp")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_env_example(self, mock_file):
        """Test creating .env.example"""
        config = Config()
        self.assertTrue(config.create_env_example())
        mock_file.assert_called_with("/tmp/.env.example", "w")

    def test_platform_properties(self):
        """Test platform detection properties"""
        config = Config()
        # Just check they return booleans
        self.assertIsInstance(config.is_windows, bool)
        self.assertIsInstance(config.is_macos, bool)
        self.assertIsInstance(config.is_linux, bool)
