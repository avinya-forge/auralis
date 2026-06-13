import builtins
import os
import sys

import pytest

from src.modules.plg.plugin_sandbox import PluginSandboxFinder, enable_sandbox


class TestPluginIsolation:
    @pytest.fixture(autouse=True)
    def setup_sandbox(self):
        # We need to save the original __import__ to restore it after each test
        self.original_import = builtins.__import__
        enable_sandbox()
        yield
        # Teardown to restore the original state
        builtins.__import__ = self.original_import
        sys.meta_path = [f for f in sys.meta_path if not isinstance(f, PluginSandboxFinder)]

    def test_verify_isolation_os_system(self):
        # Create a mock plugin file inside the sandbox directory
        sandbox_dir = PluginSandboxFinder.SANDBOX_DIR
        os.makedirs(sandbox_dir, exist_ok=True)

        mock_file_path = os.path.join(sandbox_dir, "test_malicious_plugin_os.py")

        # Test blocking 'os' execution capability by blocking the import itself
        plugin_code = """
import os
os.system("echo 'Vulnerable'")
"""
        compiled_code = compile(plugin_code, mock_file_path, "exec")
        with pytest.raises(ImportError, match="Sandbox violation: importing 'os' is blocked."):
            exec(
                compiled_code, {"__file__": mock_file_path, "__name__": "test_malicious_plugin_os"}
            )

    def test_verify_isolation_subprocess(self):
        # Create a mock plugin file inside the sandbox directory
        sandbox_dir = PluginSandboxFinder.SANDBOX_DIR
        os.makedirs(sandbox_dir, exist_ok=True)

        mock_file_path = os.path.join(sandbox_dir, "test_malicious_plugin_subp.py")

        # Test blocking 'subprocess' execution capability
        plugin_code = """
import subprocess
subprocess.run(["echo", "Vulnerable"])
"""
        compiled_code = compile(plugin_code, mock_file_path, "exec")
        with pytest.raises(
            ImportError, match="Sandbox violation: importing 'subprocess' is blocked."
        ):
            exec(
                compiled_code,
                {"__file__": mock_file_path, "__name__": "test_malicious_plugin_subp"},
            )
