import os
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QThreadPool

# Mock QImage before importing ImageLoader if possible
with patch("PyQt6.QtGui.QImage"):
    from src.utils.image_loader import ImageLoader, ImageRunnable


class TestImageLoader:

    @pytest.fixture
    def mock_signals(self):
        """Fixture to mock ImageLoaderSignals with working connect/emit."""
        with patch("src.utils.image_loader.ImageLoaderSignals") as MockSignals:
            instance = MockSignals.return_value

            # Setup signal logic
            instance.loaded = MagicMock()
            instance.error = MagicMock()

            instance.callbacks = {}

            def make_connect(name):
                def connect(callback):
                    instance.callbacks[name] = callback
                return connect

            def make_emit(name):
                def emit(arg):
                    if name in instance.callbacks:
                        instance.callbacks[name](arg)
                return emit

            instance.loaded.connect.side_effect = make_connect("loaded")
            instance.loaded.emit.side_effect = make_emit("loaded")
            instance.error.connect.side_effect = make_connect("error")
            instance.error.emit.side_effect = make_emit("error")

            yield MockSignals

    @pytest.fixture
    def image_loader(self, mock_signals):
        # No patch needed, conftest provides MockQThreadPool that runs synchronously
        loader = ImageLoader()
        yield loader

    def test_load_image_url(self, image_loader):
        print(f"DEBUG: thread_pool type: {type(image_loader.thread_pool)}")
        print(f"DEBUG: thread_pool start: {image_loader.thread_pool.start}")

        with patch("src.utils.image_loader.requests.get") as mock_get, \
             patch("src.utils.image_loader.QImage") as MockQImage:

            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            mock_image = MockQImage.return_value
            mock_image.loadFromData.return_value = True
            mock_image.isNull.return_value = False

            callback = MagicMock()
            image_loader.load_image("http://example.com/image.jpg", callback)

            mock_get.assert_called_with("http://example.com/image.jpg", timeout=10)
            callback.assert_called_once()
            args, _ = callback.call_args
            assert args[0] is mock_image

    def test_load_image_local(self, image_loader, tmp_path):
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")

        with patch("src.utils.image_loader.QImage") as MockQImage:
            mock_image = MockQImage.return_value
            mock_image.load.return_value = True
            mock_image.isNull.return_value = False

            callback = MagicMock()
            image_loader.load_image(str(image_path), callback)

            callback.assert_called_once()
            args, _ = callback.call_args
            assert args[0] is mock_image

    def test_load_image_error(self, image_loader):
        with patch("src.utils.image_loader.requests.get", side_effect=Exception("Network error")):
            callback = MagicMock()
            image_loader.load_image("http://example.com/bad.jpg", callback)

            callback.assert_called_with(None)

    def test_cache(self, image_loader):
        # Pre-populate cache
        mock_image = MagicMock()
        image_loader.cache["test.jpg"] = mock_image

        # We need to spy on start method since it's a real method on MockQThreadPool now
        with patch.object(image_loader.thread_pool, "start") as mock_start:
            callback = MagicMock()
            image_loader.load_image("test.jpg", callback)

            callback.assert_called_with(mock_image)
            mock_start.assert_not_called()
