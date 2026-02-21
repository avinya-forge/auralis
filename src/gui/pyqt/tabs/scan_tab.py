"""
Stage 1: Scan & Rename Tab
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.utils.config import get_config


class ScanTab(QWidget):
    """Tab for Stage 1: Scan & Rename"""

    scan_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Source directory selection
        source_group = QGroupBox("Source Directories")
        source_layout = QVBoxLayout(source_group)

        self.source_list = QListWidget()
        source_layout.addWidget(self.source_list)

        source_btn_layout = QHBoxLayout()
        add_source_btn = QPushButton("Add Directory")
        add_source_btn.clicked.connect(self.add_source_directory)
        remove_source_btn = QPushButton("Remove Selected")
        remove_source_btn.clicked.connect(self.remove_source_directory)

        source_btn_layout.addWidget(add_source_btn)
        source_btn_layout.addWidget(remove_source_btn)
        source_layout.addLayout(source_btn_layout)

        layout.addWidget(source_group)

        # Scan options
        options_group = QGroupBox("Scan Options")
        options_layout = QVBoxLayout(options_group)

        # File extensions
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("File Extensions:"))
        self.extensions_edit = QLineEdit(
            str(get_config("FILE_EXTENSIONS", "mp3,flac,m4a,wav,aac,ogg,wma"))
        )
        ext_layout.addWidget(self.extensions_edit)
        options_layout.addLayout(ext_layout)

        # Rename options
        self.rename_check = QCheckBox("Rename Files (Title - Artist format)")
        self.rename_check.setChecked(bool(get_config("RENAME_FILES", True)))
        options_layout.addWidget(self.rename_check)

        # Test mode
        self.test_mode_check = QCheckBox("Test Mode (Process only a subset of files)")
        self.test_mode_check.setChecked(bool(get_config("TEST_MODE_ENABLED", True)))
        options_layout.addWidget(self.test_mode_check)

        # Number of test files
        test_files_layout = QHBoxLayout()
        test_files_layout.addWidget(QLabel("Number of test files:"))
        self.test_files_spin = QSpinBox()
        self.test_files_spin.setMinimum(1)
        self.test_files_spin.setMaximum(100)
        self.test_files_spin.setValue(int(get_config("TEST_MODE_FILE_COUNT", 10)))
        test_files_layout.addWidget(self.test_files_spin)
        options_layout.addLayout(test_files_layout)

        layout.addWidget(options_group)

        # Scan button
        scan_btn = QPushButton("Scan Only")
        scan_btn.clicked.connect(self.on_scan_clicked)
        layout.addWidget(scan_btn)

    def add_source_directory(self) -> None:
        """Add a source directory to scan"""
        directory = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if directory:
            self.add_directory(directory)

    def add_directory(self, path: str) -> None:
        """Add a directory path to the list"""
        self.source_list.addItem(path)

    def remove_source_directory(self) -> None:
        """Remove the selected source directory"""
        selected_items = self.source_list.selectedItems()
        for item in selected_items:
            self.source_list.takeItem(self.source_list.row(item))

    def on_scan_clicked(self) -> None:
        """Handle scan button click"""
        if self.validate_source_directories():
            self.scan_requested.emit()

    def validate_source_directories(self) -> bool:
        """Validate that source directories are selected"""
        if self.source_list.count() == 0:
            QMessageBox.warning(self, "Missing Source", "Please add at least one source directory.")
            return False
        return True

    def collect_source_dirs(self) -> List[str]:
        """Collect all source directories from the list"""
        source_dirs = []
        for i in range(self.source_list.count()):
            item = self.source_list.item(i)
            if item:
                source_dirs.append(item.text())
        return source_dirs

    def get_options(self) -> Dict[str, Any]:
        """Get options relevant to this tab"""
        return {
            "rename_files": self.rename_check.isChecked(),
            "file_extensions": self.extensions_edit.text().split(","),
            "test_mode": self.test_mode_check.isChecked(),
            "test_file_count": self.test_files_spin.value(),
        }
