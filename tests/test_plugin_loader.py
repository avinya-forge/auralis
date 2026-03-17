"""
Tests for Plugin Loader
"""

import os
import shutil
import tempfile
import unittest

from src.plugins.plugin_loader import PluginLoader


class TestPluginLoader(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for plugins
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_plugin_state.db")
        self.plugin_loader = PluginLoader(plugin_dir=self.test_dir, db_path=self.db_path)

        # Context to pass to plugins
        self.context = {"app": "AuralisTest"}
        self.plugin_loader.set_context(self.context)

    def tearDown(self):
        # Clean up temporary directory
        self.plugin_loader.unload_all()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        shutil.rmtree(self.test_dir)

    def _create_mock_plugin(self, name: str, code: str) -> None:
        """Helper to create a python file with plugin code in test dir."""
        path = os.path.join(self.test_dir, f"{name}.py")
        with open(path, "w") as f:
            f.write(code)

    def test_discover_plugins_empty(self):
        """Test discovering plugins in an empty directory."""
        plugins = self.plugin_loader.discover_plugins()
        self.assertEqual(plugins, [])

    def test_discover_plugins_with_files(self):
        """Test discovering plugins when files are present."""
        self._create_mock_plugin("mock_plugin1", "# valid plugin file")
        self._create_mock_plugin("mock_plugin2", "# valid plugin file")

        # Add a file that should be ignored
        with open(os.path.join(self.test_dir, "ignore_me.txt"), "w") as f:
            f.write("test")

        # Add a __pycache__ dir
        os.makedirs(os.path.join(self.test_dir, "__pycache__"))

        plugins = self.plugin_loader.discover_plugins()
        self.assertEqual(len(plugins), 2)
        self.assertIn("mock_plugin1", plugins)
        self.assertIn("mock_plugin2", plugins)

    def test_load_plugin_success(self):
        """Test loading a valid plugin."""
        valid_plugin_code = """
from src.plugins.plugin_interface import PluginInterface

class MockPlugin(PluginInterface):
    @property
    def name(self):
        return "Mock Plugin"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "A mock plugin for testing."

    def initialize(self, context):
        self.initialized = True
        return True

    def shutdown(self):
        self.initialized = False
"""
        self._create_mock_plugin("valid_plugin", valid_plugin_code)

        # Load plugin
        plugin = self.plugin_loader.load_plugin("valid_plugin")

        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "Mock Plugin")
        self.assertEqual(plugin.version, "1.0.0")
        self.assertEqual(plugin.description, "A mock plugin for testing.")

        # Check initialization was called
        self.assertTrue(getattr(plugin, "initialized", False))

        # Check plugin added to dict
        self.assertIn("valid_plugin", self.plugin_loader.plugins)

    def test_load_plugin_missing_interface(self):
        """Test loading a plugin that doesn't implement PluginInterface."""
        invalid_plugin_code = """
class InvalidPlugin:
    pass
"""
        self._create_mock_plugin("invalid_plugin", invalid_plugin_code)

        plugin = self.plugin_loader.load_plugin("invalid_plugin")
        self.assertIsNone(plugin)
        self.assertNotIn("invalid_plugin", self.plugin_loader.plugins)

    def test_load_plugin_init_fails(self):
        """Test loading a plugin where initialization fails."""
        failing_plugin_code = """
from src.plugins.plugin_interface import PluginInterface

class FailingPlugin(PluginInterface):
    @property
    def name(self): return "Fail"
    @property
    def version(self): return "1.0.0"
    @property
    def description(self): return "Fails."

    def initialize(self, context):
        return False

    def shutdown(self):
        pass
"""
        self._create_mock_plugin("failing_plugin", failing_plugin_code)

        plugin = self.plugin_loader.load_plugin("failing_plugin")
        self.assertIsNone(plugin)
        self.assertNotIn("failing_plugin", self.plugin_loader.plugins)

    def test_unload_plugin(self):
        """Test unloading a plugin."""
        plugin_code = """
from src.plugins.plugin_interface import PluginInterface

class TPlugin(PluginInterface):
    @property
    def name(self): return "T"
    @property
    def version(self): return "1.0.0"
    @property
    def description(self): return "T"

    def initialize(self, context):
        self.shutdown_called = False
        return True

    def shutdown(self):
        self.shutdown_called = True
"""
        self._create_mock_plugin("t_plugin", plugin_code)

        # Load
        plugin = self.plugin_loader.load_plugin("t_plugin")
        self.assertIsNotNone(plugin)
        self.assertIn("t_plugin", self.plugin_loader.plugins)

        # Unload
        result = self.plugin_loader.unload_plugin("t_plugin")

        self.assertTrue(result)
        self.assertNotIn("t_plugin", self.plugin_loader.plugins)

        # Check shutdown was called
        self.assertTrue(getattr(plugin, "shutdown_called", False))

        # Unload missing plugin
        self.assertFalse(self.plugin_loader.unload_plugin("missing"))

    def test_load_plugin_disabled(self):
        """Test that disabled plugins are not loaded."""
        valid_plugin_code = """
from src.plugins.plugin_interface import PluginInterface

class MockPlugin(PluginInterface):
    @property
    def name(self): return "Mock Plugin"
    @property
    def version(self): return "1.0.0"
    @property
    def description(self): return "A mock plugin for testing."

    def initialize(self, context):
        self.initialized = True
        return True

    def shutdown(self):
        self.initialized = False
"""
        self._create_mock_plugin("disabled_plugin", valid_plugin_code)

        # Disable the plugin in the state tracker
        self.plugin_loader.plugin_state.set_plugin_active("disabled_plugin", False)

        # Attempt to load plugin
        plugin = self.plugin_loader.load_plugin("disabled_plugin")

        self.assertIsNone(plugin)
        self.assertNotIn("disabled_plugin", self.plugin_loader.plugins)

    def test_load_all_and_unload_all(self):
        """Test load_all and unload_all methods."""
        code1 = """
from src.plugins.plugin_interface import PluginInterface

class P1(PluginInterface):
    @property
    def name(self): return "P1"
    @property
    def version(self): return "1.0.0"
    @property
    def description(self): return "P1"
    def initialize(self, context): return True
    def shutdown(self): pass
"""
        code2 = """
from src.plugins.plugin_interface import PluginInterface

class P2(PluginInterface):
    @property
    def name(self): return "P2"
    @property
    def version(self): return "1.0.0"
    @property
    def description(self): return "P2"
    def initialize(self, context): return True
    def shutdown(self): pass
"""
        self._create_mock_plugin("p1", code1)
        self._create_mock_plugin("p2", code2)

        # Load all
        self.plugin_loader.load_all()

        self.assertEqual(len(self.plugin_loader.plugins), 2)
        self.assertIn("p1", self.plugin_loader.plugins)
        self.assertIn("p2", self.plugin_loader.plugins)

        # Unload all
        self.plugin_loader.unload_all()

        self.assertEqual(len(self.plugin_loader.plugins), 0)


if __name__ == "__main__":
    unittest.main()
