import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Need to run without real PyQt objects in test mode as the environment
# globally patches QThread and QPixmap making testing hard
import tests.conftest

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem

# Initialize QApplication before any tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from src.gui.pyqt.lazy_loader import ImageLoadWorker, LazyLoader


class TestImageLoadWorker(unittest.TestCase):
    def setUp(self):
        # We patch QThread directly for the worker tests so we don't have to deal with thread mocks
        self.qthread_patcher = patch('src.gui.pyqt.lazy_loader.QThread')
        self.mock_qthread = self.qthread_patcher.start()

        self.worker = ImageLoadWorker()
        # Mock msleep and wait to avoid PyQt actual calls
        self.worker.msleep = MagicMock()
        self.worker.wait = MagicMock()

    def tearDown(self):
        self.qthread_patcher.stop()

    def test_add_task(self):
        """Test adding tasks to the worker."""
        # Add new task
        self.worker.add_task("file1.mp3")
        self.assertIn("file1.mp3", self.worker._queue)

        # Add same task again (should be ignored)
        self.worker.add_task("file1.mp3")
        self.assertEqual(len(self.worker._queue), 1)

    @patch('src.gui.pyqt.lazy_loader.get_album_art')
    def test_run_loads_image(self, mock_get_album_art):
        """Test the run method loading an image from a file."""
        self.worker.image_loaded = MagicMock()

        # Set up mocks
        mock_get_album_art.return_value = b"fake_image_data"

        self.worker._queue.append("test.mp3")

        with patch.object(self.worker, 'msleep', side_effect=Exception("StopLoop")):
            try:
                self.worker.run()
            except Exception as e:
                if str(e) != "StopLoop":
                    raise

        # Check that it extracted the image
        mock_get_album_art.assert_called_once_with("test.mp3")

        # Check signal
        self.worker.image_loaded.emit.assert_called_once()
        self.assertEqual(self.worker.image_loaded.emit.call_args[0][0], "test.mp3")
        self.assertEqual(self.worker.image_loaded.emit.call_args[0][1], b"fake_image_data")

    @patch('src.gui.pyqt.lazy_loader.get_album_art')
    def test_run_exception(self, mock_get_album_art):
        """Test the run method handling exceptions."""
        mock_get_album_art.side_effect = Exception("File not found")

        self.worker._queue.append("error.mp3")

        with patch('builtins.print') as mock_print:
            with patch.object(self.worker, 'msleep', side_effect=Exception("StopLoop")):
                try:
                    self.worker.run()
                except Exception as e:
                    if str(e) != "StopLoop":
                        raise

            mock_print.assert_called_once()
            self.assertIn("Failed to load album art", mock_print.call_args[0][0])
            self.assertIn("error.mp3", mock_print.call_args[0][0])

    def test_stop(self):
        """Test stop method"""
        with patch.object(self.worker, 'wait') as mock_wait:
            self.worker.stop()
            self.assertFalse(self.worker._is_running)
            mock_wait.assert_called_once()


class TestLazyLoader(unittest.TestCase):
    @patch('src.gui.pyqt.lazy_loader.ImageLoadWorker')
    def setUp(self, MockWorker):
        self.list_widget = MagicMock()
        self.list_widget.count.return_value = 0
        self.mock_worker_instance = MockWorker.return_value
        self.loader = LazyLoader(self.list_widget)
        self.loader.worker = self.mock_worker_instance

    def tearDown(self):
        self.loader.stop()

    def test_add_item(self):
        """Test adding an item to the loader."""
        with patch.object(self.loader, '_check_visible_items') as mock_check:
            with patch('src.gui.pyqt.lazy_loader.QListWidgetItem') as mock_item_class:
                mock_item = mock_item_class.return_value

                item = self.loader.add_item("test.mp3", "Test Track")

                # Check item added to list widget
                self.list_widget.addItem.assert_called_once_with(mock_item)

                # Check data stored correctly
                mock_item.setData.assert_called_once_with(100, "test.mp3")

                # Check internal dict
                self.assertIn("test.mp3", self.loader._items)
                self.assertEqual(self.loader._items["test.mp3"], item)

                # Check trigger
                mock_check.assert_called_once()

    def test_check_visible_items_empty(self):
        """Test checking visible items when list is empty."""
        self.list_widget.count.return_value = 0
        self.loader._check_visible_items()
        self.mock_worker_instance.add_task.assert_not_called()

    def test_check_visible_items(self):
        """Test checking visible items."""
        self.list_widget.count.return_value = 1

        # Mock view methods
        self.list_widget.indexAt = MagicMock()
        mock_index = MagicMock()
        mock_index.row.return_value = 0
        self.list_widget.indexAt.return_value = mock_index

        mock_item = MagicMock()
        mock_item.data.return_value = "test1.mp3"
        mock_item.icon().isNull.return_value = True
        self.list_widget.item.return_value = mock_item

        self.loader._check_visible_items()
        self.mock_worker_instance.add_task.assert_called_once_with("test1.mp3")

    def test_check_visible_items_has_icon(self):
        """Test checking visible items when icon already exists."""
        self.list_widget.count.return_value = 1

        # Mock view methods
        self.list_widget.indexAt = MagicMock()
        mock_index = MagicMock()
        mock_index.row.return_value = 0
        self.list_widget.indexAt.return_value = mock_index

        mock_item = MagicMock()
        mock_item.data.return_value = "test1.mp3"
        mock_item.icon().isNull.return_value = False
        self.list_widget.item.return_value = mock_item

        self.loader._check_visible_items()
        self.mock_worker_instance.add_task.assert_not_called()

    def test_check_visible_items_with_cache(self):
        """Test checking visible items when it is already in cache."""
        self.list_widget.count.return_value = 1

        # Add to cache
        mock_pixmap = MagicMock()
        self.loader._cache["test1.mp3"] = mock_pixmap

        # Mock view methods
        self.list_widget.indexAt = MagicMock()
        mock_index = MagicMock()
        mock_index.row.return_value = 0
        self.list_widget.indexAt.return_value = mock_index

        mock_item = MagicMock()
        mock_item.data.return_value = "test1.mp3"
        mock_item.icon().isNull.return_value = True
        self.list_widget.item.return_value = mock_item

        with patch.object(self.loader, '_apply_pixmap') as mock_apply:
            self.loader._check_visible_items()

            # Since it's in cache, we shouldn't add task
            self.mock_worker_instance.add_task.assert_not_called()
            # We should apply directly
            mock_apply.assert_called_once_with("test1.mp3", mock_pixmap)

    def test_on_image_loaded(self):
        """Test handling a loaded image data."""
        mock_item = MagicMock()
        self.loader._items["test1.mp3"] = mock_item

        with patch('src.gui.pyqt.lazy_loader.QPixmap') as mock_pixmap_class:
            mock_pixmap = mock_pixmap_class.return_value
            mock_pixmap.loadFromData.return_value = True

            with patch.object(self.loader, '_apply_pixmap') as mock_apply:
                self.loader._on_image_loaded("test1.mp3", b"image_data")

                mock_pixmap.loadFromData.assert_called_once_with(b"image_data")
                mock_apply.assert_called_once_with("test1.mp3", mock_pixmap)

                # Check cache updated
                self.assertIn("test1.mp3", self.loader._cache)
                self.assertEqual(self.loader._cache["test1.mp3"], mock_pixmap)

    def test_apply_pixmap(self):
        """Test applying a pixmap to an item."""
        mock_item = MagicMock()
        self.loader._items["test1.mp3"] = mock_item

        mock_pixmap = MagicMock()
        mock_scaled_pixmap = MagicMock()
        mock_pixmap.scaled.return_value = mock_scaled_pixmap

        with patch('src.gui.pyqt.lazy_loader.QIcon') as mock_icon_class:
            mock_icon = mock_icon_class.return_value

            self.loader._apply_pixmap("test1.mp3", mock_pixmap)

            mock_pixmap.scaled.assert_called_once_with(64, 64)
            mock_icon_class.assert_called_once_with(mock_scaled_pixmap)
            mock_item.setIcon.assert_called_once_with(mock_icon)

    def test_apply_pixmap_unknown_item(self):
        """Test handling a loaded image for an unknown item."""
        mock_pixmap = MagicMock()

        # Should not crash
        self.loader._apply_pixmap("unknown.mp3", mock_pixmap)

    def test_stop(self):
        """Test stopping the loader."""
        self.loader.stop()
        self.mock_worker_instance.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
