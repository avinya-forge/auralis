"""
Stage 2: Organize Tab
"""

import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.config import get_config


class OrganizeTab(QWidget):
    """Tab for Stage 2: Organize"""

    dry_run_requested = pyqtSignal()
    organize_requested = pyqtSignal()

    def __init__(self, parent=None, default_output_dir=""):
        super().__init__(parent)
        self.default_output_dir = default_output_dir
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Destination directory selection
        dest_group = QGroupBox("Destination Directory")
        dest_layout = QVBoxLayout(dest_group)

        self.dest_label = QLabel("No destination selected")
        if self.default_output_dir and os.path.exists(os.path.dirname(self.default_output_dir)):
            self.dest_label.setText(self.default_output_dir)

        dest_layout.addWidget(self.dest_label)

        dest_btn = QPushButton("Select Destination")
        dest_btn.clicked.connect(self.select_destination)
        dest_layout.addWidget(dest_btn)

        layout.addWidget(dest_group)

        # Organization options
        org_group = QGroupBox("Organization Options")
        org_layout = QVBoxLayout(org_group)

        # Language-based organization
        self.lang_org_check = QCheckBox("Organize by Language")
        self.lang_org_check.setChecked(get_config("ORGANIZE_BY_LANGUAGE", True))
        org_layout.addWidget(self.lang_org_check)

        # Audio language detection checkbox
        self.audio_lang_detect_check = QCheckBox("Use Audio Content for Language Detection")
        self.audio_lang_detect_check.setChecked(True)
        self.audio_lang_detect_check.setEnabled(self.lang_org_check.isChecked())
        # Connect language organization checkbox to enable/disable audio detection
        self.lang_org_check.toggled.connect(self.audio_lang_detect_check.setEnabled)
        org_layout.addWidget(self.audio_lang_detect_check)

        # Audio similarity detection
        self.audio_similarity_check = QCheckBox("Detect Similar Audio Content (Find Duplicates)")
        self.audio_similarity_check.setChecked(get_config("DETECT_AUDIO_SIMILARITY", True))
        self.audio_similarity_check.setToolTip(
            "Analyzes audio content to find duplicate tracks regardless " "of filename or metadata"
        )
        org_layout.addWidget(self.audio_similarity_check)

        # Keep duplicates option
        self.keep_duplicates_check = QCheckBox("Keep All Duplicate Versions")
        self.keep_duplicates_check.setChecked(get_config("KEEP_ALL_DUPLICATES", False))
        self.keep_duplicates_check.setEnabled(self.audio_similarity_check.isChecked())
        self.keep_duplicates_check.setToolTip(
            "If unchecked, only the highest quality version of each duplicate " "will be kept"
        )
        # Connect audio similarity checkbox to enable/disable keep duplicates
        self.audio_similarity_check.toggled.connect(self.keep_duplicates_check.setEnabled)
        org_layout.addWidget(self.keep_duplicates_check)

        # Duplicate handling
        self.dup_check = QCheckBox("Detect and Handle Duplicates")
        self.dup_check.setChecked(get_config("HANDLE_DUPLICATES", True))
        org_layout.addWidget(self.dup_check)

        # Remove empty directories
        self.empty_dirs_check = QCheckBox("Remove Empty Directories")
        self.empty_dirs_check.setChecked(get_config("REMOVE_EMPTY_DIRS", True))
        org_layout.addWidget(self.empty_dirs_check)

        layout.addWidget(org_group)

        # Organize buttons
        btn_layout = QHBoxLayout()

        dry_run_btn = QPushButton("Dry Run")
        dry_run_btn.clicked.connect(self.on_dry_run_clicked)
        btn_layout.addWidget(dry_run_btn)

        organize_btn = QPushButton("Organize Files")
        organize_btn.clicked.connect(self.on_organize_clicked)
        btn_layout.addWidget(organize_btn)

        layout.addLayout(btn_layout)

    def select_destination(self):
        """Select the destination directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if directory:
            self.dest_label.setText(directory)

    def on_dry_run_clicked(self):
        """Handle dry run button click"""
        if self.validate_destination():
            self.dry_run_requested.emit()

    def on_organize_clicked(self):
        """Handle organize button click"""
        if self.validate_destination():
            self.organize_requested.emit()

    def validate_destination(self):
        """Validate that a destination directory is selected"""
        if self.dest_label.text() == "No destination selected":
            QMessageBox.warning(
                self, "Missing Destination", "Please select a destination directory."
            )
            return False
        return True

    def get_destination(self):
        """Get the selected destination directory"""
        return self.dest_label.text()

    def get_options(self):
        """Get options relevant to this tab"""
        return {
            "organize_by_language": self.lang_org_check.isChecked(),
            "use_audio_language_detection": self.audio_lang_detect_check.isChecked(),
            "detect_audio_similarity": self.audio_similarity_check.isChecked(),
            "keep_all_duplicates": self.keep_duplicates_check.isChecked(),
            "handle_duplicates": self.dup_check.isChecked(),
            "remove_empty_dirs": self.empty_dirs_check.isChecked(),
        }
