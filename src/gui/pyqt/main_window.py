"""
Auralis - PyQt6 Main Window Implementation
"""

import os
import time
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent, QFont, QIcon
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.organizer import MusicOrganizer
from src.core.scanner import MusicScanner
from src.gui.pyqt.tabs.metadata_tab import MetadataTab
from src.gui.pyqt.tabs.organize_tab import OrganizeTab
from src.gui.pyqt.tabs.scan_tab import ScanTab
from src.gui.pyqt.worker import WorkerThread
from src.utils.config import create_env_example, get_config
from src.utils.system_utils import SystemMonitor


class MainWindow(QMainWindow):
    """Main window for the Auralis application - PyQt6 implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Auralis - Music File Management")
        self.setMinimumSize(1200, 800)  # Larger default size

        # Set window icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "resources",
            "icons",
            "auralis.png",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize components
        self.scanner = MusicScanner()
        self.organizer = MusicOrganizer()
        self.system_monitor = SystemMonitor()

        # Initialize data structures
        self.scanned_files: List[Dict[str, Any]] = []  # List of scanned file info dictionaries
        self.file_errors: Dict[str, str] = {}  # Dict to track errors by file path

        # Current stage tracking
        self.current_stage = 1  # Start at stage 1

        # Load default directories from configuration
        self.default_input_dir = str(get_config("DEFAULT_INPUT_DIR", ""))
        self.default_output_dir = str(get_config("DEFAULT_OUTPUT_DIR", ""))

        # Create example environment file if it doesn't exist
        if not create_env_example():
            print("Warning: Could not create .env.example file")

        # Start system monitoring
        self.system_monitor.start_monitoring()

        # Setup UI
        self.setup_ui()

        # Set default directories
        self.set_default_directories()

        # Update UI timer
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(500)  # Update every 500ms

        # Worker thread
        self.worker_thread: Optional[WorkerThread] = None

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """Handle window close event"""
        # Stop system monitoring
        self.system_monitor.stop_monitoring()

        # Stop UI timer
        if self.ui_timer:
            self.ui_timer.stop()

        if event:
            event.accept()

    def setup_ui(self) -> None:
        """Set up the full user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Header with title
        header_layout = QHBoxLayout()
        header_label = QLabel("Auralis")
        header_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(header_label)

        main_layout.addLayout(header_layout)

        # Main splitter between file list and controls
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Basic file list placeholder
        file_list_container = QWidget()
        file_list_layout = QVBoxLayout(file_list_container)
        file_list_label = QLabel("File List")
        file_list_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        file_list_layout.addWidget(file_list_label)

        self.file_list = QListWidget()
        file_list_layout.addWidget(self.file_list)

        # File details
        file_details_label = QLabel("File Details")
        file_details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        file_list_layout.addWidget(file_details_label)

        self.file_details = QTextEdit()
        self.file_details.setReadOnly(True)
        self.file_details.setMaximumHeight(150)
        file_list_layout.addWidget(self.file_details)

        main_splitter.addWidget(file_list_container)

        # Right side: Controls
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)

        # Tab widget for stages
        self.stage_tabs = QTabWidget()

        # Stage 1: Scan & Rename
        self.scan_tab = ScanTab()
        self.scan_tab.scan_requested.connect(self.start_scan)
        self.stage_tabs.addTab(self.scan_tab, "Stage 1: Scan & Rename")

        # Stage 2: Organize
        self.organize_tab = OrganizeTab(default_output_dir=self.default_output_dir)
        self.organize_tab.dry_run_requested.connect(self.start_dry_run)
        self.organize_tab.organize_requested.connect(self.start_organize)
        self.stage_tabs.addTab(self.organize_tab, "Stage 2: Organize")

        # Stage 3: Metadata
        self.metadata_tab = MetadataTab()
        self.metadata_tab.update_requested.connect(self.start_metadata_update)
        self.stage_tabs.addTab(self.metadata_tab, "Stage 3: Metadata")

        controls_layout.addWidget(self.stage_tabs)

        # Common controls (progress, log, etc.)
        self.setup_process_controls_ui(controls_layout)

        main_splitter.addWidget(controls_container)

        # Set initial splitter sizes (60% file list, 40% controls)
        main_splitter.setSizes([600, 400])

        main_layout.addWidget(main_splitter)

        # Set the central widget
        self.setCentralWidget(main_widget)

    def setup_process_controls_ui(self, parent_layout: QVBoxLayout) -> None:
        """Set up process controls UI"""
        process_group = QGroupBox("Process Control")
        process_layout = QVBoxLayout(process_group)

        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        process_layout.addLayout(progress_layout)

        # Current stage and file
        self.stage_label = QLabel("Ready")
        process_layout.addWidget(self.stage_label)

        self.current_file_label = QLabel("No file being processed")
        process_layout.addWidget(self.current_file_label)

        # Log
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Processing Log:"))

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        process_layout.addLayout(log_layout)

        # Run all stages button
        all_stages_btn = QPushButton("Run All Stages")
        all_stages_btn.clicked.connect(self.run_all_stages)
        process_layout.addWidget(all_stages_btn)

        # Stop button
        stop_btn = QPushButton("Stop Processing")
        stop_btn.clicked.connect(self.stop_processing)
        process_layout.addWidget(stop_btn)

        parent_layout.addWidget(process_group)

    def set_default_directories(self) -> None:
        """Set default directories from configuration"""
        # Add default input directory if it exists
        if self.default_input_dir and os.path.exists(self.default_input_dir):
            self.scan_tab.add_directory(self.default_input_dir)

    def update_ui(self) -> None:
        """Update UI elements that need regular updates"""
        # Only update if no worker thread is running
        if self.worker_thread is None or not self.worker_thread.isRunning():
            # Update system resource display if needed
            pass

    def collect_source_dirs(self) -> List[str]:
        """Collect all source directories from the list"""
        return self.scan_tab.collect_source_dirs()

    def collect_options(self) -> Dict[str, Any]:
        """Collect all options from UI controls"""
        options: Dict[str, Any] = {}
        options.update(self.scan_tab.get_options())
        options.update(self.organize_tab.get_options())
        options.update(self.metadata_tab.get_options())
        return options

    def prepare_worker_thread(
        self, dry_run: bool = False, start_stage: int = 1, end_stage: int = 3
    ) -> bool:
        """Prepare the worker thread with current settings"""
        # Collect source directories
        source_dirs = self.collect_source_dirs()

        # Get destination directory
        dest_dir = self.organize_tab.get_destination()

        # Get options
        options = self.collect_options()

        # Get file limit for test mode
        limit_files = None
        if options.get("test_mode"):
            limit_files = options.get("test_file_count")

        # Create worker thread
        self.worker_thread = WorkerThread(
            source_dirs,
            dest_dir,
            options,
            self.system_monitor,
            limit_files=limit_files,
            dry_run=dry_run,
            start_stage=start_stage,
            end_stage=end_stage,
        )

        # Connect signals
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.status_updated.connect(self.update_status)
        self.worker_thread.file_updated.connect(self.update_current_file)
        self.worker_thread.completed.connect(self.processing_completed)

        return True

    def start_scan(self) -> None:
        """Start the scanning process (Stage 1)"""
        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting scan...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=1, end_stage=1):
            # The check above creates the thread, now we start it
            if self.worker_thread:
                self.worker_thread.start()

    def start_dry_run(self) -> None:
        """Start a dry run of the organization process"""
        if not self.scan_tab.validate_source_directories():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting dry run (no files will be moved)...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(dry_run=True, start_stage=2, end_stage=2):
            if self.worker_thread:
                self.worker_thread.start()

    def start_organize(self) -> None:
        """Start the organization process (Stage 2)"""
        if not self.scan_tab.validate_source_directories():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting organization...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=2, end_stage=2):
            if self.worker_thread:
                self.worker_thread.start()

    def start_metadata_update(self) -> None:
        """Start the metadata update process (Stage 3)"""
        if not self.scan_tab.validate_source_directories():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting metadata update...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=3, end_stage=3):
            if self.worker_thread:
                self.worker_thread.start()

    def run_all_stages(self) -> None:
        """Run all stages of the process"""
        if (
            not self.scan_tab.validate_source_directories()
            or not self.organize_tab.validate_destination()
        ):
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting all stages...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=1, end_stage=3):
            if self.worker_thread:
                self.worker_thread.start()

    def stop_processing(self) -> None:
        """Stop the current processing"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Stop Processing",
                "Are you sure you want to stop the current process?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker_thread.terminate()
                self.worker_thread.wait()
                self.add_log_message("Processing stopped by user")

    def update_progress(self, stage: int, current: int, total: int) -> None:
        """Update progress bar"""
        if total > 0:
            percent = int(current / total * 100)
            self.progress_bar.setValue(percent)
            self.stage_label.setText(f"{stage}: {current}/{total} ({percent}%)")

    def update_status(self, message: str) -> None:
        """Update status label"""
        self.stage_label.setText(message)
        self.add_log_message(message)

    def update_current_file(self, file_info: str) -> None:
        """Update current file being processed"""
        self.current_file_label.setText(file_info)

    def add_log_message(self, message: str) -> None:
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Scroll to bottom
        sb = self.log_text.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def processing_completed(self, results: Dict[str, Any]) -> None:
        """Handle completion of processing"""
        # Check for errors
        if "error" in results:
            self.add_log_message(f"Error: {results['error']}")
            QMessageBox.critical(self, "Error", f"Processing failed: {results['error']}")
            return

        # Log completion
        self.add_log_message("Processing completed successfully!")

        # Show summary
        QMessageBox.information(self, "Processing Complete", "Processing completed successfully!")
