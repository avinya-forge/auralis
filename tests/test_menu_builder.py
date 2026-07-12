from unittest.mock import MagicMock

from src.gui.pyqt.menu_builder import build_menu_bar


def test_build_menu_bar_success():
    """Test successful menu bar creation."""
    mock_window = MagicMock()
    mock_menu_bar = MagicMock()
    mock_window.menuBar.return_value = mock_menu_bar

    mock_view_menu = MagicMock()
    mock_menu_bar.addMenu.return_value = mock_view_menu

    mock_theme_menu = MagicMock()
    mock_view_menu.addMenu.return_value = mock_theme_menu

    mock_window.theme_manager.get_available_themes.return_value = ["Dark", "Light"]

    build_menu_bar(mock_window)

    # Assertions
    mock_window.menuBar.assert_called_once()
    mock_menu_bar.addMenu.assert_called_with("View")
    mock_view_menu.addMenu.assert_called_with("Theme")
    mock_window.theme_manager.get_available_themes.assert_called_once()
    assert mock_theme_menu.addAction.call_count == 2


def test_build_menu_bar_no_themes():
    """Test menu bar creation when no themes are available."""
    mock_window = MagicMock()
    mock_menu_bar = MagicMock()
    mock_window.menuBar.return_value = mock_menu_bar

    mock_view_menu = MagicMock()
    mock_menu_bar.addMenu.return_value = mock_view_menu

    mock_theme_menu = MagicMock()
    mock_view_menu.addMenu.return_value = mock_theme_menu

    mock_window.theme_manager.get_available_themes.return_value = []

    build_menu_bar(mock_window)

    # Theme menu created, but no actions added
    assert mock_theme_menu.addAction.call_count == 2


def test_build_menu_bar_no_menu_bar():
    """Test early return when no menu bar is available."""
    mock_window = MagicMock()
    mock_window.menuBar.return_value = None

    build_menu_bar(mock_window)
    mock_window.theme_manager.get_available_themes.assert_not_called()
