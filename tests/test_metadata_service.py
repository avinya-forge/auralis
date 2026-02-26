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
if "spotipy" not in sys.modules:
    sys.modules["spotipy"] = MagicMock()
if "spotipy.oauth2" not in sys.modules:
    sys.modules["spotipy.oauth2"] = MagicMock()
if "pylast" not in sys.modules:
    sys.modules["pylast"] = MagicMock()

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
    LastFmSource,
    MetadataService,
    MusicBrainzSource,
    SpotifySource,
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


class TestSpotifySource:
    @pytest.fixture
    def spotify_source(self):
        """Create a SpotifySource instance with mocks"""
        with patch("src.services.metadata_service.HAS_SPOTIFY", True):
            with patch("src.services.metadata_service.spotipy", create=True) as mock_spotipy:
                with patch("src.services.metadata_service.SpotifyClientCredentials", create=True):
                    with patch("os.environ.get") as mock_env:
                        mock_env.return_value = "fake_cred"

                        source = SpotifySource()
                        # Manually attach client since the mock above handles the import,
                        # but we want to inspect the client in tests
                        source.client = mock_spotipy.Spotify.return_value
                        return source

    def test_init(self, spotify_source):
        """Test initialization"""
        assert spotify_source.name == "Spotify"
        assert spotify_source.available is True

    def test_get_metadata_success(self, spotify_source):
        """Test successful metadata retrieval via Spotify"""
        # Mock search results
        mock_track = {
            "name": "Spotify Title",
            "artists": [{"name": "Spotify Artist"}],
            "album": {"name": "Spotify Album", "release_date": "2023-05-05"},
        }

        spotify_source.client.search.return_value = {"tracks": {"items": [mock_track]}}

        file_info = {
            "path": "/path/to/file.mp3",
            "metadata": {"artist": "Artist", "title": "Title"},
        }
        metadata, success, _ = spotify_source.get_metadata(file_info)

        assert success is True
        assert metadata["title"] == "Spotify Title"
        assert metadata["artist"] == "Spotify Artist"
        assert metadata["album"] == "Spotify Album"
        assert metadata["year"] == "2023"


class TestLastFmSource:
    @pytest.fixture
    def lastfm_source(self):
        """Create a LastFmSource instance with mocks"""
        with patch("src.services.metadata_service.HAS_LASTFM", True):
            with patch("src.services.metadata_service.pylast", create=True) as mock_pylast:
                with patch("os.environ.get") as mock_env:
                    mock_env.return_value = "fake_cred"

                    source = LastFmSource()
                    source.network = mock_pylast.LastFMNetwork.return_value
                    return source

    def test_init(self, lastfm_source):
        """Test initialization"""
        assert lastfm_source.name == "Last.fm"
        assert lastfm_source.available is True

    def test_get_metadata_success(self, lastfm_source):
        """Test successful metadata retrieval via Last.fm"""
        # Mock track
        mock_track = MagicMock()
        mock_track.get_duration.return_value = 200000
        mock_tag = MagicMock()
        mock_tag.item.get_name.return_value = "rock"
        mock_track.get_top_tags.return_value = [mock_tag]

        mock_album = MagicMock()
        mock_album.get_name.return_value = "Last.fm Album"
        mock_track.get_album.return_value = mock_album

        lastfm_source.network.get_track.return_value = mock_track

        file_info = {
            "path": "/path/to/file.mp3",
            "metadata": {"artist": "Artist", "title": "Title"},
        }
        metadata, success, _ = lastfm_source.get_metadata(file_info)

        assert success is True
        assert metadata["genre"] == "Rock"
        assert metadata["album"] == "Last.fm Album"


class TestMetadataService:
    @pytest.fixture
    def service(self):
        """Create a MetadataService instance"""
        # Patch init methods to avoid real network/file calls
        with patch.object(MetadataService, "_init_sources"), patch.object(
            MetadataService, "_load_stats"
        ), patch("src.services.metadata_service.BioService"), patch(
            "src.services.metadata_service.AudioAnalyzer"
        ), patch(
            "src.services.metadata_service.CacheService"
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

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_update_metadata_concurrency(self, mock_executor_cls, service):
        """Test metadata update concurrency using ThreadPoolExecutor"""
        # Mock executor context manager
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        # Mock future
        mock_future = MagicMock()
        mock_future.result.return_value = {
            "path": "test.mp3",
            "metadata": {"title": "New Title"},
        }

        # Mock executor.submit
        mock_executor.submit.return_value = mock_future

        # Mock as_completed to yield our future
        with patch("concurrent.futures.as_completed", return_value=[mock_future]):
            # Prepare input
            music_files = [
                {"path": "test.mp3", "metadata": {"artist": "Artist"}, "hash": "h1"},
            ]
            options = {"force_update": True}

            # Patch internal methods to avoid side effects
            with patch.object(service, "_save_stats"):
                # Call update_metadata
                result = service.update_metadata(music_files, options)

                # Verify executor usage
                mock_executor_cls.assert_called_with(max_workers=4)
                assert mock_executor.submit.call_count == 1

                # Verify result update
                assert result[0]["metadata"]["title"] == "New Title"

    @patch("src.services.metadata_service.BioService")
    def test_finalize_file_update_with_bio(self, mock_bio_service_cls, service):
        """Test finalizing file update with bio fetching enabled"""
        # Setup mock bio service
        mock_bio_service = mock_bio_service_cls.return_value
        mock_bio_service.get_artist_bio.return_value = "Test Bio"
        service.bio_service = mock_bio_service

        file_info = {"path": "test.mp3", "metadata": {"artist": "Test Artist"}}
        options = {"fetch_bio": True}

        # Mock other methods called in _finalize_file_update
        with patch.object(service, "_download_cover_art"), patch.object(
            service, "_apply_metadata_to_file"
        ), patch.object(service, "_fetch_and_embed_lyrics"):

            service._finalize_file_update(file_info, file_info["metadata"], options)

            # Verify bio was fetched
            mock_bio_service.get_artist_bio.assert_called_with("Test Artist")
            assert file_info["metadata"]["bio"] == "Test Bio"

    def test_analyze_audio(self, service):
        """Test audio analysis"""
        # Setup mock audio analyzer
        mock_analyzer = service.audio_analyzer
        mock_analyzer.get_bpm.return_value = 120.0
        mock_analyzer.get_key.return_value = "C Major"
        mock_analyzer.get_mood.return_value = "Happy"
        mock_analyzer.calculate_replay_gain.return_value = -3.5

        file_info = {"path": "test.mp3"}
        metadata = {}

        service._analyze_audio(file_info, metadata)

        assert metadata["bpm"] == 120.0
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Happy"
        assert metadata["replay_gain"] == -3.5

        mock_analyzer.save_analysis_tags.assert_called_with(
            "test.mp3", 120.0, "C Major", "Happy", -3.5
        )
