"""
Unit tests for wxPython WorkerThread
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx before importing module under test
# This is necessary because wx is not installed
if "wx" not in sys.modules:
    mock_wx = MagicMock()
    mock_wx.lib = MagicMock()
    mock_wx.lib.newevent = MagicMock()

    # Mock NewEvent to return (EventClass, Binder)
    def mock_new_event():
        class Event:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        return Event, MagicMock()

    mock_wx.lib.newevent.NewEvent = mock_new_event
    mock_wx.PostEvent = MagicMock()

    sys.modules["wx"] = mock_wx
    sys.modules["wx.lib"] = mock_wx.lib
    sys.modules["wx.lib.newevent"] = mock_wx.lib.newevent

# Mock requests before importing module under test
if "requests" not in sys.modules:
    sys.modules["requests"] = MagicMock()

if "PIL" not in sys.modules:
    sys.modules["PIL"] = MagicMock()
    sys.modules["PIL.Image"] = MagicMock()

if "bs4" not in sys.modules:
    sys.modules["bs4"] = MagicMock()

# We do NOT mock core services in sys.modules anymore to avoid polluting other tests.
# Instead, we rely on patch.multiple to replace them in the worker module.

# However, we must ensure imports succeed.
# If src.core.scanner fails to import (e.g. missing dependencies), we might have issues.
# But dependencies are installed now.

from src.gui.wx.worker import WorkerThread


class TestWxWorkerThread(unittest.TestCase):

    def setUp(self):
        self.mock_window = MagicMock()
        self.mock_monitor = MagicMock()

        # Setup mocks for services
        self.mock_scanner = MagicMock()
        self.mock_scanner.progress_updated = MagicMock()
        self.mock_scanner.file_scanned = MagicMock()

        async def mock_scan(*args, **kwargs):
            return [{"path": "test.mp3"}]
        self.mock_scanner.scan_directories.side_effect = mock_scan

        self.mock_organizer = MagicMock()
        self.mock_organizer.progress_updated = MagicMock()
        self.mock_organizer.file_organized = MagicMock()
        self.mock_organizer.organize_files.return_value = {}

        self.mock_metadata = MagicMock()
        self.mock_metadata.progress_updated = MagicMock()
        self.mock_metadata.file_updated = MagicMock()
        self.mock_metadata.update_metadata.return_value = []

        # Patch the classes in the module
        patcher = patch.multiple(
            "src.gui.wx.worker",
            MusicScanner=MagicMock(return_value=self.mock_scanner),
            MusicOrganizer=MagicMock(return_value=self.mock_organizer),
            MetadataService=MagicMock(return_value=self.mock_metadata),
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_run_scan_stage(self):
        worker = WorkerThread(
            window=self.mock_window,
            source_dirs=["/src"],
            dest_dir="/dest",
            options={},
            system_monitor=self.mock_monitor,
            start_stage=1,
            end_stage=1,
        )

        worker.run()

        self.mock_scanner.scan_directories.assert_called_once()
        self.mock_organizer.organize_files.assert_not_called()
        self.mock_metadata.update_metadata.assert_not_called()

        # Check if events were posted
        # We expect at least start status, completion status, and result
        # Note: We need to access the mock_wx from sys.modules or use the global one we defined
        mock_wx_module = sys.modules["wx"]
        self.assertTrue(mock_wx_module.PostEvent.called)

    def test_run_all_stages(self):
        worker = WorkerThread(
            window=self.mock_window,
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

    def test_stop(self):
        worker = WorkerThread(
            window=self.mock_window,
            source_dirs=["/src"],
            dest_dir="/dest",
            options={},
            system_monitor=self.mock_monitor,
        )

        worker.stop()
        self.assertTrue(worker._stop_event.is_set())

        # If stopped before run, it should check flag
        worker.run()

        # Should return immediately because of stop flag check at start of stage 1
        self.mock_scanner.scan_directories.assert_not_called()

    def test_bridge_scan_progress(self):
        worker = WorkerThread(self.mock_window, [], "", {}, self.mock_monitor)

        worker._on_scan_progress(5, 10)

        # Check if PostEvent called
        mock_wx_module = sys.modules["wx"]
        args, _ = mock_wx_module.PostEvent.call_args
        event = args[1]
        self.assertEqual(event.current, 5)
        self.assertEqual(event.total, 10)
        self.assertEqual(event.stage, "Scanning")

    def test_active_stages(self):
        worker = WorkerThread(
            window=self.mock_window,
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
