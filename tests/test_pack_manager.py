from pathlib import Path
from typing import Any

from src.services.cache.pack_manager import PackManager


def test_pack_manager_compress_decompress() -> None:
    manager = PackManager()
    metadata = {"artist": "Test Artist", "title": "Test Title", "tags": ["jazz", "upbeat"]}

    compressed = manager.compress_pack(metadata)
    assert compressed is not None
    assert isinstance(compressed, bytes)

    decompressed = manager.decompress_pack(compressed)
    assert decompressed == metadata


def test_pack_manager_save_load(tmp_path: Path) -> None:
    manager = PackManager()
    metadata = {"key": "value"}
    pack_path = tmp_path / "test_pack.bin"

    success = manager.save_pack(metadata, str(pack_path))
    assert success is True
    assert pack_path.exists()

    loaded = manager.load_pack(str(pack_path))
    assert loaded == metadata


def test_pack_manager_corrupted_data() -> None:
    manager = PackManager()
    decompressed = manager.decompress_pack(b"corrupted_zlib_data")
    assert decompressed is None
