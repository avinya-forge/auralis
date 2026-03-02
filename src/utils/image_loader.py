"""
Auralis - Image Loader Utility

This module provides a lazy image loader using QThreadPool to load images
in the background without freezing the UI.
"""

import os
from typing import Callable, Dict, Optional

import requests  # type: ignore
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage


class ImageLoaderSignals(QObject):
    """Signals for the ImageLoader runnable."""

    loaded = pyqtSignal(object)  # Emits QImage
    error = pyqtSignal(str)


class ImageRunnable(QRunnable):
    """Runnable task to load an image."""

    def __init__(self, path_or_url: str) -> None:
        """Initialize the runnable."""
        super().__init__()
        self.path_or_url = path_or_url
        self.signals = ImageLoaderSignals()

    @pyqtSlot()
    def run(self) -> None:
        """Execute the task."""
        try:
            image = QImage()
            if self.path_or_url.startswith("http"):
                # Load from URL
                response = requests.get(self.path_or_url, timeout=10)
                response.raise_for_status()
                image.loadFromData(response.content)
            else:
                # Load from local path
                if os.path.exists(self.path_or_url):
                    image.load(self.path_or_url)
                else:
                    self.signals.error.emit(f"File not found: {self.path_or_url}")
                    return

            if not image.isNull():
                self.signals.loaded.emit(image)
            else:
                self.signals.error.emit(f"Failed to load image: {self.path_or_url}")

        except Exception as e:
            self.signals.error.emit(str(e))


class ImageLoader:
    """
    Lazy loader for images.
    """

    def __init__(self) -> None:
        """Initialize the ImageLoader."""
        self.thread_pool = QThreadPool.globalInstance()
        self.cache: Dict[str, QImage] = {}

    def load_image(self, path_or_url: str, callback: Callable[[Optional[QImage]], None]) -> None:
        """
        Load an image from a path or URL.

        Args:
            path_or_url (str): The path or URL of the image.
            callback (Callable): Function to call with the loaded QImage (or None on failure).
        """
        if not path_or_url:
            callback(None)
            return

        # Check cache
        if path_or_url in self.cache:
            callback(self.cache[path_or_url])
            return

        # Create runnable
        runnable = ImageRunnable(path_or_url)

        # Connect signals
        # We need to use a slot/method to capture the callback context safely
        runnable.signals.loaded.connect(lambda img: self._on_loaded(path_or_url, img, callback))
        runnable.signals.error.connect(lambda err: self._on_error(err, callback))

        # Start task
        self.thread_pool.start(runnable)

    def _on_loaded(
        self, path: str, image: QImage, callback: Callable[[Optional[QImage]], None]
    ) -> None:
        """Handle successful load."""
        self.cache[path] = image
        callback(image)

    def _on_error(self, error: str, callback: Callable[[Optional[QImage]], None]) -> None:
        """Handle load error."""
        # print(f"Image load error: {error}")
        callback(None)
