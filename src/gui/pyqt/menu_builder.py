from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction, QActionGroup

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMainWindow


def build_menu_bar(main_window: "QMainWindow") -> None:
    """Set up the menu bar for the main window"""
    menu_bar = main_window.menuBar()
    if not menu_bar:
        return

    # View Menu
    view_menu = menu_bar.addMenu("View")
    if not view_menu:
        return

    # Theme Submenu
    theme_menu = view_menu.addMenu("Theme")
    if not theme_menu:
        return

    main_window.theme_action_group = QActionGroup(main_window)
    main_window.theme_action_group.setExclusive(True)

    # Add available themes
    available_themes = main_window.theme_manager.get_available_themes()
    # Ensure Dark and Light are there, otherwise fallback
    if not available_themes:
        # Fallback if no themes loaded (shouldn't happen with resources)
        pass

    for theme_name in sorted(available_themes):
        action = QAction(theme_name, main_window)
        action.setCheckable(True)
        action.triggered.connect(lambda checked, name=theme_name: main_window.change_theme(name))
        theme_menu.addAction(action)
        main_window.theme_action_group.addAction(action)

        # Check if this is the current theme (default Dark)
        if theme_name == "Dark":
            action.setChecked(True)
