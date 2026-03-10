# Auralis Plugin API Documentation

This document outlines the usage, minimum requirements, event hooking patterns, and provides examples for the `PluginInterface` to help developers write extensions for Auralis.

## Minimum Requirements

Every plugin in Auralis must inherit from `PluginInterface` (typically located in `src/plugins/plugin_interface.py`) and implement the following base properties and methods:

- `name`: A string property indicating the unique name of the plugin.
- `version`: A string property indicating the semantic version of the plugin (e.g., `1.0.0`).
- `init()`: The initialization method called by the `PluginLoader` when the plugin is activated.

## Event Hooking Patterns

Auralis uses a robust event hooking system allowing plugins to react to various lifecycle stages or data events. The primary hooks include:

- `on_scan_start(directory: str)`: Called before a directory scan begins.
- `on_track_played(track_id: str)`: Called when a track starts playing.
- `on_metadata_updated(track_id: str, new_metadata: dict)`: Called when track metadata is modified.

To hook into these events, simply define the methods in your plugin class. The internal Event Bus will dynamically register and trigger them.

## Hello World Example

Below is a minimal 'Hello World' plugin that demonstrates how to implement the `PluginInterface` and log an initialization message.

```python
from src.plugins.plugin_interface import PluginInterface
import logging

class HelloWorldPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "HelloWorld"

    @property
    def version(self) -> str:
        return "1.0.0"

    def init(self) -> None:
        logging.info("HelloWorld plugin has been initialized successfully!")
        print(f"[{self.name} v{self.version}] Loading complete.")

    def on_track_played(self, track_id: str) -> None:
        logging.info(f"HelloWorld plugin says: Now playing track {track_id}")
```
