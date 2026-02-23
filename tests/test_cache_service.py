from unittest.mock import patch

import pytest

from src.services.cache_service import CacheService


class TestCacheService:

    @pytest.fixture
    def cache_service(self, tmp_path):
        # Patch Path.home() to return tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Reset singleton instance
            CacheService._instance = None
            service = CacheService()
            yield service
            service.close()
            CacheService._instance = None

    def test_singleton(self, cache_service):
        service2 = CacheService()
        assert cache_service is service2

    def test_save_get_metadata(self, cache_service):
        file_hash = "abc123hash"
        data = {"artist": "Test Artist", "title": "Test Title"}

        assert cache_service.save_metadata(file_hash, data)

        cached = cache_service.get_metadata(file_hash)
        assert cached == data
        assert cached["artist"] == "Test Artist"

    def test_get_nonexistent(self, cache_service):
        assert cache_service.get_metadata("nonexistent") is None

    def test_update_metadata(self, cache_service):
        file_hash = "abc123hash"
        data1 = {"artist": "Artist 1"}
        data2 = {"artist": "Artist 2"}

        cache_service.save_metadata(file_hash, data1)
        assert cache_service.get_metadata(file_hash) == data1

        cache_service.save_metadata(file_hash, data2)
        assert cache_service.get_metadata(file_hash) == data2

    def test_invalid_input(self, cache_service):
        assert not cache_service.save_metadata("", {})
        assert not cache_service.save_metadata(None, {})
        assert cache_service.get_metadata("") is None
        assert cache_service.get_metadata(None) is None
