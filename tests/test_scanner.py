from unittest.mock import patch

import pytest

# Create a QCoreApplication instance for QObject signals
from PyQt6.QtCore import QCoreApplication

from src.core.scanner import MusicScanner


# We need a QApplication for QObject signals to work properly,
# although for simple instantiation it might not be strictly necessary,
# it's safer to have one.
@pytest.fixture(scope="session")
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


class TestMusicScanner:

    @pytest.fixture
    def scanner(self, qapp):
        return MusicScanner()

    def test_init(self, scanner):
        assert scanner.files == []
        assert ".mp3" in scanner.supported_extensions
        assert ".flac" in scanner.supported_extensions
        # Check for case insensitivity or normalization if applicable,
        # but the code uses a set of strings.

        # Default exclude patterns
        assert any("git" in p for p in scanner.exclude_patterns)

    def test_is_music_file(self, scanner):
        assert scanner._is_music_file("song.mp3")
        assert scanner._is_music_file("song.FLAC")
        assert not scanner._is_music_file("image.jpg")
        assert not scanner._is_music_file("song")

    def test_parse_filename(self, scanner):
        # "Artist - Title"
        artist, title = scanner._parse_filename("The Beatles - Hey Jude.mp3")
        assert artist == "The Beatles"
        assert title == "Hey Jude"

        # "Artist_-_Title"
        artist, title = scanner._parse_filename("Queen_-_Bohemian_Rhapsody.mp3")
        assert artist == "Queen"
        assert title == "Bohemian Rhapsody"

        # No pattern
        artist, title = scanner._parse_filename("UnknownSong.mp3")
        assert artist is None
        assert title is None

    def test_scan_directories_empty(self, scanner, tmp_path):
        results = scanner.scan_directories([str(tmp_path)])
        assert results == []

    def test_scan_directories_with_files(self, scanner, tmp_path):
        # Create a dummy music file
        music_file = tmp_path / "test_song.mp3"
        music_file.write_text("dummy content")

        # Mock _extract_file_info to avoid mutagen dependency during test
        # We need to mock it on the instance or class. Since scanner is an instance,
        # and _extract_file_info is an instance method.
        with patch.object(scanner, "_extract_file_info") as mock_extract:
            mock_extract.return_value = {
                "path": str(music_file),
                "filename": "test_song.mp3",
                "extension": ".mp3",
                "size": 100,
                "hash": "dummyhash",
                "metadata": {"title": "Test", "artist": "Artist"},
            }

            # Also mock _get_modification_time to avoid OS calls
            with patch.object(scanner, "_get_modification_time", return_value="2023-01-01"):
                results = scanner.scan_directories([str(tmp_path)])

            assert len(results) == 1
            assert results[0]["filename"] == "test_song.mp3"
            mock_extract.assert_called()

    def test_should_exclude_dir(self, scanner):
        # The method checks if directory starts with . or is in exclude patterns
        assert scanner._should_exclude_dir(".git")
        assert scanner._should_exclude_dir("node_modules")

        # Should not exclude standard directories
        assert not scanner._should_exclude_dir("Music")
        assert not scanner._should_exclude_dir("My Songs")
