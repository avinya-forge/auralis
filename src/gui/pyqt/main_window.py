"""
Auralis - PyQt6 Main Window Implementation
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTabWidget,
    QHBoxLayout, QListWidget, QGroupBox, QCheckBox,
    QSpinBox, QLineEdit, QTextEdit,
    QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

import os
import time
from src.core.scanner import MusicScanner
from src.core.organizer import MusicOrganizer
from src.services.metadata_service import MetadataService
from src.utils.system_utils import SystemMonitor
from src.utils.config import (
    get_config, create_env_example
)


class WorkerThread(QThread):
    """Worker thread for background processing with 3-stage workflow"""

    # General signals
    progress_updated = pyqtSignal(str, int, int)  # stage, current, total
    status_updated = pyqtSignal(str)  # status message
    file_updated = pyqtSignal(str)  # current file being processed
    completed = pyqtSignal(dict)  # results summary

    # Stages
    STAGE_SCAN = 1
    STAGE_ORGANIZE = 2
    STAGE_METADATA = 3

    def __init__(self, source_dirs, dest_dir, options, system_monitor,
                 limit_files=None, dry_run=False, start_stage=1, end_stage=3):
        super().__init__()
        self.source_dirs = source_dirs
        self.dest_dir = dest_dir
        self.options = options
        self.system_monitor = system_monitor
        self.limit_files = limit_files  # Limit processing
        self.dry_run = dry_run  # Whether this is a dry run
        self.start_stage = start_stage  # Which stage to start from (1-3)
        self.end_stage = end_stage  # Which stage to end at (1-3)

        # Results and tracking
        self.processed_files = []  # List of files processed in dry run
        self.file_errors = {}  # Dict to track errors by file path
        self.scanned_files = []  # List of file info dicts from scan stage

        # Initialize components
        self.scanner = MusicScanner()
        self.metadata_service = MetadataService()
        self.organizer = MusicOrganizer(dry_run=dry_run)

    def run(self):
        """Run the multi-stage processing workflow"""
        try:
            # Basic implementation - just emit some progress updates
            self.status_updated.emit("Starting processing...")

            # Simplified implementation for demonstration
            total_files = 10 if self.limit_files else 100

            for i in range(total_files):
                if self.start_stage <= self.STAGE_SCAN:
                    # Stage 1 progress
                    self.progress_updated.emit("Scanning", i + 1, total_files)
                    self.file_updated.emit(f"Processing file {i + 1}")
                    self.status_updated.emit(
                        f"Scanning file {i + 1} of {total_files}")
                    time.sleep(0.2)  # Simulate processing time

            # Complete with results
            results = {
                "success": True,
                "files_processed": total_files,
                "stages_completed": [self.start_stage,
                                     min(self.end_stage, 3)]
            }

            self.status_updated.emit("Processing completed successfully")
            self.completed.emit(results)

        except Exception as e:
            self.status_updated.emit(f"Error: {str(e)}")
            self.completed.emit({"error": str(e)})


class MainWindow(QMainWindow):
    """Main window for the Auralis application - PyQt6 implementation"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auralis - Music File Management")
        self.setMinimumSize(1200, 800)  # Larger default size

        # Set window icon
        icon_path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__)))),
            "resources", "icons", "auralis.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize components
        self.scanner = MusicScanner()
        self.organizer = MusicOrganizer()
        self.system_monitor = SystemMonitor()

        # Initialize data structures
        self.scanned_files = []  # List of scanned file info dictionaries
        self.file_errors = {}    # Dict to track errors by file path

        # Current stage tracking
        self.current_stage = 1  # Start at stage 1

        # Load default directories from configuration
        self.default_input_dir = get_config("DEFAULT_INPUT_DIR", "")
        self.default_output_dir = get_config("DEFAULT_OUTPUT_DIR", "")

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
        self.worker_thread = None

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop system monitoring
        self.system_monitor.stop_monitoring()

        # Stop UI timer
        if self.ui_timer:
            self.ui_timer.stop()

        event.accept()

    def setup_ui(self):
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
        scan_tab = QWidget()
        scan_layout = QVBoxLayout(scan_tab)
        self.setup_stage1_ui(scan_layout)
        self.stage_tabs.addTab(scan_tab, "Stage 1: Scan & Rename")

        # Stage 2: Organize
        organize_tab = QWidget()
        organize_layout = QVBoxLayout(organize_tab)
        self.setup_stage2_ui(organize_layout)
        self.stage_tabs.addTab(organize_tab, "Stage 2: Organize")

        # Stage 3: Metadata
        metadata_tab = QWidget()
        metadata_layout = QVBoxLayout(metadata_tab)
        self.setup_stage3_ui(metadata_layout)
        self.stage_tabs.addTab(metadata_tab, "Stage 3: Metadata")

        controls_layout.addWidget(self.stage_tabs)

        # Common controls (progress, log, etc.)
        self.setup_process_controls_ui(controls_layout)

        main_splitter.addWidget(controls_container)

        # Set initial splitter sizes (60% file list, 40% controls)
        main_splitter.setSizes([600, 400])

        main_layout.addWidget(main_splitter)

        # Set the central widget
        self.setCentralWidget(main_widget)

    def setup_stage1_ui(self, parent_layout):
        """Set up the Stage 1 (Scan & Rename) UI"""
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

        parent_layout.addWidget(source_group)

        # Scan options
        options_group = QGroupBox("Scan Options")
        options_layout = QVBoxLayout(options_group)

        # File extensions
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("File Extensions:"))
        self.extensions_edit = QLineEdit(
            get_config("FILE_EXTENSIONS", "mp3,flac,m4a,wav,aac,ogg,wma"))
        ext_layout.addWidget(self.extensions_edit)
        options_layout.addLayout(ext_layout)

        # Rename options
        self.rename_check = QCheckBox("Rename Files (Title - Artist format)")
        self.rename_check.setChecked(get_config("RENAME_FILES", True))
        options_layout.addWidget(self.rename_check)

        # Test mode
        self.test_mode_check = QCheckBox(
            "Test Mode (Process only a subset of files)")
        self.test_mode_check.setChecked(get_config("TEST_MODE_ENABLED", True))
        options_layout.addWidget(self.test_mode_check)

        # Number of test files
        test_files_layout = QHBoxLayout()
        test_files_layout.addWidget(QLabel("Number of test files:"))
        self.test_files_spin = QSpinBox()
        self.test_files_spin.setMinimum(1)
        self.test_files_spin.setMaximum(100)
        self.test_files_spin.setValue(get_config("TEST_MODE_FILE_COUNT", 10))
        test_files_layout.addWidget(self.test_files_spin)
        options_layout.addLayout(test_files_layout)

        parent_layout.addWidget(options_group)

        # Scan button
        scan_btn = QPushButton("Scan Only")
        scan_btn.clicked.connect(self.start_scan)
        parent_layout.addWidget(scan_btn)

    def setup_stage2_ui(self, parent_layout):
        """Set up the Stage 2 (Organize) UI"""
        # Destination directory selection
        dest_group = QGroupBox("Destination Directory")
        dest_layout = QVBoxLayout(dest_group)

        self.dest_label = QLabel("No destination selected")
        dest_layout.addWidget(self.dest_label)

        dest_btn = QPushButton("Select Destination")
        dest_btn.clicked.connect(self.select_destination)
        dest_layout.addWidget(dest_btn)

        parent_layout.addWidget(dest_group)

        # Organization options
        org_group = QGroupBox("Organization Options")
        org_layout = QVBoxLayout(org_group)

        # Language-based organization
        self.lang_org_check = QCheckBox("Organize by Language")
        self.lang_org_check.setChecked(get_config("ORGANIZE_BY_LANGUAGE", True))
        org_layout.addWidget(self.lang_org_check)

        # Audio language detection checkbox
        self.audio_lang_detect_check = QCheckBox(
            "Use Audio Content for Language Detection")
        self.audio_lang_detect_check.setChecked(True)
        self.audio_lang_detect_check.setEnabled(self.lang_org_check.isChecked())
        # Connect language organization checkbox to enable/disable audio detection
        self.lang_org_check.toggled.connect(
            self.audio_lang_detect_check.setEnabled)
        org_layout.addWidget(self.audio_lang_detect_check)

        # Audio similarity detection
        self.audio_similarity_check = QCheckBox(
            "Detect Similar Audio Content (Find Duplicates)")
        self.audio_similarity_check.setChecked(
            get_config("DETECT_AUDIO_SIMILARITY", True))
        self.audio_similarity_check.setToolTip(
            "Analyzes audio content to find duplicate tracks regardless "
            "of filename or metadata")
        org_layout.addWidget(self.audio_similarity_check)

        # Keep duplicates option
        self.keep_duplicates_check = QCheckBox("Keep All Duplicate Versions")
        self.keep_duplicates_check.setChecked(
            get_config("KEEP_ALL_DUPLICATES", False))
        self.keep_duplicates_check.setEnabled(
            self.audio_similarity_check.isChecked())
        self.keep_duplicates_check.setToolTip(
            "If unchecked, only the highest quality version of each duplicate "
            "will be kept")
        # Connect audio similarity checkbox to enable/disable keep duplicates
        self.audio_similarity_check.toggled.connect(
            self.keep_duplicates_check.setEnabled)
        org_layout.addWidget(self.keep_duplicates_check)

        # Duplicate handling
        self.dup_check = QCheckBox("Detect and Handle Duplicates")
        self.dup_check.setChecked(get_config("HANDLE_DUPLICATES", True))
        org_layout.addWidget(self.dup_check)

        # Remove empty directories
        self.empty_dirs_check = QCheckBox("Remove Empty Directories")
        self.empty_dirs_check.setChecked(get_config("REMOVE_EMPTY_DIRS", True))
        org_layout.addWidget(self.empty_dirs_check)

        parent_layout.addWidget(org_group)

        # Organize buttons
        btn_layout = QHBoxLayout()

        dry_run_btn = QPushButton("Dry Run")
        dry_run_btn.clicked.connect(self.start_dry_run)
        btn_layout.addWidget(dry_run_btn)

        organize_btn = QPushButton("Organize Files")
        organize_btn.clicked.connect(self.start_organize)
        btn_layout.addWidget(organize_btn)

        parent_layout.addLayout(btn_layout)

    def setup_stage3_ui(self, parent_layout):
        """Set up the Stage 3 (Metadata) UI"""
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

        parent_layout.addWidget(metadata_group)

        # Lyrics options
        lyrics_group = QGroupBox("Lyrics")
        lyrics_layout = QVBoxLayout(lyrics_group)

        # Fetch lyrics
        self.lyrics_check = QCheckBox("Fetch and Embed Lyrics")
        self.lyrics_check.setChecked(get_config("FETCH_LYRICS", True))
        self.lyrics_check.setToolTip(
            "Fetch lyrics from online sources and embed them in the audio files")
        lyrics_layout.addWidget(self.lyrics_check)

        lyrics_info = QLabel(
            "Lyrics will be embedded in the audio files so they can be "
            "displayed in music players like Apple Music.")
        lyrics_info.setWordWrap(True)
        lyrics_layout.addWidget(lyrics_info)

        parent_layout.addWidget(lyrics_group)

        # Update button
        update_btn = QPushButton("Update Metadata")
        update_btn.clicked.connect(self.start_metadata_update)
        parent_layout.addWidget(update_btn)

    def setup_process_controls_ui(self, parent_layout):
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

    def add_source_directory(self):
        """Add a source directory to scan"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Source Directory")
        if directory:
            self.source_list.addItem(directory)

    def remove_source_directory(self):
        """Remove the selected source directory"""
        selected_items = self.source_list.selectedItems()
        for item in selected_items:
            self.source_list.takeItem(self.source_list.row(item))

    def select_destination(self):
        """Select the destination directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory")
        if directory:
            self.dest_label.setText(directory)

    def set_default_directories(self):
        """Set default directories from configuration"""
        # Add default input directory if it exists
        if self.default_input_dir and os.path.exists(self.default_input_dir):
            self.source_list.addItem(self.default_input_dir)

        # Set default output directory
        if self.default_output_dir and os.path.exists(
                os.path.dirname(self.default_output_dir)):
            self.dest_label.setText(self.default_output_dir)

    def update_ui(self):
        """Update UI elements that need regular updates"""
        # Only update if no worker thread is running
        if self.worker_thread is None or not self.worker_thread.isRunning():
            # Update system resource display if needed
            pass

    def validate_source_directories(self):
        """Validate that source directories are selected"""
        if self.source_list.count() == 0:
            QMessageBox.warning(
                self, "Missing Source",
                "Please add at least one source directory.")
            return False
        return True

    def validate_destination(self):
        """Validate that a destination directory is selected"""
        if self.dest_label.text() == "No destination selected":
            QMessageBox.warning(
                self, "Missing Destination",
                "Please select a destination directory.")
            return False
        return True

    def collect_source_dirs(self):
        """Collect all source directories from the list"""
        source_dirs = []
        for i in range(self.source_list.count()):
            source_dirs.append(self.source_list.item(i).text())
        return source_dirs

    def collect_options(self):
        """Collect all options from UI controls"""
        options = {
            'organize_by_language': self.lang_org_check.isChecked(),
            'use_audio_language_detection':
                self.audio_lang_detect_check.isChecked(),
            'detect_audio_similarity':
                self.audio_similarity_check.isChecked(),
            'keep_all_duplicates': self.keep_duplicates_check.isChecked(),
            'handle_duplicates': self.dup_check.isChecked(),
            'rename_files': self.rename_check.isChecked(),
            'remove_empty_dirs': self.empty_dirs_check.isChecked(),
            'use_musicbrainz': self.mb_check.isChecked(),
            'use_discogs': self.discogs_check.isChecked(),
            'fetch_lyrics': self.lyrics_check.isChecked(),
            'file_extensions': self.extensions_edit.text().split(','),
        }
        return options

    def prepare_worker_thread(self, dry_run=False, start_stage=1,
                              end_stage=3):
        """Prepare the worker thread with current settings"""
        # Collect source directories
        source_dirs = self.collect_source_dirs()

        # Get destination directory
        dest_dir = self.dest_label.text()

        # Get options
        options = self.collect_options()

        # Get file limit for test mode
        limit_files = None
        if self.test_mode_check.isChecked():
            limit_files = self.test_files_spin.value()

        # Create worker thread
        self.worker_thread = WorkerThread(
            source_dirs, dest_dir, options, self.system_monitor,
            limit_files=limit_files, dry_run=dry_run,
            start_stage=start_stage, end_stage=end_stage
        )

        # Connect signals
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.status_updated.connect(self.update_status)
        self.worker_thread.file_updated.connect(self.update_current_file)
        self.worker_thread.completed.connect(self.processing_completed)

        return True

    def start_scan(self):
        """Start the scanning process (Stage 1)"""
        if not self.validate_source_directories():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting scan...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=1, end_stage=1):
            self.worker_thread.start()

    def start_dry_run(self):
        """Start a dry run of the organization process"""
        if not self.validate_source_directories() or not self.validate_destination():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting dry run (no files will be moved)...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(dry_run=True, start_stage=2,
                                      end_stage=2):
            self.worker_thread.start()

    def start_organize(self):
        """Start the organization process (Stage 2)"""
        if not self.validate_source_directories() or not self.validate_destination():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting organization...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=2, end_stage=2):
            self.worker_thread.start()

    def start_metadata_update(self):
        """Start the metadata update process (Stage 3)"""
        if not self.validate_source_directories():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting metadata update...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=3, end_stage=3):
            self.worker_thread.start()

    def run_all_stages(self):
        """Run all stages of the process"""
        if not self.validate_source_directories() or not self.validate_destination():
            return

        # Prepare UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.add_log_message("Starting all stages...")

        # Prepare and start worker thread
        if self.prepare_worker_thread(start_stage=1, end_stage=3):
            self.worker_thread.start()

    def stop_processing(self):
        """Stop the current processing"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self, "Stop Processing",
                "Are you sure you want to stop the current process?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker_thread.terminate()
                self.worker_thread.wait()
                self.add_log_message("Processing stopped by user")

    def update_progress(self, stage, current, total):
        """Update progress bar"""
        if total > 0:
            percent = int(current / total * 100)
            self.progress_bar.setValue(percent)
            self.stage_label.setText(
                f"{stage}: {current}/{total} ({percent}%)")

    def update_status(self, message):
        """Update status label"""
        self.stage_label.setText(message)
        self.add_log_message(message)

    def update_current_file(self, file_info):
        """Update current file being processed"""
        self.current_file_label.setText(file_info)

    def add_log_message(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Scroll to bottom
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def processing_completed(self, results):
        """Handle completion of processing"""
        # Check for errors
        if 'error' in results:
            self.add_log_message(f"Error: {results['error']}")
            QMessageBox.critical(self, "Error",
                                 f"Processing failed: {results['error']}")
            return

        # Log completion
        self.add_log_message("Processing completed successfully!")

        # Show summary
        QMessageBox.information(
            self, "Processing Complete",
            "Processing completed successfully!"
        )
