"""
Worker Thread for Auralis wxPython Main Window
"""

import threading
import traceback
import wx

from src.gui.wx.events import (
    ProgressEvent,
    StatusEvent,
    FileEvent,
    CompletionEvent
)
from src.core.organizer import MusicOrganizer
from src.core.scanner import MusicScanner
from src.services.metadata_service import MetadataService


class WorkerThread(threading.Thread):
    """Worker thread for background processing with 3-stage workflow (wxPython)"""

    # Stages
    STAGE_SCAN = 1
    STAGE_ORGANIZE = 2
    STAGE_METADATA = 3

    def __init__(
        self,
        window,
        source_dirs,
        dest_dir,
        options,
        system_monitor,
        limit_files=None,
        dry_run=False,
        start_stage=1,
        end_stage=3,
        active_stages=None,
    ):
        super().__init__()
        self.window = window  # The window to post events to
        self.source_dirs = source_dirs
        self.dest_dir = dest_dir
        self.options = options
        self.system_monitor = system_monitor
        self.limit_files = limit_files
        self.dry_run = dry_run

        # Determine active stages
        if active_stages:
            self.active_stages = active_stages
        else:
            self.active_stages = list(range(start_stage, end_stage + 1))

        self.daemon = True  # Daemon thread exits when main thread exits

        # Results and tracking
        self.scanned_files = []

        # Initialize components
        # Note: These components use QObject, so they need a QCoreApplication instance
        # to exist in the process. The CLI or Main Window should have initialized it.
        self.scanner = MusicScanner()
        self.metadata_service = MetadataService()
        self.organizer = MusicOrganizer(dry_run=dry_run)

        # Stop flag
        self._stop_event = threading.Event()

    def stop(self):
        """Signal the worker to stop"""
        self._stop_event.set()

    def run(self):
        """Run the multi-stage processing workflow"""
        try:
            results = {
                "success": False,
                "files_processed": 0,
                "stages_completed": [],
            }

            # --- STAGE 1: SCAN ---
            if self.STAGE_SCAN in self.active_stages:
                if self._stop_event.is_set():
                    return

                self._post_status("Starting scan...")

                # Connect scanner signals
                self.scanner.progress_updated.connect(self._on_scan_progress)
                self.scanner.file_scanned.connect(self._on_scan_file)

                # Run scan
                scan_options = {
                    "file_extensions": self.options.get("file_extensions"),
                    "exclude_patterns": self.options.get("exclude_patterns"),
                }

                # Note: scan_directories is blocking. We can't easily interrupt it
                # unless we modify MusicScanner to check a stop flag.
                self.scanned_files = self.scanner.scan_directories(self.source_dirs, scan_options)

                # Disconnect signals
                self.scanner.progress_updated.disconnect(self._on_scan_progress)
                self.scanner.file_scanned.disconnect(self._on_scan_file)

                results["stages_completed"].append(self.STAGE_SCAN)
                self._post_status(f"Scan completed. Found {len(self.scanned_files)} files.")

                if not self.scanned_files:
                    self._post_status("No files found to process.")
                    self._post_completed(results)
                    return

                if self.limit_files and len(self.scanned_files) > self.limit_files:
                    self.scanned_files = self.scanned_files[:self.limit_files]
                    self._post_status(f"Limiting to {self.limit_files} files for processing.")

            # --- STAGE 2: ORGANIZE ---
            if self.STAGE_ORGANIZE in self.active_stages:
                if self._stop_event.is_set():
                    return

                if not self.scanned_files and self.STAGE_SCAN not in self.active_stages:
                    self._post_status("Skipping organize: No files scanned.")
                elif self.scanned_files:
                    self._post_status("Starting organization...")

                    # Connect signals
                    self.organizer.progress_updated.connect(self._on_organize_progress)
                    self.organizer.file_organized.connect(self._on_organize_file)

                    organize_options = {
                        "organize_by_language": self.options.get("organize_by_language", True),
                        "detect_audio_similarity": self.options.get("detect_audio_similarity", False),
                        "rename_files": self.options.get("rename_files", True),
                        "handle_duplicates": self.options.get("handle_duplicates", True),
                        "remove_empty_dirs": self.options.get("remove_empty_dirs", True),
                    }

                    org_results = self.organizer.organize_files(self.scanned_files, self.dest_dir, organize_options)

                    self.organizer.progress_updated.disconnect(self._on_organize_progress)
                    self.organizer.file_organized.disconnect(self._on_organize_file)

                    results["stages_completed"].append(self.STAGE_ORGANIZE)
                    results["organize_stats"] = org_results
                    self._post_status("Organization completed.")

            # --- STAGE 3: METADATA ---
            if self.STAGE_METADATA in self.active_stages:
                if self._stop_event.is_set():
                    return

                if not self.scanned_files and self.STAGE_SCAN not in self.active_stages:
                    self._post_status("Skipping metadata: No files scanned.")
                elif self.scanned_files:
                    self._post_status("Starting metadata update...")

                    self.metadata_service.progress_updated.connect(self._on_metadata_progress)
                    self.metadata_service.file_updated.connect(self._on_metadata_file)

                    meta_options = {
                        "use_musicbrainz": self.options.get("use_musicbrainz", True),
                        "use_discogs": self.options.get("use_discogs", True),
                        "fetch_lyrics": self.options.get("fetch_lyrics", True),
                        "force_update": self.options.get("force_metadata_update", False),
                    }

                    # Update paths if files were moved
                    files_to_update = self.scanned_files
                    for f in files_to_update:
                        if "new_path" in f:
                            f["path"] = f["new_path"]

                    self.metadata_service.update_metadata(files_to_update, meta_options)

                    self.metadata_service.progress_updated.disconnect(self._on_metadata_progress)
                    self.metadata_service.file_updated.disconnect(self._on_metadata_file)

                    results["stages_completed"].append(self.STAGE_METADATA)
                    self._post_status("Metadata update completed.")

            results["success"] = True
            results["files_processed"] = len(self.scanned_files)

            self._post_status("Processing completed successfully")
            self._post_completed(results)

        except Exception as e:
            traceback.print_exc()
            self._post_status(f"Error: {str(e)}")
            self._post_completed({"error": str(e), "success": False})

    # --- Event Posting Helpers ---

    def _post_progress(self, stage, current, total):
        wx.PostEvent(self.window, ProgressEvent(stage=stage, current=current, total=total))

    def _post_status(self, message):
        wx.PostEvent(self.window, StatusEvent(message=message))

    def _post_file(self, file_path):
        wx.PostEvent(self.window, FileEvent(file_path=file_path))

    def _post_completed(self, results):
        wx.PostEvent(self.window, CompletionEvent(results=results))

    # --- Signal Handlers (Bridge) ---

    def _on_scan_progress(self, current, total):
        self._post_progress("Scanning", current, total)

    def _on_scan_file(self, file_path):
        self._post_file(f"Scanning: {file_path}")

    def _on_organize_progress(self, current, total):
        self._post_progress("Organizing", current, total)

    def _on_organize_file(self, src, dest):
        self._post_file(f"Organizing: {src} -> {dest}")

    def _on_metadata_progress(self, current, total):
        self._post_progress("Metadata", current, total)

    def _on_metadata_file(self, file_path):
        self._post_file(f"Updating metadata: {file_path}")
