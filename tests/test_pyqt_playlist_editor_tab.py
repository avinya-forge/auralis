"""
Unit tests for PyQt6 PlaylistEditorTab
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QAbstractItemView


class TestPyQtPlaylistEditorTab(unittest.TestCase):
    """Test cases for PyQt6 PlaylistEditorTab"""

    def setUp(self):
        # We temporarily unmock QWidget in PyQt6.QtWidgets to let python parse the module normally
        self.modules_patcher = patch.dict(sys.modules)
        self.modules_patcher.start()

        if "src.modules.pl.playlist_editor_tab" in sys.modules:
            del sys.modules["src.modules.pl.playlist_editor_tab"]

        # Mock PlaylistService to avoid DB / disk interactions
        self.service_patcher = patch("src.modules.pl.playlist_editor_tab.PlaylistService")
        self.mock_service_class = self.service_patcher.start()
        self.mock_service = MagicMock()
        self.mock_service_class.return_value = self.mock_service

        from src.modules.pl.playlist_editor_tab import PlaylistEditorTab

        self.PlaylistEditorTab = PlaylistEditorTab

    def tearDown(self):
        self.service_patcher.stop()
        self.modules_patcher.stop()

    def test_init_ui(self):
        """Test PlaylistEditorTab initialization"""
        with patch("src.modules.pl.playlist_editor_tab.QListWidget") as mock_list_widget:
            mock_list = MagicMock()
            mock_list_widget.return_value = mock_list

            tab = self.PlaylistEditorTab()

            # Verify buttons exist
            self.assertTrue(hasattr(tab, "btn_save"))
            self.assertTrue(hasattr(tab, "btn_rename"))
            self.assertTrue(hasattr(tab, "btn_export"))

            # Verify ListWidget configured correctly
            self.assertTrue(hasattr(tab, "track_list"))
            mock_list.setDragDropMode.assert_called_with(
                QAbstractItemView.DragDropMode.InternalMove
            )

    @patch("src.modules.pl.playlist_editor_tab.QInputDialog")
    @patch("src.modules.pl.playlist_editor_tab.QMessageBox")
    def test_save_playlist(self, mock_msgbox, mock_input_dialog):
        """Test saving a playlist"""
        tab = self.PlaylistEditorTab()

        # Simulate clicking save when no playlist name exists
        mock_input_dialog.getText.return_value = ("My Playlist", True)
        self.mock_service.save_playlist.return_value = True

        tab.save_playlist()

        mock_input_dialog.getText.assert_called_once()
        self.mock_service.save_playlist.assert_called_with("My Playlist", [])
        mock_msgbox.information.assert_called_once()

        # Test error handling
        self.mock_service.save_playlist.return_value = False
        tab.current_playlist_name = "Existing Playlist"

        tab.save_playlist()

        # Input dialog shouldn't be called again
        mock_input_dialog.getText.assert_called_once()
        mock_msgbox.warning.assert_called_once()

    @patch("src.modules.pl.playlist_editor_tab.QInputDialog")
    @patch("src.modules.pl.playlist_editor_tab.QMessageBox")
    def test_rename_playlist(self, mock_msgbox, mock_input_dialog):
        """Test renaming a playlist"""
        tab = self.PlaylistEditorTab()

        # Try renaming without a playlist
        tab.rename_playlist()
        mock_msgbox.warning.assert_called_with(
            tab, "Warning", "No active playlist to rename."
        )

        mock_msgbox.reset_mock()

        # Setup an existing playlist
        tab.current_playlist_name = "Old Name"
        mock_input_dialog.getText.return_value = ("New Name", True)
        self.mock_service.rename_playlist.return_value = True

        tab.rename_playlist()

        self.mock_service.rename_playlist.assert_called_with("Old Name", "New Name")
        self.assertEqual(tab.current_playlist_name, "New Name")
        mock_msgbox.information.assert_called_once()

    @patch("src.modules.pl.playlist_editor_tab.QFileDialog")
    @patch("src.modules.pl.playlist_editor_tab.QMessageBox")
    def test_export_m3u8(self, mock_msgbox, mock_file_dialog):
        """Test exporting a playlist"""
        tab = self.PlaylistEditorTab()

        # Try exporting empty playlist
        tab.export_playlist()
        mock_msgbox.warning.assert_called_with(tab, "Warning", "No tracks to export.")

        mock_msgbox.reset_mock()

        # Setup playlist
        tab.current_playlist = [{"path": "/path/to/song.mp3"}]
        tab.current_playlist_name = "MyList"

        mock_file_dialog.getSaveFileName.return_value = ("/out/MyList.m3u8", "Filter")
        self.mock_service.export_playlist.return_value = True

        tab.export_playlist()

        mock_file_dialog.getSaveFileName.assert_called_with(
            tab, "Export Playlist", "MyList.m3u8", "Playlist Files (*.m3u8)"
        )
        self.mock_service.export_playlist.assert_called_with(
            tab.current_playlist, "/out/MyList.m3u8"
        )
        mock_msgbox.information.assert_called_once()


if __name__ == "__main__":
    unittest.main()
