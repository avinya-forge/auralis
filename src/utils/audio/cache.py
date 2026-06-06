import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class AudioCacheManager:
    """
    Manages cache for demixed audio chunks.
    Implements an LRU eviction policy to keep cache size under a limit.
    """

    def __init__(self, cache_dir: str, max_size_bytes: int = 1024 * 1024 * 500):
        """
        Initializes the cache manager.
        max_size_bytes: Default is 500MB.
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_bytes
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_files_with_stats(self) -> List[Tuple[Path, float, int]]:
        """Returns a list of (filepath, access_time, size)"""
        files = []
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    # Use st_atime for LRU, or st_mtime as fallback
                    files.append((file_path, stat.st_atime, stat.st_size))
                except OSError as e:
                    logger.warning(f"Could not stat {file_path}: {e}")
        return files

    def get_current_size(self) -> int:
        """Returns the total size of the cache in bytes."""
        files = self._get_files_with_stats()
        return sum(f[2] for f in files)

    def cleanup(self) -> int:
        """
        Evicts oldest accessed files until the cache is under max_size_bytes.
        Returns the number of bytes freed.
        """
        files = self._get_files_with_stats()
        total_size = sum(f[2] for f in files)

        if total_size <= self.max_size_bytes:
            return 0

        # Sort files by access time (oldest first)
        files.sort(key=lambda x: x[1])

        bytes_freed = 0
        bytes_to_free = total_size - self.max_size_bytes

        for file_path, _, size in files:
            if bytes_freed >= bytes_to_free:
                break
            try:
                file_path.unlink()
                bytes_freed += size
                logger.debug(f"Evicted {file_path} from cache ({size} bytes).")
            except OSError as e:
                logger.error(f"Failed to delete {file_path}: {e}")

        logger.info(f"Audio cache cleanup freed {bytes_freed} bytes.")
        return bytes_freed
