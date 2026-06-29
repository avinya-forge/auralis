"""
Auralis - Metadata Validation Tab
Gamified interface for user metadata verification.
"""

import os
from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.services.gamification import GamificationService
from src.utils.config import DATA_DIR


class ValidationTab(QWidget):
    """
    Tab for user crowdsourcing and metadata validation.
    """

    metadata_verified = pyqtSignal(str, dict)  # file_id, validated_metadata
    metadata_skipped = pyqtSignal(str)  # file_id

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_record: Optional[Dict[str, Any]] = None
        db_path = os.path.join(DATA_DIR, "gamification.db")
        self.gamification_service = GamificationService(db_path)
        self.user_id = "local_user"  # Fixed user for now
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        self.header = QLabel("Metadata Validation Queue")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header)

        # Stats Display
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 14px; color: #2980b9;")
        self.update_stats_display()
        layout.addWidget(self.stats_label)

        # Content Area (Scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.empty_label = QLabel("No pending validations. Great job!")
        self.container_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.skip_btn = QPushButton("Skip")
        self.skip_btn.setEnabled(False)
        self.verify_btn = QPushButton("Verify & Earn Points")
        self.verify_btn.setEnabled(False)
        self.verify_btn.setStyleSheet("background-color: #2ecc71; color: white;")

        # Handle skip button click
        self.skip_btn.clicked.connect(self._on_skip)

        # Handle verify button click
        self.verify_btn.clicked.connect(self._on_verify)

        button_layout.addWidget(self.skip_btn)
        button_layout.addWidget(self.verify_btn)
        layout.addLayout(button_layout)

    def load_record(self, record: Dict[str, Any]) -> None:
        """Loads a metadata record into the validation view."""
        self.current_record = record
        # Cleanup container
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        # Build form
        tags = record.get("raw_tags", {})
        for key, value in tags.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key.capitalize()}:"))
            edit = QLineEdit(str(value))
            row.addWidget(edit)
            self.container_layout.addLayout(row)

        self.skip_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)


    def update_stats_display(self) -> None:
        stats = self.gamification_service.get_user_stats(self.user_id)
        self.stats_label.setText(
            f"Level: {stats['level']} | Points: {stats['points']} | Validations: {stats['validations']}"
        )

    def _on_verify(self) -> None:
        if self.current_record:
            file_id = self.current_record.get("file_id", "")
            tags = {}
            for i in range(self.container_layout.count()):
                item = self.container_layout.itemAt(i)
                if item is not None and item.layout() is not None:
                    row = item.layout()
                    label_widget = row.itemAt(0).widget()
                    edit_widget = row.itemAt(1).widget()
                    if label_widget is not None and edit_widget is not None:
                        key = label_widget.text().replace(":", "").lower()
                        tags[key] = edit_widget.text()

            # Award points and update UI
            _ = self.gamification_service.add_validation_points(self.user_id)
            self.update_stats_display()

            self.metadata_verified.emit(file_id, tags)
