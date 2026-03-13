import asyncio
"""
Worker Thread for Auralis PyQt6 Main Window
"""

import traceback
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from src.core.organizer import MusicOrganizer
from src.core.scanner import MusicScanner
from src.services.metadata_service import MetadataService


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

    def __init__(
        self,
        source_dirs: List[str],
        dest_dir: str,
        options: Dict[str, Any],
        system_monitor: Any,
        limit_files: Optional[int] = None,
        dry_run: bool = False,
        start_stage: int = 1,
        end_stage: int = 3,
        active_stages: Optional[List[int]] = None,
    ) -> None:
        super().__init__()
        self.source_dirs = source_dirs
        self.dest_dir = dest_dir
        self.options = options
        self.system_monitor = system_monitor
        self.limit_files = limit_files  # Limit processing
        self.dry_run = dry_run  # Whether this is a dry run

        # Determine active stages
        if active_stages:
            self.active_stages = active_stages
        else:
            self.active_stages = list(range(start_stage, end_stage + 1))

        # Results and tracking
        self.processed_files: List[str] = []  # List of files processed in dry run
        self.file_errors: Dict[str, str] = {}  # Dict to track errors by file path
        self.scanned_files: List[Dict[str, Any]] = []  # List of file info dicts from scan stage

        # Initialize components
        self.scanner = MusicScanner()
        self.metadata_service = MetadataService()
        self.organizer = MusicOrganizer(dry_run=dry_run)

    def run(self) -> None:
        """Run the multi-stage processing workflow"""
        try:
            results: Dict[str, Any] = {
                "success": False,
                "files_processed": 0,
                "stages_completed": [],
            }

            if self.STAGE_SCAN in self.active_stages:
                self._run_scan_stage(results)
                if not self.scanned_files:
                    self.completed.emit(results)
                    return

            if self.STAGE_ORGANIZE in self.active_stages:
                self._run_organize_stage(results)

            if self.STAGE_METADATA in self.active_stages:
                self._run_metadata_stage(results)

            results["success"] = True
            results["files_processed"] = len(self.scanned_files)

            self.status_updated.emit("Processing completed successfully")
            self.completed.emit(results)

        except Exception as e:
            traceback.print_exc()
            self.status_updated.emit(f"Error: {str(e)}")
            self.completed.emit({"error": str(e), "success": False})

    def _run_scan_stage(self, results: Dict[str, Any]) -> None:
        self.status_updated.emit("Starting scan...")

        # Connect scanner signals
        self.scanner.progress_updated.connect(self._on_scan_progress)
        self.scanner.file_scanned.connect(self._on_scan_file)

        # Run scan
        scan_options = {
            "file_extensions": self.options.get("file_extensions"),
            "exclude_patterns": self.options.get("exclude_patterns"),
        }
        self.scanned_files = asyncio.run(self.scanner.scan_directories(self.source_dirs, scan_options))

        # Disconnect signals
        self.scanner.progress_updated.disconnect(self._on_scan_progress)
        self.scanner.file_scanned.disconnect(self._on_scan_file)

        results["stages_completed"].append(self.STAGE_SCAN)
        self.status_updated.emit(f"Scan completed. Found {len(self.scanned_files)} files.")

        if not self.scanned_files:
            self.status_updated.emit("No files found to process.")
            return

        # Apply file limit if set (e.g. for test mode)
        if self.limit_files and len(self.scanned_files) > self.limit_files:
            self.scanned_files = self.scanned_files[: self.limit_files]
            self.status_updated.emit(f"Limiting to {self.limit_files} files for processing.")

    def _run_organize_stage(self, results: Dict[str, Any]) -> None:
        if not self.scanned_files and self.STAGE_SCAN not in self.active_stages:
            self.status_updated.emit("Skipping organize: No files scanned.")
            return

        if self.scanned_files:
            self.status_updated.emit("Starting organization...")

            # Connect signals
            self.organizer.progress_updated.connect(self._on_organize_progress)
            self.organizer.file_organized.connect(self._on_organize_file)

            # Run organize
            organize_options = {
                "organize_by_language": self.options.get("organize_by_language", True),
                "detect_audio_similarity": self.options.get("detect_audio_similarity", False),
                "rename_files": self.options.get("rename_files", True),
                "handle_duplicates": self.options.get("handle_duplicates", True),
                "remove_empty_dirs": self.options.get("remove_empty_dirs", True),
            }

            org_results = self.organizer.organize_files(
                self.scanned_files, self.dest_dir, organize_options
            )

            # Disconnect signals
            self.organizer.progress_updated.disconnect(self._on_organize_progress)
            self.organizer.file_organized.disconnect(self._on_organize_file)

            results["stages_completed"].append(self.STAGE_ORGANIZE)
            results["organize_stats"] = org_results
            self.status_updated.emit("Organization completed.")

    def _run_metadata_stage(self, results: Dict[str, Any]) -> None:
        if not self.scanned_files and self.STAGE_SCAN not in self.active_stages:
            self.status_updated.emit("Skipping metadata: No files scanned.")
            return

        if self.scanned_files:
            self.status_updated.emit("Starting metadata update...")

            # Connect signals
            self.metadata_service.progress_updated.connect(self._on_metadata_progress)
            self.metadata_service.file_updated.connect(self._on_metadata_file)

            # Run metadata update
            meta_options = {
                "use_musicbrainz": self.options.get("use_musicbrainz", True),
                "use_discogs": self.options.get("use_discogs", True),
                "fetch_lyrics": self.options.get("fetch_lyrics", True),
                "fetch_cover_art": self.options.get("fetch_cover_art", True),
                "analyze_audio": self.options.get("analyze_audio", False),
                "force_update": self.options.get("force_metadata_update", False),
            }

            # Update paths if files were moved
            files_to_update = self.scanned_files
            for f in files_to_update:
                if "new_path" in f:
                    f["path"] = f["new_path"]

            self.metadata_service.update_metadata(files_to_update, meta_options)

            # Disconnect signals
            self.metadata_service.progress_updated.disconnect(self._on_metadata_progress)
            self.metadata_service.file_updated.disconnect(self._on_metadata_file)

            results["stages_completed"].append(self.STAGE_METADATA)
            self.status_updated.emit("Metadata update completed.")

    def _on_scan_progress(self, current: int, total: int) -> None:
        self.progress_updated.emit("Scanning", current, total)

    def _on_scan_file(self, file_path: str) -> None:
        self.file_updated.emit(f"Scanning: {file_path}")

    def _on_organize_progress(self, current: int, total: int) -> None:
        self.progress_updated.emit("Organizing", current, total)

    def _on_organize_file(self, src: str, dest: str) -> None:
        self.file_updated.emit(f"Organizing: {src} -> {dest}")

    def _on_metadata_progress(self, current: int, total: int) -> None:
        self.progress_updated.emit("Metadata", current, total)

    def _on_metadata_file(self, file_path: str) -> None:
        self.file_updated.emit(f"Updating metadata: {file_path}")
