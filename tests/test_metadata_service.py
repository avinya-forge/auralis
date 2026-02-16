import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock dependencies
if "musicbrainzngs" not in sys.modules:
    sys.modules["musicbrainzngs"] = MagicMock()
if "acoustid" not in sys.modules:
    sys.modules["acoustid"] = MagicMock()
if "discogs_client" not in sys.modules:
    sys.modules["discogs_client"] = MagicMock()
if "mutagen" not in sys.modules:
    sys.modules["mutagen"] = MagicMock()
if "requests" not in sys.modules:
    sys.modules["requests"] = MagicMock()

# Mock PyQt6
if "PyQt6" not in sys.modules:
    mock_pyqt6 = MagicMock()
    mock_qtcore = MagicMock()

    # Mock QObject
    class MockQObject:
        def __init__(self, parent=None):
            pass

    # Mock pyqtSignal
    class MockSignal:
        def __init__(self, *args, **kwargs):
            self.slots = []

        def connect(self, slot):
            self.slots.append(slot)

        def emit(self, *args):
            for slot in self.slots:
                slot(*args)

    mock_qtcore.QObject = MockQObject
    mock_qtcore.pyqtSignal = MockSignal

    mock_pyqt6.QtCore = mock_qtcore

    sys.modules["PyQt6"] = mock_pyqt6
    sys.modules["PyQt6.QtCore"] = mock_qtcore

# Import the service module
from src.services.metadata_service import (
    DiscogsSource,
    MetadataService,
    MusicBrainzSource,
)


class TestMusicBrainzSource:
    @pytest.fixture
    def mb_source(self):
        """Create a MusicBrainzSource instance with mocks"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.return_code = 0
            return MusicBrainzSource()

    def test_init(self, mb_source):
        """Test initialization"""
        assert mb_source.name == "MusicBrainz/AcoustID"
        assert mb_source.enabled is True

    @patch("acoustid.fingerprint_file")
    @patch("acoustid.lookup")
    @patch("musicbrainzngs.get_recording_by_id")
    def test_get_metadata_fingerprint_success(
        self, mock_mb_get, mock_acoustid_lookup, mock_fingerprint, mb_source
    ):
        """Test successful metadata retrieval via fingerprint"""
        # Mock fingerprinting
        mb_source.fingerprinting_available = True
        mock_fingerprint.return_value = (100, "encoded_fp")

        # Mock AcoustID lookup
        mock_acoustid_lookup.return_value = [
            {
                "recordings": [
                    {"id": "mbid1", "title": "Test Title", "artists": [{"name": "Test Artist"}]}
                ]
            }
        ]

        # Mock MusicBrainz lookup
        mock_mb_get.return_value = {
            "recording": {
                "artist-credit": [{"artist": {"name": "Test Artist"}}],
                "release-list": [{"title": "Test Album", "date": "2023-01-01"}],
            }
        }

        file_info = {"path": "/path/to/file.mp3", "metadata": {}}
        metadata, success, _ = mb_source.get_metadata(file_info)

        assert success is True
        assert metadata["title"] == "Test Title"
        assert metadata["artist"] == "Test Artist"
        assert metadata["album"] == "Test Album"
        assert metadata["year"] == "2023"

    @patch("musicbrainzngs.search_recordings")
    def test_get_metadata_search_fallback(self, mock_search, mb_source):
        """Test fallback to search when fingerprinting fails or is unavailable"""
        mb_source.fingerprinting_available = False

        # Mock search results
        mock_search.return_value = {
            "recording-list": [
                {
                    "title": "Search Title",
                    "artist-credit": [{"artist": {"name": "Search Artist"}}],
                    "release-list": [{"title": "Search Album", "date": "2022-01-01"}],
                }
            ]
        }

        file_info = {
            "path": "/path/to/file.mp3",
            "metadata": {"artist": "Artist", "title": "Title"},
        }
        metadata, success, _ = mb_source.get_metadata(file_info)

        assert success is True
        assert metadata["title"] == "Search Title"
        assert metadata["artist"] == "Search Artist"
        assert metadata["album"] == "Search Album"
        assert metadata["year"] == "2022"


class TestDiscogsSource:
    @pytest.fixture
    def discogs_source(self):
        """Create a DiscogsSource instance with mocks"""
        with patch("discogs_client.Client") as mock_client:
            source = DiscogsSource()
            source.client = mock_client.return_value
            return source

    def test_init(self, discogs_source):
        """Test initialization"""
        assert discogs_source.name == "Discogs"
        assert discogs_source.available is True

    def test_get_metadata_success(self, discogs_source):
        """Test successful metadata retrieval via Discogs"""
        # Mock search results
        mock_release = MagicMock()
        mock_release.title = "Discogs Artist - Discogs Title"
        mock_release.artists = [MagicMock(name="Discogs Artist")]
        mock_release.year = 2021
        mock_release.genres = ["Pop"]

        discogs_source.client.search.return_value = [mock_release]

        # Use partial metadata to trigger Discogs filling in the gaps
        file_info = {"path": "/path/to/file.mp3", "metadata": {"artist": "Artist"}}
        metadata, success, _ = discogs_source.get_metadata(file_info)

        assert success is True
        assert metadata["title"] == "Discogs Title"
        # Artist is already in metadata, so DiscogsSource doesn't return it
        # assert metadata["artist"] == "Discogs Artist"
        assert metadata["year"] == "2021"
        assert metadata["genre"] == "Pop"


class TestMetadataService:
    @pytest.fixture
    def service(self):
        """Create a MetadataService instance"""
        # Patch init methods to avoid real network/file calls
        with patch.object(MetadataService, "_init_sources"), patch.object(
            MetadataService, "_load_stats"
        ):
            service = MetadataService()
            # Manually add mock sources
            service.sources = {}
            service.source_order = []
            return service

    def test_detect_language(self, service):
        """Test language detection based on genre"""
        music_files = [
            {"metadata": {"genre": "J-Pop"}, "path": "1.mp3"},
            {"metadata": {"genre": "K-Pop"}, "path": "2.mp3"},
            {"metadata": {"genre": "Mandopop"}, "path": "3.mp3"},
            {"metadata": {"genre": "Bollywood"}, "path": "4.mp3"},
            {"metadata": {"genre": "Latin"}, "path": "5.mp3"},
            {"metadata": {"genre": "Chanson"}, "path": "6.mp3"},
            {"metadata": {"genre": "Schlager"}, "path": "7.mp3"},
            {"metadata": {"genre": "Instrumental"}, "path": "8.mp3"},
            {"metadata": {"genre": "Rock"}, "path": "9.mp3"},
        ]

        result = service.detect_language(music_files)

        assert result[0]["metadata"]["language"] == "Japanese"
        assert result[1]["metadata"]["language"] == "Korean"
        assert result[2]["metadata"]["language"] == "Chinese"
        assert result[3]["metadata"]["language"] == "Hindi"
        assert result[4]["metadata"]["language"] == "Spanish"
        assert result[5]["metadata"]["language"] == "French"
        assert result[6]["metadata"]["language"] == "German"
        assert result[7]["metadata"]["language"] == "Instrumental"
        assert result[8]["metadata"]["language"] == "English"
