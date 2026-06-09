import pytest
import sys
import builtins
import os
from src.modules.plg.plugin_sandbox import enable_sandbox, _original_import


def test_plugin_sandbox_prevents_os():
    enable_sandbox()
    sandbox_file = os.path.abspath("src/modules/plg/test_banned_plugin.py")
    with open(sandbox_file, "w") as f:
        f.write("import os\n")
    try:
        with pytest.raises(ImportError):
            with open(sandbox_file, "r") as f:
                code = compile(f.read(), sandbox_file, "exec")
                exec(code, {})
        safe_file = os.path.abspath("src/modules/plg/test_safe_plugin.py")
        with open(safe_file, "w") as f:
            f.write("import math\n")
        with open(safe_file, "r") as f:
            code = compile(f.read(), safe_file, "exec")
            exec(code, {})
    finally:
        if os.path.exists(sandbox_file):
            os.remove(sandbox_file)
        if os.path.exists(safe_file):
            os.remove(safe_file)
        if _original_import is not None:
            builtins.__import__ = _original_import
            sys.meta_path = [p for p in sys.meta_path if type(p).__name__ != "PluginSandboxFinder"]
