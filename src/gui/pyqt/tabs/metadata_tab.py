"""
Stage 3: Metadata Tab
"""

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.config import get_config
from src.utils.image_loader import ImageLoader


class MetadataTab(QWidget):
    """Tab for Stage 3: Metadata"""

    update_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.image_loader = ImageLoader()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI"""
        main_layout = QHBoxLayout(self)

        # Left Column: Options
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 1)

        # Metadata sources
        metadata_group = QGroupBox("Metadata Sources")
        metadata_layout = QVBoxLayout(metadata_group)

        # MusicBrainz / AcoustID
        self.mb_check = QCheckBox("MusicBrainz / AcoustID")
        self.mb_check.setChecked(bool(get_config("USE_MUSICBRAINZ", True)))
        metadata_layout.addWidget(self.mb_check)

        # Discogs
        self.discogs_check = QCheckBox("Discogs")
        self.discogs_check.setChecked(bool(get_config("USE_DISCOGS", True)))
        metadata_layout.addWidget(self.discogs_check)

        left_layout.addWidget(metadata_group)

        # Additional Metadata options
        enrichment_group = QGroupBox("Additional Metadata")
        enrichment_layout = QVBoxLayout(enrichment_group)

        # Fetch lyrics
        self.lyrics_check = QCheckBox("Fetch and Embed Lyrics")
        self.lyrics_check.setChecked(bool(get_config("FETCH_LYRICS", True)))
        self.lyrics_check.setToolTip(
            "Fetch lyrics from online sources and embed them in the audio files"
        )
        enrichment_layout.addWidget(self.lyrics_check)

        # Fetch Cover Art
        self.cover_art_check = QCheckBox("Fetch and Embed Cover Art")
        self.cover_art_check.setChecked(bool(get_config("FETCH_COVER_ART", True)))
        self.cover_art_check.setToolTip(
            "Fetch album artwork from online sources (Spotify, Last.fm) and embed it in the audio files"
        )
        enrichment_layout.addWidget(self.cover_art_check)

        # Analyze Audio
        self.analyze_check = QCheckBox("Analyze Audio (BPM, Key, Mood)")
        self.analyze_check.setChecked(bool(get_config("ANALYZE_AUDIO", False)))
        self.analyze_check.setToolTip(
            "Analyze audio files to detect BPM, Key, and Mood (Computationally Intensive)"
        )
        enrichment_layout.addWidget(self.analyze_check)

        enrichment_info = QLabel(
            "Lyrics and Cover Art will be embedded in the audio files so they can be "
            "displayed in music players."
        )
        enrichment_info.setWordWrap(True)
        enrichment_layout.addWidget(enrichment_info)

        left_layout.addWidget(enrichment_group)

        # Update button
        update_btn = QPushButton("Update Metadata")
        update_btn.clicked.connect(self.update_requested.emit)
        left_layout.addWidget(update_btn)
        left_layout.addStretch()

        # Right Column: Preview
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 1)

        # Cover Art Preview
        preview_group = QGroupBox("Cover Art Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.cover_art_label = QLabel("No Image")
        self.cover_art_label.setFixedSize(200, 200)
        self.cover_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_art_label.setStyleSheet("border: 1px solid gray; background-color: #333;")
        preview_layout.addWidget(self.cover_art_label, 0, Qt.AlignmentFlag.AlignCenter)

        # Analysis Results
        self.bpm_label = QLabel("BPM: -")
        self.key_label = QLabel("Key: -")
        self.mood_label = QLabel("Mood: -")
        preview_layout.addWidget(self.bpm_label)
        preview_layout.addWidget(self.key_label)
        preview_layout.addWidget(self.mood_label)
        preview_layout.addStretch()

        right_layout.addWidget(preview_group)
        right_layout.addStretch()

    def get_options(self) -> Dict[str, Any]:
        """Get options relevant to this tab"""
        return {
            "use_musicbrainz": self.mb_check.isChecked(),
            "use_discogs": self.discogs_check.isChecked(),
            "fetch_lyrics": self.lyrics_check.isChecked(),
            "fetch_cover_art": self.cover_art_check.isChecked(),
            "analyze_audio": self.analyze_check.isChecked(),
        }

    def set_cover_art(self, path_or_url: Optional[str]) -> None:
        """Set the cover art preview image"""
        if not path_or_url:
            self.cover_art_label.setText("No Image")
            self.cover_art_label.setPixmap(QPixmap())
            return

        self.cover_art_label.setText("Loading...")
        self.image_loader.load_image(path_or_url, self._on_image_loaded)

    def _on_image_loaded(self, image: Optional[QImage]) -> None:
        """Callback when image is loaded"""
        if image and not image.isNull():
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(
                self.cover_art_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.cover_art_label.setPixmap(scaled_pixmap)
            self.cover_art_label.setText("")
        else:
            self.cover_art_label.setText("Load Failed")

    def update_analysis_display(
        self, bpm: Optional[float], key: Optional[str], mood: Optional[str]
    ) -> None:
        """Update analysis results display"""
        self.bpm_label.setText(f"BPM: {int(bpm) if bpm else '-'}")
        self.key_label.setText(f"Key: {key if key else '-'}")
        self.mood_label.setText(f"Mood: {mood if mood else '-'}")
