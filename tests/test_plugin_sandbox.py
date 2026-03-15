import builtins
import os
import sys
import tempfile
import pytest

from src.modules.plg.plugin_sandbox import PluginSandboxFinder, enable_sandbox


class TestPluginSandboxFinder:
    @pytest.fixture(autouse=True)
    def setup_sandbox(self):
        # We need to save the original __import__ to restore it after each test
        self.original_import = builtins.__import__
        enable_sandbox()
        yield
        # Teardown to restore the original state
        builtins.__import__ = self.original_import
        sys.meta_path = [f for f in sys.meta_path if not isinstance(f, PluginSandboxFinder)]

    def test_allow_safe_imports_via_exec(self):
        # Create a mock plugin file inside the sandbox directory
        sandbox_dir = PluginSandboxFinder.SANDBOX_DIR
        os.makedirs(sandbox_dir, exist_ok=True)

        # We test that importing a safe module like 'json' is allowed
        plugin_code = """
import json
assert json is not None
"""
        # Execute the code as if it was loaded from inside the sandbox
        mock_file_path = os.path.join(sandbox_dir, "test_safe_plugin.py")
        compiled_code = compile(plugin_code, mock_file_path, "exec")
        exec(compiled_code, {"__file__": mock_file_path, "__name__": "test_safe_plugin"})

    def test_block_banned_imports_via_exec(self):
        # Create a mock plugin file inside the sandbox directory
        sandbox_dir = PluginSandboxFinder.SANDBOX_DIR
        os.makedirs(sandbox_dir, exist_ok=True)

        mock_file_path = os.path.join(sandbox_dir, "test_banned_plugin.py")

        # Test blocking 'os'
        plugin_code_os = """
import os
"""
        compiled_os = compile(plugin_code_os, mock_file_path, "exec")
        with pytest.raises(ImportError, match="Sandbox violation: importing 'os' is blocked."):
            exec(compiled_os, {"__file__": mock_file_path, "__name__": "test_banned_plugin"})

        # Test blocking 'subprocess'
        plugin_code_subprocess = """
import subprocess
"""
        compiled_subprocess = compile(plugin_code_subprocess, mock_file_path, "exec")
        with pytest.raises(
            ImportError, match="Sandbox violation: importing 'subprocess' is blocked."
        ):
            exec(
                compiled_subprocess, {"__file__": mock_file_path, "__name__": "test_banned_plugin"}
            )

        # Test blocking 'sys'
        plugin_code_sys = """
import sys
"""
        compiled_sys = compile(plugin_code_sys, mock_file_path, "exec")
        with pytest.raises(ImportError, match="Sandbox violation: importing 'sys' is blocked."):
            exec(compiled_sys, {"__file__": mock_file_path, "__name__": "test_banned_plugin"})

        # Test blocking deep imports
        plugin_code_os_path = """
import os.path
"""
        compiled_os_path = compile(plugin_code_os_path, mock_file_path, "exec")
        with pytest.raises(ImportError, match="Sandbox violation: importing 'os.path' is blocked."):
            exec(compiled_os_path, {"__file__": mock_file_path, "__name__": "test_banned_plugin"})

    def test_allow_banned_imports_from_outside_sandbox_via_exec(self):
        # Create a mock file outside the sandbox
        outside_dir = tempfile.gettempdir()
        mock_file_path = os.path.join(outside_dir, "test_core_module.py")

        plugin_code = """
import os
import sys
import subprocess
assert os is not None
assert sys is not None
assert subprocess is not None
"""
        # This should execute without errors
        compiled_code = compile(plugin_code, mock_file_path, "exec")
        exec(compiled_code, {"__file__": mock_file_path, "__name__": "test_core_module"})

    def test_enable_sandbox_idempotence(self):
        # The setup already called enable_sandbox once
        count_finders = sum(1 for f in sys.meta_path if isinstance(f, PluginSandboxFinder))
        assert count_finders == 1

        # Call it again
        enable_sandbox()
        count_finders = sum(1 for f in sys.meta_path if isinstance(f, PluginSandboxFinder))
        assert count_finders == 1

        # The __import__ should still be wrapped
        assert builtins.__import__.__name__ == "_sandboxed_import"
