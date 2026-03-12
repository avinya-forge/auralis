# Auralis Plugin Sandbox Architecture

This document describes the design and restrictions of the `PluginSandbox` module, intended to prevent unauthorized access by third-party plugins in Auralis.

## Objective
The `PluginSandbox` enforces restrictions dynamically. Subclassing `importlib.abc.MetaPathFinder`, this mechanism restricts `sys.modules` from loading standard libraries that present a security risk, namely native OS interaction and system processes.

## Implementation Details

### Banned Modules
The sandbox explicitly blocks the following standard library modules from being imported within any dynamically loaded plugin namespace (`src/modules/plg/`):

1. `os` - Banned to prevent filesystem tampering and unauthorized file reads/writes outside sandboxed contexts.
2. `subprocess` - Banned to block shell execution and arbitrary command injection.
3. `sys` - Banned to protect the python runtime, interpreter paths, and global application state.

### How It Works

By overriding `find_spec` in the custom `MetaPathFinder`, the sandbox intercepts `import` statements at the loader level. If a sandboxed module attempts to resolve a blocked library (e.g., `import os`), the system intentionally raises an `ImportError` explicitly detailing the sandbox violation.

### Example Architecture

```python
import importlib.abc
import sys

class PluginSandboxFinder(importlib.abc.MetaPathFinder):
    BANNED_MODULES = {'os', 'subprocess', 'sys'}

    def find_spec(self, fullname, path, target=None):
        if fullname in self.BANNED_MODULES:
            raise ImportError(f"Sandbox violation: importing '{fullname}' is blocked.")
        return None  # Delegate to normal loaders

# Injection at startup
sys.meta_path.insert(0, PluginSandboxFinder())
```

This ensures a baseline level of isolation, reducing the risk of malicious third-party plugins impacting user data or system integrity.