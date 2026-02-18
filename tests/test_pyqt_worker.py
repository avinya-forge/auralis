"""
Unit tests for PyQt6 WorkerThread
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure PyQt6 is mocked if not present
if "PyQt6" not in sys.modules:
    mock_pyqt6 = MagicMock()
    mock_qtcore = MagicMock()

    class MockQThread:
        def __init__(self, parent=None):
            pass

        def start(self):
            self.run()

        def wait(self):
            pass

    class MockSignal:
        def __init__(self, *args):
            self.callbacks = []

        def connect(self, callback):
            self.callbacks.append(callback)

        def disconnect(self, callback):
            if callback in self.callbacks:
                self.callbacks.remove(callback)

        def emit(self, *args):
            for cb in self.callbacks:
                cb(*args)

    mock_qtcore.QThread = MockQThread
    mock_qtcore.pyqtSignal = MockSignal

    sys.modules["PyQt6"] = mock_pyqt6
    sys.modules["PyQt6.QtCore"] = mock_qtcore

# We rely on imported modules being real (or patched locally), not globally mocked in sys.modules
# unless absolutely necessary (like PyQt6/wx if missing).

from src.gui.pyqt.worker import WorkerThread


class TestPyQtWorkerThread(unittest.TestCase):

    def setUp(self):
        # Setup mocks for services
        self.mock_scanner = MagicMock()
        self.mock_scanner.progress_updated = MagicMock()
        self.mock_scanner.file_scanned = MagicMock()
        self.mock_scanner.scan_directories.return_value = [{"path": "test.mp3"}]

        self.mock_organizer = MagicMock()
        self.mock_organizer.progress_updated = MagicMock()
        self.mock_organizer.file_organized = MagicMock()
        self.mock_organizer.organize_files.return_value = {}

        self.mock_metadata = MagicMock()
        self.mock_metadata.progress_updated = MagicMock()
        self.mock_metadata.file_updated = MagicMock()
        self.mock_metadata.update_metadata.return_value = []

        # Patch classes
        self.patcher = patch.multiple(
            "src.gui.pyqt.worker",
            MusicScanner=MagicMock(return_value=self.mock_scanner),
            MusicOrganizer=MagicMock(return_value=self.mock_organizer),
            MetadataService=MagicMock(return_value=self.mock_metadata),
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

        # Mock monitor
        self.mock_monitor = MagicMock()

    def test_run_scan_stage(self):
        worker = WorkerThread(
            source_dirs=["/src"],
            dest_dir="/dest",
            options={},
            system_monitor=self.mock_monitor,
            start_stage=1,
            end_stage=1,
        )

        # Connect signals to verify emission
        mock_status = MagicMock()
        worker.status_updated.connect(mock_status)

        worker.run()

        self.mock_scanner.scan_directories.assert_called_once()
        self.mock_organizer.organize_files.assert_not_called()
        self.mock_metadata.update_metadata.assert_not_called()

        self.assertTrue(mock_status.called)

    def test_run_all_stages(self):
        worker = WorkerThread(
            source_dirs=["/src"],
            dest_dir="/dest",
            options={},
            system_monitor=self.mock_monitor,
            start_stage=1,
            end_stage=3,
        )

        worker.run()

        self.mock_scanner.scan_directories.assert_called_once()
        self.mock_organizer.organize_files.assert_called_once()
        self.mock_metadata.update_metadata.assert_called_once()

    def test_signal_bridge(self):
        worker = WorkerThread([], "", {}, self.mock_monitor)

        mock_progress = MagicMock()
        worker.progress_updated.connect(mock_progress)

        worker._on_scan_progress(10, 100)

        mock_progress.assert_called_with("Scanning", 10, 100)

    def test_active_stages(self):
        # Test active_stages=[1, 3] (Skip Organize)
        worker = WorkerThread(
            source_dirs=["/src"],
            dest_dir="/dest",
            options={},
            system_monitor=self.mock_monitor,
            active_stages=[1, 3],
        )

        worker.run()

        self.mock_scanner.scan_directories.assert_called_once()
        self.mock_organizer.organize_files.assert_not_called()
        self.mock_metadata.update_metadata.assert_called_once()
