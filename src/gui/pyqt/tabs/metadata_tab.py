"""
Stage 3: Metadata Tab
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget

from src.utils.config import get_config


class MetadataTab(QWidget):
    """Tab for Stage 3: Metadata"""

    update_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Metadata sources
        metadata_group = QGroupBox("Metadata Sources")
        metadata_layout = QVBoxLayout(metadata_group)

        # MusicBrainz / AcoustID
        self.mb_check = QCheckBox("MusicBrainz / AcoustID")
        self.mb_check.setChecked(get_config("USE_MUSICBRAINZ", True))
        metadata_layout.addWidget(self.mb_check)

        # Discogs
        self.discogs_check = QCheckBox("Discogs")
        self.discogs_check.setChecked(get_config("USE_DISCOGS", True))
        metadata_layout.addWidget(self.discogs_check)

        layout.addWidget(metadata_group)

        # Lyrics options
        lyrics_group = QGroupBox("Lyrics")
        lyrics_layout = QVBoxLayout(lyrics_group)

        # Fetch lyrics
        self.lyrics_check = QCheckBox("Fetch and Embed Lyrics")
        self.lyrics_check.setChecked(get_config("FETCH_LYRICS", True))
        self.lyrics_check.setToolTip(
            "Fetch lyrics from online sources and embed them in the audio files"
        )
        lyrics_layout.addWidget(self.lyrics_check)

        lyrics_info = QLabel(
            "Lyrics will be embedded in the audio files so they can be "
            "displayed in music players like Apple Music."
        )
        lyrics_info.setWordWrap(True)
        lyrics_layout.addWidget(lyrics_info)

        layout.addWidget(lyrics_group)

        # Update button
        update_btn = QPushButton("Update Metadata")
        update_btn.clicked.connect(self.update_requested.emit)
        layout.addWidget(update_btn)

    def get_options(self):
        """Get options relevant to this tab"""
        return {
            "use_musicbrainz": self.mb_check.isChecked(),
            "use_discogs": self.discogs_check.isChecked(),
            "fetch_lyrics": self.lyrics_check.isChecked(),
        }
