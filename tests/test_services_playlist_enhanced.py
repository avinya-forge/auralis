import pytest

from src.services.playlist_service import PlaylistGenerator


class TestPlaylistServiceEnhanced:

    @pytest.fixture
    def generator(self):
        return PlaylistGenerator()

    @pytest.fixture
    def sample_files(self):
        return [
            # C Major, 120 BPM
            {
                "path": "song1.mp3",
                "metadata": {"bpm": "120", "key": "C Major", "artist": "A", "title": "1"},
            },
            # G Major (Compatible with C), 122 BPM (Within tolerance 5% of 120 is 6 -> 114-126)
            {
                "path": "song2.mp3",
                "metadata": {"bpm": "122", "key": "G Major", "artist": "B", "title": "2"},
            },
            # A Minor (Compatible with C), 125 BPM (Within tolerance 5% of 120 is 6 -> 114-126)
            {
                "path": "song3.mp3",
                "metadata": {"bpm": "125", "key": "A Minor", "artist": "C", "title": "3"},
            },
            # F# Major (Incompatible with C), 120 BPM
            {
                "path": "song4.mp3",
                "metadata": {"bpm": "120", "key": "F# Major", "artist": "D", "title": "4"},
            },
            # C Major, 140 BPM (Outside tolerance from 120)
            {
                "path": "song5.mp3",
                "metadata": {"bpm": "140", "key": "C Major", "artist": "E", "title": "5"},
            },
        ]

    def test_generate_flow_mode_playlist(self, generator, sample_files):
        start_track = sample_files[0]
        # Request 10 minutes, files are 3 mins default. Should pick tracks until no more found.
        playlist = generator.generate_flow_mode_playlist(
            sample_files, start_track=start_track, length_minutes=10, tolerance_bpm=0.05
        )

        # It should pick at least start_track and one of song2 or song3
        assert len(playlist) >= 2
        assert playlist[0] == start_track

        # Verify compatibility chain
        for i in range(len(playlist) - 1):
            current = playlist[i]
            next_track = playlist[i + 1]

            curr_bpm = float(current["metadata"]["bpm"])
            next_bpm = float(next_track["metadata"]["bpm"])
            curr_key = current["metadata"]["key"]
            next_key = next_track["metadata"]["key"]

            # Check BPM
            bpm_diff = abs(next_bpm - curr_bpm) / curr_bpm
            # Fallback tolerance is 2*0.05 = 0.1
            assert bpm_diff <= 0.10001

            # Check Key
            compatible = generator.KEY_COMPATIBILITY.get(curr_key, [])
            assert next_key in compatible, f"Key {next_key} not compatible with {curr_key}"

    def test_flow_mode_random_start(self, generator, sample_files):
        playlist = generator.generate_flow_mode_playlist(
            sample_files, length_minutes=10, tolerance_bpm=0.05
        )
        assert len(playlist) >= 1

    def test_flow_mode_exhaustion(self, generator, sample_files):
        # Only 2 compatible tracks
        playlist = generator.generate_flow_mode_playlist(
            sample_files,
            start_track=sample_files[0],
            length_minutes=60,  # Request long playlist
            tolerance_bpm=0.05,
        )
        # Should stop after 2 tracks
        assert len(playlist) == 2

    def test_export_import_playlist(self, generator, sample_files, tmp_path):
        playlist = sample_files[:2]
        filepath = tmp_path / "test_playlist.m3u8"

        # Export
        assert generator.export_playlist(playlist, str(filepath))
        assert filepath.exists()

        # Read content
        content = filepath.read_text(encoding="utf-8")
        assert "#EXTM3U" in content
        assert "#EXTINF:180,A - 1" in content
        assert "song1.mp3" in content

        # Import
        imported_paths = generator.import_playlist(str(filepath))
        assert len(imported_paths) == 2
        assert "song1.mp3" in imported_paths
        assert "song2.mp3" in imported_paths

    def test_export_playlist_error(self, generator, sample_files):
        # Test error handling (e.g. invalid path)
        assert not generator.export_playlist(sample_files, "/invalid/path/test.m3u8")

    def test_import_playlist_error(self, generator):
        # Test error handling
        assert generator.import_playlist("/invalid/path/test.m3u8") == []

    def test_flow_mode_no_valid_files(self, generator):
        files = [{"path": "bad.mp3", "metadata": {}}]  # No BPM/Key
        playlist = generator.generate_flow_mode_playlist(files)
        assert len(playlist) == 0

    def test_find_similar_tracks(self, generator, sample_files):
        target = sample_files[0]  # C Major, 120
        # song3: A Minor (Same key vector), 125 (Close BPM) -> High similarity
        # song5: C Major (Same key vector), 140 (Farther BPM) -> High similarity
        # song2: G Major (Close key), 122 (Close BPM) -> High similarity
        # song4: F# Major (Opposite key), 120 -> Low similarity

        similar = generator.find_similar_tracks(target, sample_files, limit=3)

        assert len(similar) == 3
        paths = [t["path"] for t in similar]

        # F# Major is musically opposite to C Major in Circle of Fifths (distance 6)
        # So it should have very low cosine similarity (close to -1 for key part)
        assert "song4.mp3" not in paths

    def test_playlist_history(self, tmp_path):
        from src.services.playlist_service import PlaylistHistory
        from unittest.mock import patch

        # Mock Path.home to return tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            history = PlaylistHistory()
            assert history.get_history() == []

            # Add entry
            playlist = [{"path": "song1.mp3"}, {"path": "song2.mp3"}]
            history.add_entry("My Playlist", playlist)

            assert len(history.get_history()) == 1
            entry = history.get_history()[0]
            assert entry["name"] == "My Playlist"
            assert entry["count"] == 2
            assert "song1.mp3" in entry["tracks"]

            # Verify file created
            hist_file = tmp_path / ".auralis" / "playlist_history.json"
            assert hist_file.exists()

            # Test loading
            history2 = PlaylistHistory()
            assert len(history2.get_history()) == 1
            assert history2.get_history()[0]["name"] == "My Playlist"
