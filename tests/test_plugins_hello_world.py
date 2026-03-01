"""
Tests for Hello World Plugin
"""

import unittest
from unittest.mock import patch

from src.plugins.sample_plugins.hello_world import HelloWorldPlugin


class TestHelloWorldPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = HelloWorldPlugin()
        self.context = {"app_name": "TestApp"}

    def test_properties(self):
        """Test the plugin properties return expected values."""
        self.assertEqual(self.plugin.name, "Hello World Plugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertTrue("sample plugin" in self.plugin.description)

    @patch("src.plugins.sample_plugins.hello_world.logger")
    def test_initialize(self, mock_logger):
        """Test initialization logs correctly and returns True."""
        result = self.plugin.initialize(self.context)

        self.assertTrue(result)
        mock_logger.info.assert_called_once_with(
            "[Hello World Plugin] Hello World! Initialized within context: TestApp"
        )

    @patch("src.plugins.sample_plugins.hello_world.logger")
    def test_initialize_default_context(self, mock_logger):
        """Test initialization with empty context uses default."""
        result = self.plugin.initialize({})

        self.assertTrue(result)
        mock_logger.info.assert_called_once_with(
            "[Hello World Plugin] Hello World! Initialized within context: Auralis"
        )

    @patch("src.plugins.sample_plugins.hello_world.logger")
    def test_shutdown(self, mock_logger):
        """Test shutdown logs correctly."""
        self.plugin.shutdown()

        mock_logger.info.assert_called_once_with(
            "[Hello World Plugin] Goodbye World! Shutting down."
        )


if __name__ == "__main__":
    unittest.main()
