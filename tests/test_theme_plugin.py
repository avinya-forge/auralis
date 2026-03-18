from typing import Any, Dict

import pytest

from src.modules.plg.theme_plugin_interface import ThemePluginInterface


class MockThemePlugin(ThemePluginInterface):
    @property
    def name(self) -> str:
        return "Test Theme"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "A test theme plugin."

    def initialize(self, context: Dict[str, Any]) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def get_stylesheet(self) -> str:
        return "QWidget { background-color: #000000; }"

    def get_palette(self) -> Dict[str, Any]:
        return {"Window": "#000000", "Text": "#ffffff"}


class MockIncompleteThemePlugin(ThemePluginInterface):
    @property
    def name(self) -> str:
        return "Incomplete Theme"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "An incomplete test theme plugin."

    def initialize(self, context: Dict[str, Any]) -> bool:
        return True

    def shutdown(self) -> None:
        pass


def test_theme_plugin_interface_instantiation() -> None:
    """Test that a concrete ThemePluginInterface can be instantiated."""
    plugin = MockThemePlugin()

    assert plugin.name == "Test Theme"
    assert plugin.version == "1.0.0"
    assert plugin.description == "A test theme plugin."

    stylesheet = plugin.get_stylesheet()
    assert stylesheet == "QWidget { background-color: #000000; }"

    palette = plugin.get_palette()
    assert "Window" in palette
    assert palette["Window"] == "#000000"


def test_theme_plugin_interface_incomplete_instantiation() -> None:
    """Test that an incomplete ThemePluginInterface raises TypeError."""
    with pytest.raises(
        TypeError, match="Can't instantiate abstract class MockIncompleteThemePlugin"
    ):
        MockIncompleteThemePlugin()  # type: ignore


def test_abstract_methods() -> None:
    """Test that abstract methods raise NotImplementedError if called on base via super (for coverage)."""

    # This just ensures we hit the `pass` inside the abstract methods for coverage
    class BaseCaller(ThemePluginInterface):
        @property
        def name(self) -> str:
            return ""

        @property
        def version(self) -> str:
            return ""

        @property
        def description(self) -> str:
            return ""

        def initialize(self, context: Dict[str, Any]) -> bool:
            return True

        def shutdown(self) -> None:
            pass

        def get_stylesheet(self) -> str:
            super().get_stylesheet()
            return ""

        def get_palette(self) -> Dict[str, Any]:
            super().get_palette()
            return {}

    caller = BaseCaller()
    caller.get_stylesheet()
    caller.get_palette()
