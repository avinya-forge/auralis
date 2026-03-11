"""
Playlist Editor Tab implementation.
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.services.playlist_service import PlaylistGenerator as PlaylistService


class PlaylistEditorTab(QWidget):
    """UI tab for managing playlists (CRUD operations)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.playlist_service = PlaylistService()
        self.current_playlist_name: Optional[str] = None
        self.current_playlist: List[Dict[str, Any]] = []
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        # Controls Layout
        controls_layout = QHBoxLayout()

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_playlist)
        controls_layout.addWidget(self.btn_save)

        self.btn_rename = QPushButton("Rename")
        self.btn_rename.clicked.connect(self.rename_playlist)
        controls_layout.addWidget(self.btn_rename)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.export_playlist)
        controls_layout.addWidget(self.btn_export)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Track List
        self.track_list = QListWidget()
        self.track_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        layout.addWidget(self.track_list)

    def save_playlist(self) -> None:
        """Save the current playlist, prompting for a name if necessary."""
        if not self.current_playlist_name:
            name, ok = QInputDialog.getText(self, "Save Playlist", "Playlist Name:")
            if ok and name:
                self.current_playlist_name = name
            else:
                return

        # Sync visual list order back to internal state if items were reordered
        reordered_playlist = []
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            # Find the dict based on path stored in data
            if item is not None:
                path = item.data(100)
            else:
                continue
            for track in self.current_playlist:
                if track.get("path") == path:
                    reordered_playlist.append(track)
                    break
        self.current_playlist = reordered_playlist

        success = self.playlist_service.save_playlist(
            self.current_playlist_name, self.current_playlist
        )
        if success:
            QMessageBox.information(
                self, "Success", f"Playlist '{self.current_playlist_name}' saved."
            )
        else:
            QMessageBox.warning(self, "Error", "Failed to save playlist.")

    def rename_playlist(self) -> None:
        """Rename the current playlist."""
        if not self.current_playlist_name:
            QMessageBox.warning(self, "Warning", "No active playlist to rename.")
            return

        new_name, ok = QInputDialog.getText(
            self, "Rename Playlist", "New Name:", text=self.current_playlist_name
        )
        if ok and new_name and new_name != self.current_playlist_name:
            success = self.playlist_service.rename_playlist(
                self.current_playlist_name, new_name
            )
            if success:
                self.current_playlist_name = new_name
                QMessageBox.information(
                    self, "Success", f"Playlist renamed to '{new_name}'."
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to rename playlist.")

    def export_playlist(self) -> None:
        """Export the current playlist to a file."""
        if not self.current_playlist:
            QMessageBox.warning(self, "Warning", "No tracks to export.")
            return

        default_name = f"{self.current_playlist_name or 'playlist'}.m3u8"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Playlist", default_name, "Playlist Files (*.m3u8)"
        )
        if filepath:
            success = self.playlist_service.export_playlist(self.current_playlist, filepath)
            if success:
                QMessageBox.information(self, "Success", "Playlist exported successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to export playlist.")
