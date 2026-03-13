import os
from unittest.mock import patch

import pytest
from PyQt6.QtCore import QCoreApplication

from src.core.scanner import MusicScanner


@pytest.fixture(scope="session")
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


class TestScannerOptions:
    @pytest.fixture
    def scanner(self, qapp):
        return MusicScanner()

    def test_update_options_extensions(self, scanner):
        options = {"file_extensions": "mp3,wav"}
        scanner._update_options(options)
        assert ".mp3" in scanner.supported_extensions
        assert ".wav" in scanner.supported_extensions

        assert ".flac" not in scanner.supported_extensions

        options = {"file_extensions": [".aac", ".ogg"]}
        scanner._update_options(options)
        assert ".aac" in scanner.supported_extensions
        assert ".ogg" in scanner.supported_extensions
        assert ".mp3" not in scanner.supported_extensions

    def test_update_options_exclude(self, scanner):
        options = {"exclude_patterns": "test,dummy"}
        scanner._update_options(options)
        assert "test" in scanner.exclude_patterns
        assert "dummy" in scanner.exclude_patterns

        options = {"exclude_patterns": ["foo", "bar"]}
        scanner._update_options(options)
        assert "foo" in scanner.exclude_patterns
        assert "bar" in scanner.exclude_patterns

    def test_update_options_depth(self, scanner):
        options = {"max_scan_depth": "5"}
        scanner._update_options(options)
        assert scanner.max_scan_depth == 5

    def test_scan_depth_limit(self, scanner, tmp_path):
        # Create structure: root/d1/song.mp3
        d1 = tmp_path / "d1"
        d1.mkdir()
        (d1 / "song.mp3").write_text("content")

        with patch.object(scanner, "_extract_file_info") as mock_extract:
            mock_extract.return_value = {
                "path": str(d1 / "song.mp3"),
                "filename": "song.mp3",
                "extension": ".mp3",
                "size": 7,
                "hash": "hash",
                "metadata": {},
            }

            # Set max depth 0 (only root)
            scanner.max_scan_depth = 0
            import asyncio

            results = asyncio.run(scanner.scan_directories([str(tmp_path)]))
            assert len(results) == 0

            # Set max depth 1
            scanner.max_scan_depth = 1
            results = asyncio.run(scanner.scan_directories([str(tmp_path)]))
            assert len(results) == 1

    def test_scan_depth_limit_coverage(self, scanner, tmp_path):
        # Create structure: root/root_song.mp3 and root/d1/nested_song.mp3
        (tmp_path / "root_song.mp3").write_text("content")
        d1 = tmp_path / "d1"
        d1.mkdir()
        (d1 / "nested_song.mp3").write_text("content")

        with patch.object(scanner, "_extract_file_info") as mock_extract:
            mock_extract.side_effect = lambda p: {
                "path": p,
                "filename": os.path.basename(p),
                "extension": ".mp3",
                "size": 7,
                "hash": "hash",
                "metadata": {},
            }

            # Set max depth 0 (only root)
            scanner.max_scan_depth = 0
            import asyncio

            results = asyncio.run(scanner.scan_directories([str(tmp_path)]))

            # Should find root_song.mp3 but NOT nested_song.mp3
            assert len(results) == 1
            assert "root_song.mp3" in results[0]["filename"]
