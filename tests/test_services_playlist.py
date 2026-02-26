import pytest

from src.services.playlist_service import PlaylistGenerator


class TestPlaylistService:

    @pytest.fixture
    def generator(self):
        return PlaylistGenerator()

    @pytest.fixture
    def sample_files(self):
        return [
            {"path": "upbeat.mp3", "metadata": {"bpm": "130", "mood": "Energetic"}},
            {"path": "chill.mp3", "metadata": {"bpm": "80", "mood": "Calm"}},
            {"path": "mid.mp3", "metadata": {"bpm": "110", "mood": "Happy"}},
            {"path": "unknown.mp3", "metadata": {}},
            {"path": "invalid.mp3", "metadata": {"bpm": "invalid"}},
        ]

    def test_generate_upbeat_playlist(self, generator, sample_files):
        playlist = generator.generate_upbeat_playlist(sample_files, min_bpm=120)
        assert len(playlist) == 1
        assert playlist[0]["path"] == "upbeat.mp3"

        # Test custom threshold
        playlist = generator.generate_upbeat_playlist(sample_files, min_bpm=100)
        assert len(playlist) == 2  # upbeat + mid

    def test_generate_chill_playlist(self, generator, sample_files):
        playlist = generator.generate_chill_playlist(sample_files, max_bpm=100)
        assert len(playlist) == 1
        assert playlist[0]["path"] == "chill.mp3"

        # Test custom threshold
        playlist = generator.generate_chill_playlist(sample_files, max_bpm=115)
        assert len(playlist) == 2  # chill + mid

    def test_generate_playlist_by_mood(self, generator, sample_files):
        playlist = generator.generate_playlist_by_mood(sample_files, "Energetic")
        assert len(playlist) == 1
        assert playlist[0]["path"] == "upbeat.mp3"

        playlist = generator.generate_playlist_by_mood(sample_files, "calm")  # Case insensitive
        assert len(playlist) == 1
        assert playlist[0]["path"] == "chill.mp3"

        playlist = generator.generate_playlist_by_mood(sample_files, "NonExistent")
        assert len(playlist) == 0

    def test_find_similar_tracks(self, generator):
        target = {"path": "target.mp3", "metadata": {"bpm": "120", "key": "C Major"}}

        # Similar BPM and Key
        similar1 = {"path": "similar1.mp3", "metadata": {"bpm": "120", "key": "C Major"}}

        # Compatible Key (G Major is 1 step away), Similar BPM
        similar2 = {"path": "similar2.mp3", "metadata": {"bpm": "122", "key": "G Major"}}

        # Far Key (F# Major is 6 steps away), Same BPM
        diff1 = {"path": "diff1.mp3", "metadata": {"bpm": "120", "key": "F# Major"}}

        # Very different BPM, Same Key
        diff2 = {"path": "diff2.mp3", "metadata": {"bpm": "60", "key": "C Major"}}

        pool = [similar1, similar2, diff1, diff2, target]

        results = generator.find_similar_tracks(target, pool, limit=3)

        assert len(results) == 3
        # similar1 should be first (exact match vector)
        assert results[0]["path"] == "similar1.mp3"
        # similar2 should be second (close key)
        assert results[1]["path"] == "similar2.mp3"
