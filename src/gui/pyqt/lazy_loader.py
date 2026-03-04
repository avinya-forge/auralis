from typing import Dict, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from src.utils.audio_utils import get_album_art


class ImageLoadWorker(QThread):
    """Background worker to extract and load album art from audio files."""

    # Emits: file_path, bytes
    image_loaded = pyqtSignal(str, bytes)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._queue: list[str] = []
        self._is_running = True

    def add_task(self, file_path: str) -> None:
        """Add a file to the loading queue."""
        if file_path not in self._queue:
            self._queue.append(file_path)

    def run(self) -> None:
        """Extract and load album art from files in the queue."""
        while self._is_running:
            if not self._queue:
                self.msleep(50)
                continue

            file_path = self._queue.pop(0)

            try:
                # Extract image using get_album_art
                image_data = get_album_art(file_path)

                if image_data:
                    self.image_loaded.emit(file_path, image_data)
            except Exception as e:
                print(f"Failed to load album art for {file_path}: {e}")

    def stop(self) -> None:
        """Stop the worker thread."""
        self._is_running = False
        self.wait()


class LazyLoader(QObject):
    """
    LazyLoader for QListWidget items.

    Automatically loads album art for items when they become visible,
    avoiding the need to load all images at once which improves performance.
    """

    def __init__(self, list_widget: QListWidget, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.list_widget = list_widget

        # Store items by their file path
        self._items: Dict[str, QListWidgetItem] = {}

        # Cache for loaded pixmaps
        self._cache: Dict[str, QPixmap] = {}

        # Setup worker thread
        self.worker = ImageLoadWorker(self)
        self.worker.image_loaded.connect(self._on_image_loaded)
        self.worker.start()

        # Connect to scrollbar to trigger loading when scrolling
        scrollbar = self.list_widget.verticalScrollBar()
        if scrollbar:
            scrollbar.valueChanged.connect(self._check_visible_items)

    def add_item(self, file_path: str, display_text: str) -> QListWidgetItem:
        """Add an item to the list widget with a placeholder icon."""
        item = QListWidgetItem(display_text)

        # We can store the filepath in the item's data to access it later
        item.setData(100, file_path)  # Qt.ItemDataRole.UserRole starts at 32

        self.list_widget.addItem(item)
        self._items[file_path] = item

        # Trigger an initial check
        self._check_visible_items()

        return item

    def _check_visible_items(self) -> None:
        """Check which items are currently visible and request their images."""
        if self.list_widget.count() == 0:
            return

        viewport = self.list_widget.viewport()
        if not viewport:
            return

        # Get visible rows
        top_row = self.list_widget.indexAt(viewport.rect().topLeft()).row()
        bottom_row = self.list_widget.indexAt(viewport.rect().bottomLeft()).row()

        if top_row < 0:
            top_row = 0

        if bottom_row < 0:
            bottom_row = self.list_widget.count() - 1

        # Add some buffer rows
        buffer = 5
        start_row = max(0, top_row - buffer)
        end_row = min(self.list_widget.count() - 1, bottom_row + buffer)

        # Queue images for visible items
        for row in range(start_row, end_row + 1):
            item = self.list_widget.item(row)
            if item:
                # Assuming role 100 stores the file path
                file_path = item.data(100)
                if file_path and isinstance(file_path, str):
                    # We check if item has empty icon
                    if item.icon().isNull():
                        # If we have it in cache, just use it
                        if file_path in self._cache:
                            self._apply_pixmap(file_path, self._cache[file_path])
                        else:
                            self.worker.add_task(file_path)

    def _on_image_loaded(self, file_path: str, image_data: bytes) -> None:
        """Handle when an image has been loaded by the worker."""
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data):
            self._cache[file_path] = pixmap
            self._apply_pixmap(file_path, pixmap)

    def _apply_pixmap(self, file_path: str, pixmap: QPixmap) -> None:
        """Apply a QPixmap to the correct list item."""
        if file_path in self._items:
            item = self._items[file_path]
            # Create a scaled icon from the pixmap
            # Scaled to a standard size for list items
            icon = QIcon(pixmap.scaled(64, 64))
            item.setIcon(icon)

    def stop(self) -> None:
        """Stop the worker thread."""
        if self.worker:
            self.worker.stop()
