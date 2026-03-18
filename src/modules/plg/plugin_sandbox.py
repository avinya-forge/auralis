"""
Auralis Plugin Sandbox Module

Provides a custom MetaPathFinder and an __import__ hook to restrict
dangerous imports from dynamically loaded plugins inside src/modules/plg/.
"""

import builtins
import importlib.abc
import inspect
import os
import sys
import types
from typing import Any, Callable, Mapping, Optional, Sequence


class PluginSandboxFinder(importlib.abc.MetaPathFinder):
    """
    A sandbox finder that blocks banned modules from being imported
    if the caller originates from the plugins directory.
    """

    BANNED_MODULES = {"os", "subprocess", "sys"}
    SANDBOX_DIR = os.path.abspath(os.path.join("src", "modules", "plg"))
    IMPORTLIB_DIR = os.path.dirname(importlib.__file__)

    def find_spec(
        self, fullname: str, path: Optional[Any], target: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Intercept module loading to prevent banned modules from being imported
        by sandboxed plugins.

        Args:
            fullname: The fully qualified name of the module.
            path: The module path.
            target: Target module object (optional).

        Returns:
            None if the import is allowed to proceed, otherwise raises ImportError.

        Raises:
            ImportError: If a sandboxed module attempts to import a banned module.
        """
        base_module = fullname.split(".")[0]

        if base_module in self.BANNED_MODULES:
            if _is_sandboxed_caller():
                raise ImportError(f"Sandbox violation: importing '{fullname}' is blocked.")

        return None


def _is_sandboxed_caller() -> bool:
    """
    Analyzes the call stack to determine if the import originates from
    within the sandbox directory (src/modules/plg/).

    Returns:
        bool: True if the caller is sandboxed, False otherwise.
    """
    stack = inspect.stack()
    sandbox_dir = PluginSandboxFinder.SANDBOX_DIR
    importlib_dir = PluginSandboxFinder.IMPORTLIB_DIR

    for frame_info in stack:
        filename = frame_info.filename

        # Skip frames that are internal to Python's importlib machinery
        if filename.startswith(importlib_dir) or filename == "<frozen importlib._bootstrap>":
            continue

        # Skip the sandbox itself
        if filename == os.path.abspath(__file__):
            continue

        # Check if the immediate external caller is inside the sandbox
        abs_filename = os.path.abspath(filename)
        if abs_filename.startswith(sandbox_dir):
            return True

        # Stop at the first non-importlib, non-sandbox-internal frame
        break

    return False


# Keep a reference to the original __import__ function
_original_import: Optional[
    Callable[
        [
            str,
            Optional[Mapping[str, object]],
            Optional[Mapping[str, object]],
            Optional[Sequence[str]],
            int,
        ],
        types.ModuleType,
    ]
] = None


def _sandboxed_import(
    name: str,
    globals: Optional[Mapping[str, object]] = None,
    locals: Optional[Mapping[str, object]] = None,
    fromlist: Optional[Sequence[str]] = (),
    level: int = 0,
) -> types.ModuleType:
    """
    A wrapper around builtins.__import__ to intercept cached module imports.
    """
    base_module = name.split(".")[0]

    if base_module in PluginSandboxFinder.BANNED_MODULES:
        if _is_sandboxed_caller():
            raise ImportError(f"Sandbox violation: importing '{name}' is blocked.")

    # We know _original_import is not None here because it's set in enable_sandbox
    assert _original_import is not None
    return _original_import(name, globals, locals, fromlist, level)


def enable_sandbox() -> None:
    """
    Enables the sandbox globally by injecting the MetaPathFinder into
    sys.meta_path and wrapping builtins.__import__.
    """
    global _original_import

    # Register the MetaPathFinder
    if not any(isinstance(finder, PluginSandboxFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, PluginSandboxFinder())

    # Wrap builtins.__import__ to intercept cached modules (like sys and os)
    if builtins.__import__ is not _sandboxed_import:
        _original_import = builtins.__import__
        builtins.__import__ = _sandboxed_import
