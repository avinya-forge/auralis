"""
Auralis - Playlist Editor Tab
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.services.playlist_service import PlaylistGenerator, PlaylistHistory


class PlaylistEditorTab(QWidget):
    """Tab for Stage Playlist Editor (CRUD operations)"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.playlist_generator = PlaylistGenerator()
        self.playlist_history = PlaylistHistory()
        self.current_tracks: List[Dict[str, Any]] = []
        self.current_playlist_name = "New Playlist"
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Playlist Group
        playlist_group = QGroupBox("Playlist Editor")
        playlist_layout = QVBoxLayout(playlist_group)

        # Track List (Drag and Drop)
        self.track_list = QListWidget()
        self.track_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        if self.track_list.model() is not None:
            self.track_list.model().rowsMoved.connect(self.on_rows_moved)  # type: ignore
        playlist_layout.addWidget(self.track_list)

        # Controls Layout
        controls_layout = QHBoxLayout()

        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.on_rename_clicked)
        controls_layout.addWidget(self.rename_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.on_save_clicked)
        controls_layout.addWidget(self.save_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.on_export_clicked)
        controls_layout.addWidget(self.export_btn)

        playlist_layout.addLayout(controls_layout)
        main_layout.addWidget(playlist_group)

    def load_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        """Load tracks into the editor."""
        from PyQt6.QtCore import Qt

        self.current_tracks = tracks.copy()
        self.track_list.clear()
        for track in self.current_tracks:
            metadata = track.get("metadata", {})
            title = metadata.get("title", "Unknown Title")
            artist = metadata.get("artist", "Unknown Artist")
            item = QListWidgetItem(f"{artist} - {title}")
            # Store original path in UserRole to keep track during drag/drop
            item.setData(Qt.ItemDataRole.UserRole, track.get("path"))
            self.track_list.addItem(item)

    def get_ordered_tracks(self) -> List[Dict[str, Any]]:
        """Get the tracks in their current UI order."""
        from PyQt6.QtCore import Qt

        ordered_tracks = []
        path_to_track = {track.get("path"): track for track in self.current_tracks}

        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            if item is not None:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path in path_to_track:
                    ordered_tracks.append(path_to_track[path])
        return ordered_tracks

    def on_rows_moved(self, parent: Any, start: int, end: int, destination: Any, row: int) -> None:
        """Handle internal drag/drop row movement to keep current_tracks in sync."""
        self.current_tracks = self.get_ordered_tracks()

    def on_rename_clicked(self) -> None:
        """Rename the current playlist."""
        new_name, ok = QInputDialog.getText(
            self, "Rename Playlist", "Enter new name:", text=self.current_playlist_name
        )
        if ok and new_name.strip():
            self.current_playlist_name = new_name.strip()
            QMessageBox.information(
                self, "Success", f"Playlist renamed to: {self.current_playlist_name}"
            )

    def on_save_clicked(self) -> None:
        """Save the playlist to history."""
        ordered_tracks = self.get_ordered_tracks()
        if not ordered_tracks:
            QMessageBox.warning(self, "Warning", "Playlist is empty.")
            return

        success = self.playlist_history.add_to_history(self.current_playlist_name, ordered_tracks)
        if success:
            QMessageBox.information(self, "Success", "Playlist saved successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save playlist.")

    def on_export_clicked(self) -> None:
        """Export the playlist to a file."""
        ordered_tracks = self.get_ordered_tracks()
        if not ordered_tracks:
            QMessageBox.warning(self, "Warning", "Playlist is empty.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Playlist",
            self.current_playlist_name + ".m3u8",
            "Playlist Files (*.m3u8);;All Files (*)",
        )

        if filepath:
            success = self.playlist_generator.export_playlist(ordered_tracks, filepath)
            if success:
                QMessageBox.information(self, "Success", f"Playlist exported to {filepath}.")
            else:
                QMessageBox.critical(self, "Error", "Failed to export playlist.")
