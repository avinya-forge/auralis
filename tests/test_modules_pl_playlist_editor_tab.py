"""
Tests for Playlist Editor Tab
"""

import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication

from src.modules.pl.playlist_editor_tab import PlaylistEditorTab

# Ensure QApplication is created
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestPlaylistEditorTab(unittest.TestCase):
    """Test suite for PlaylistEditorTab"""

    @patch("src.modules.pl.playlist_editor_tab.QListWidget")
    def setUp(self, mock_list: MagicMock) -> None:
        """Set up the test environment"""
        self.mock_list = mock_list
        self.tab = PlaylistEditorTab()
        self.sample_tracks = [
            {"path": "/path/to/track1.mp3", "metadata": {"title": "Track 1", "artist": "Artist A"}},
            {"path": "/path/to/track2.mp3", "metadata": {"title": "Track 2", "artist": "Artist B"}},
        ]

    def test_playlist_editor_init(self) -> None:
        """Test initialization of the tab"""
        self.assertEqual(self.tab.current_playlist_name, "New Playlist")

    def test_load_tracks(self) -> None:
        """Test loading tracks into the list"""
        # Actually in headless, QListWidget methods like count() might not work correctly,
        # but the logic loads into `current_tracks`
        self.tab.load_tracks(self.sample_tracks)
        self.assertEqual(len(self.tab.current_tracks), 2)
        # We can also verify QListWidget logic via mocking if needed
        # But just checking the tracks are stored is often enough

    def test_get_ordered_tracks(self) -> None:
        """Test retrieving the current order of tracks"""
        self.tab.load_tracks(self.sample_tracks)

        # Mocking the QListWidget behaviour
        mock_item1 = MagicMock()
        mock_item1.data.return_value = "/path/to/track1.mp3"
        mock_item2 = MagicMock()
        mock_item2.data.return_value = "/path/to/track2.mp3"

        self.tab.track_list.count = MagicMock(return_value=2)  # type: ignore
        self.tab.track_list.item = MagicMock(side_effect=[mock_item1, mock_item2])  # type: ignore

        ordered = self.tab.get_ordered_tracks()
        self.assertEqual(len(ordered), 2)
        self.assertEqual(ordered[0]["path"], "/path/to/track1.mp3")

    @patch("src.modules.pl.playlist_editor_tab.QInputDialog.getText")
    @patch("src.modules.pl.playlist_editor_tab.QMessageBox.information")
    def test_rename_playlist(self, mock_info: MagicMock, mock_get_text: MagicMock) -> None:
        """Test renaming the playlist"""
        mock_get_text.return_value = ("Awesome Mix", True)

        self.tab.on_rename_clicked()

        self.assertEqual(self.tab.current_playlist_name, "Awesome Mix")
        mock_info.assert_called_once()

    @patch("src.modules.pl.playlist_editor_tab.QMessageBox.information")
    def test_save_playlist_success(self, mock_info: MagicMock) -> None:
        """Test saving playlist successfully"""
        self.tab.load_tracks(self.sample_tracks)

        # Mock ordered tracks retrieval
        self.tab.get_ordered_tracks = MagicMock(return_value=self.sample_tracks)  # type: ignore
        self.tab.playlist_history.add_to_history = MagicMock(return_value=True)  # type: ignore

        self.tab.on_save_clicked()

        self.tab.playlist_history.add_to_history.assert_called_once_with(
            "New Playlist", self.sample_tracks
        )
        mock_info.assert_called_once()

    @patch("src.modules.pl.playlist_editor_tab.QMessageBox.warning")
    def test_save_empty_playlist(self, mock_warning: MagicMock) -> None:
        """Test saving empty playlist shows warning"""
        self.tab.get_ordered_tracks = MagicMock(return_value=[])  # type: ignore
        self.tab.on_save_clicked()

        mock_warning.assert_called_once()

    @patch("src.modules.pl.playlist_editor_tab.QFileDialog.getSaveFileName")
    @patch("src.modules.pl.playlist_editor_tab.QMessageBox.information")
    def test_export_playlist_success(self, mock_info: MagicMock, mock_get_file: MagicMock) -> None:
        """Test exporting playlist successfully"""
        self.tab.load_tracks(self.sample_tracks)
        self.tab.get_ordered_tracks = MagicMock(return_value=self.sample_tracks)  # type: ignore
        mock_get_file.return_value = ("/path/to/output.m3u8", "Playlist Files (*.m3u8)")
        self.tab.playlist_generator.export_playlist = MagicMock(return_value=True)  # type: ignore

        self.tab.on_export_clicked()

        self.tab.playlist_generator.export_playlist.assert_called_once_with(
            self.sample_tracks, "/path/to/output.m3u8"
        )
        mock_info.assert_called_once()
