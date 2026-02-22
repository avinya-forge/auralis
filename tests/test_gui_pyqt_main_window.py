"""
Unit tests for PyQt6 MainWindow
"""

import unittest
from unittest.mock import MagicMock, patch

from src.gui.pyqt.main_window import MainWindow


class TestMainWindow(unittest.TestCase):
    """Test cases for PyQt6 MainWindow"""

    @patch("src.gui.pyqt.main_window.MusicScanner")
    @patch("src.gui.pyqt.main_window.MusicOrganizer")
    @patch("src.gui.pyqt.main_window.SystemMonitor")
    @patch("src.gui.pyqt.main_window.ThemeManager")
    @patch("src.gui.pyqt.main_window.ScanTab")
    @patch("src.gui.pyqt.main_window.OrganizeTab")
    @patch("src.gui.pyqt.main_window.MetadataTab")
    @patch("src.gui.pyqt.main_window.QTimer")
    @patch("src.gui.pyqt.main_window.QApplication")
    def test_init(
        self,
        mock_app_cls,
        mock_timer,
        mock_meta_tab,
        mock_org_tab,
        mock_scan_tab,
        mock_tm_cls,
        mock_sys,
        mock_mo,
        mock_ms,
    ):
        """Test initialization of MainWindow"""
        # Setup ThemeManager mock
        mock_tm_instance = MagicMock()
        mock_tm_instance.get_available_themes.return_value = ["Dark", "Light"]
        mock_tm_cls.return_value = mock_tm_instance

        # Setup App instance mock
        mock_app_instance = MagicMock()
        mock_app_cls.instance.return_value = mock_app_instance

        # Create window
        window = MainWindow()

        # Verify initialization
        self.assertTrue(window.windowTitle().startswith("Auralis"))

        # Verify components initialized
        mock_ms.assert_called()
        mock_mo.assert_called()
        mock_sys.assert_called()
        mock_tm_cls.assert_called()

        # Verify tabs created
        mock_scan_tab.assert_called()
        mock_org_tab.assert_called()
        mock_meta_tab.assert_called()

        # Verify default theme applied
        # Note: MainWindow calls self.change_theme("Dark") in init
        # which calls QApplication.instance()
        mock_tm_instance.apply_theme.assert_called()

        # Verify Status Bar components
        self.assertTrue(hasattr(window, "status_bar"))
        self.assertTrue(hasattr(window, "progress_bar"))
        self.assertTrue(hasattr(window, "stage_label"))

        # Verify Menu Bar
        self.assertTrue(hasattr(window, "theme_action_group"))
        # We mocked get_available_themes to return 2 themes
        # So we should have actions added
        # Since we can't easily inspect QMenu in mock, we assume it worked if no error

    @patch("src.gui.pyqt.main_window.MusicScanner")
    @patch("src.gui.pyqt.main_window.MusicOrganizer")
    @patch("src.gui.pyqt.main_window.SystemMonitor")
    @patch("src.gui.pyqt.main_window.ThemeManager")
    @patch("src.gui.pyqt.main_window.ScanTab")
    @patch("src.gui.pyqt.main_window.OrganizeTab")
    @patch("src.gui.pyqt.main_window.MetadataTab")
    @patch("src.gui.pyqt.main_window.QTimer")
    @patch("src.gui.pyqt.main_window.QApplication")
    def test_change_theme(
        self,
        mock_app_cls,
        mock_timer,
        mock_meta_tab,
        mock_org_tab,
        mock_scan_tab,
        mock_tm_cls,
        mock_sys,
        mock_mo,
        mock_ms,
    ):
        """Test changing theme"""
        mock_tm_instance = MagicMock()
        mock_tm_instance.get_available_themes.return_value = ["Dark", "Light"]
        mock_tm_cls.return_value = mock_tm_instance

        mock_app_instance = MagicMock()
        mock_app_cls.instance.return_value = mock_app_instance

        window = MainWindow()

        # Change theme
        window.change_theme("Light")

        # Verify ThemeManager called
        mock_tm_instance.apply_theme.assert_called_with(mock_app_instance, "Light")

    @patch("src.gui.pyqt.main_window.MusicScanner")
    @patch("src.gui.pyqt.main_window.MusicOrganizer")
    @patch("src.gui.pyqt.main_window.SystemMonitor")
    @patch("src.gui.pyqt.main_window.ThemeManager")
    @patch("src.gui.pyqt.main_window.ScanTab")
    @patch("src.gui.pyqt.main_window.OrganizeTab")
    @patch("src.gui.pyqt.main_window.MetadataTab")
    @patch("src.gui.pyqt.main_window.QTimer")
    @patch("src.gui.pyqt.main_window.QApplication")
    def test_status_bar_updates(
        self,
        mock_app_cls,
        mock_timer,
        mock_meta_tab,
        mock_org_tab,
        mock_scan_tab,
        mock_tm_cls,
        mock_sys,
        mock_mo,
        mock_ms,
    ):
        """Test status bar update methods"""
        mock_tm_instance = MagicMock()
        mock_tm_instance.get_available_themes.return_value = ["Dark"]
        mock_tm_cls.return_value = mock_tm_instance

        window = MainWindow()

        # Mock widgets
        window.progress_bar = MagicMock()
        window.stage_label = MagicMock()
        window.current_file_label = MagicMock()

        # Test update_progress
        window.update_progress(1, 50, 100)
        window.progress_bar.setValue.assert_called_with(50)
        window.stage_label.setText.assert_called_with("1: 50/100 (50%)")

        # Test update_status
        window.update_status("Testing")
        window.stage_label.setText.assert_called_with("Testing")

        # Test update_current_file
        window.update_current_file("song.mp3")
        window.current_file_label.setText.assert_called_with("song.mp3")

        # Test start_scan shows progress bar
        window.scan_tab.validate_source_directories.return_value = True
        window.prepare_worker_thread = MagicMock(return_value=True)
        window.worker_thread = MagicMock()

        window.start_scan()
        window.progress_bar.setVisible.assert_called_with(True)
        window.progress_bar.setValue.assert_called_with(0)
