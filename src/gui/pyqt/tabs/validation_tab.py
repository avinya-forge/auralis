"""
Auralis - Metadata Validation Tab
Gamified interface for user metadata verification.
"""

from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ValidationTab(QWidget):
    """
    Tab for user crowdsourcing and metadata validation.
    """

    metadata_verified = pyqtSignal(str, dict)  # file_id, validated_metadata

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_record: Optional[Dict[str, Any]] = None
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        self.header = QLabel("Metadata Validation Queue")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header)

        # Content Area (Scrollable)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.empty_label = QLabel("No pending validations. Great job!")
        self.container_layout.addWidget(self.empty_label)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.skip_btn = QPushButton("Skip")
        self.skip_btn.setEnabled(False)
        self.verify_btn = QPushButton("Verify & Earn Points")
        self.verify_btn.setEnabled(False)
        self.verify_btn.setStyleSheet("background-color: #2ecc71; color: white;")

        button_layout.addWidget(self.skip_btn)
        button_layout.addWidget(self.verify_btn)
        layout.addLayout(button_layout)

    def load_record(self, record: Dict[str, Any]) -> None:
        """Loads a metadata record into the validation view."""
        self.current_record = record
        # Cleanup container
        for i in reversed(range(self.container_layout.count())):
            self.container_layout.itemAt(i).widget().setParent(None)

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
