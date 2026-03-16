from unittest.mock import patch
import time
import pytest
import sqlite3

from src.modules.perf.metadata_cache import MetadataCache


class TestMetadataCache:
    @pytest.fixture
    def metadata_cache(self, tmp_path):
        # Patch Path.home() to return tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Reset singleton instance
            MetadataCache._instance = None
            cache = MetadataCache()
            yield cache
            cache.close()
            MetadataCache._instance = None

    def test_singleton(self, metadata_cache):
        cache2 = MetadataCache()
        assert metadata_cache is cache2

    def test_save_get_metadata(self, metadata_cache):
        file_hash = "abc123hash"
        data = {"artist": "Test Artist", "title": "Test Title"}

        assert metadata_cache.set(file_hash, data)

        cached = metadata_cache.get(file_hash)
        assert cached == data
        assert cached["artist"] == "Test Artist"

    def test_get_nonexistent(self, metadata_cache):
        assert metadata_cache.get("nonexistent") is None

    def test_update_metadata(self, metadata_cache):
        file_hash = "abc123hash"
        data1 = {"artist": "Artist 1"}
        data2 = {"artist": "Artist 2"}

        metadata_cache.set(file_hash, data1)
        assert metadata_cache.get(file_hash) == data1

        metadata_cache.set(file_hash, data2)
        assert metadata_cache.get(file_hash) == data2

    def test_invalid_input(self, metadata_cache):
        assert not metadata_cache.set("", {})
        assert not metadata_cache.set(None, {})
        assert metadata_cache.get("") is None
        assert metadata_cache.get(None) is None

    @patch("time.time")
    def test_ttl_expiration_lazy(self, mock_time, metadata_cache):
        # Set current time
        current_time = 1000000.0
        mock_time.return_value = current_time

        file_hash = "ttl_hash"
        data = {"artist": "TTL Artist"}

        assert metadata_cache.set(file_hash, data)

        # Still valid right after setting
        assert metadata_cache.get(file_hash) == data

        # Fast forward time beyond 7 days
        mock_time.return_value = current_time + MetadataCache.TTL_SECONDS + 10

        # Should return None because it is expired
        assert metadata_cache.get(file_hash) is None

        # Record should also be removed from DB
        with sqlite3.connect(metadata_cache.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM metadata WHERE hash = ?", (file_hash,))
            count = cursor.fetchone()[0]
            assert count == 0

    @patch("time.time")
    def test_clean_expired(self, mock_time, metadata_cache):
        current_time = 1000000.0
        mock_time.return_value = current_time

        # Set first item (will be expired)
        metadata_cache.set("hash_old", {"artist": "Old"})

        # Move time forward by 8 days
        mock_time.return_value = current_time + (8 * 24 * 60 * 60)

        # Set second item (will be fresh)
        metadata_cache.set("hash_new", {"artist": "New"})

        # Now clean expired
        metadata_cache.clean_expired()

        # Try to retrieve them directly from DB without triggering lazy delete
        import sqlite3
        with sqlite3.connect(metadata_cache.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM metadata")
            rows = cursor.fetchall()

        # Only hash_new should remain
        hashes = [row[0] for row in rows]
        assert "hash_old" not in hashes
        assert "hash_new" in hashes
