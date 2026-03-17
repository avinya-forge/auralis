"""
Tests for Plugin State persistence
"""

import os
import tempfile
import unittest

from src.plugins.plugin_state import PluginState


class TestPluginState(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for db
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_plugin_state.db")
        self.plugin_state = PluginState(db_path=self.db_path)

    def tearDown(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test database initialization and table creation."""
        self.assertTrue(os.path.exists(self.db_path))

    def test_default_is_active(self):
        """Test that unknown plugins default to active."""
        self.assertTrue(self.plugin_state.is_plugin_active("unknown_plugin"))

    def test_set_plugin_active(self):
        """Test setting and retrieving active state."""
        # Disable plugin
        self.plugin_state.set_plugin_active("test_plugin_1", False)
        self.assertFalse(self.plugin_state.is_plugin_active("test_plugin_1"))

        # Enable plugin
        self.plugin_state.set_plugin_active("test_plugin_1", True)
        self.assertTrue(self.plugin_state.is_plugin_active("test_plugin_1"))

    def test_update_existing_plugin(self):
        """Test updating an already existing plugin record."""
        self.plugin_state.set_plugin_active("test_plugin_2", True)
        self.assertTrue(self.plugin_state.is_plugin_active("test_plugin_2"))

        # Change to false
        self.plugin_state.set_plugin_active("test_plugin_2", False)
        self.assertFalse(self.plugin_state.is_plugin_active("test_plugin_2"))


if __name__ == "__main__":
    unittest.main()
