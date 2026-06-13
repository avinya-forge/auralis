"""
data-002-1-pack-generator: Zlib compression for metadata music packs
"""

import json
import logging
import zlib
from pathlib import Path
from typing import Any, Dict, Optional, cast

logger = logging.getLogger(__name__)


class PackManager:
    """Manages metadata music packs using zlib compression."""

    def compress_pack(self, metadata: Dict[str, Any]) -> Optional[bytes]:
        """Compress metadata dict to zlib bytes."""
        try:
            json_data = json.dumps(metadata).encode("utf-8")
            return zlib.compress(json_data)
        except Exception as e:
            logger.error(f"Failed to compress pack: {e}")
            return None

    def decompress_pack(self, compressed_data: bytes) -> Optional[Dict[str, Any]]:
        """Decompress zlib bytes to metadata dict."""
        try:
            json_data = zlib.decompress(compressed_data).decode("utf-8")
            return cast(Dict[str, Any], json.loads(json_data))
        except Exception as e:
            logger.error(f"Failed to decompress pack: {e}")
            return None

    def save_pack(self, metadata: Dict[str, Any], filepath: str) -> bool:
        """Save a compressed pack to disk."""
        compressed = self.compress_pack(metadata)
        if compressed is None:
            return False

        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(compressed)
            return True
        except Exception as e:
            logger.error(f"Failed to write pack to {filepath}: {e}")
            return False

    def load_pack(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load a compressed pack from disk."""
        try:
            with open(filepath, "rb") as f:
                compressed_data = f.read()
            return self.decompress_pack(compressed_data)
        except Exception as e:
            logger.error(f"Failed to read pack from {filepath}: {e}")
            return None
