import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestAudioSimilarityService:

    @pytest.fixture
    def mock_dependencies(self):
        """Fixture to mock dependencies and ensure clean import"""
        mock_numpy = MagicMock()
        mock_numpy.ndarray = MagicMock  # Use MagicMock as type placeholder
        mock_numpy.std.return_value = 1.0
        mock_numpy.zeros.return_value = MagicMock()
        mock_numpy.ones.return_value = MagicMock()
        mock_numpy.mean.return_value = MagicMock()

        mock_mutagen = MagicMock()
        mock_librosa = MagicMock()
        mock_soundfile = MagicMock()
        mock_sklearn = MagicMock()
        mock_pydub = MagicMock()
        mock_acoustid = MagicMock()
        mock_chromaprint = MagicMock()

        mocks = {
            "numpy": mock_numpy,
            "mutagen": mock_mutagen,
            "librosa": mock_librosa,
            "soundfile": mock_soundfile,
            "sklearn": mock_sklearn,
            "sklearn.metrics": MagicMock(),
            "sklearn.metrics.pairwise": MagicMock(),
            "pydub": mock_pydub,
            "acoustid": mock_acoustid,
            "chromaprint": mock_chromaprint,
        }

        # Apply patches
        with patch.dict(sys.modules, mocks):
            # We must remove the service from sys.modules to force reload with mocked deps
            if "src.services.audio_similarity_service" in sys.modules:
                del sys.modules["src.services.audio_similarity_service"]

            import src.services.audio_similarity_service

            importlib.reload(src.services.audio_similarity_service)

            yield src.services.audio_similarity_service

        # Cleanup: Remove the service to avoid polluting other tests with mocked version
        if "src.services.audio_similarity_service" in sys.modules:
            del sys.modules["src.services.audio_similarity_service"]

    @pytest.fixture
    def service(self, mock_dependencies):
        """Fixture to provide a fresh service instance"""
        service = mock_dependencies.AudioSimilarityService()
        # Ensure cache is empty
        service.fingerprint_cache = {}
        return service

    def test_initialization(self, mock_dependencies):
        """Test initialization logic"""
        # Test when dependencies are available (default in our mock env)
        service = mock_dependencies.AudioSimilarityService()
        assert service.available is True

        # Test when dependencies are missing
        with patch.dict(sys.modules):
            sys.modules["librosa"] = None
            service = mock_dependencies.AudioSimilarityService()
            assert service.available is False

    def test_compute_fingerprint(self, service, mock_dependencies):
        """Test fingerprint computation"""
        mock_librosa = sys.modules["librosa"]

        # Setup mocks
        mock_librosa.load.return_value = (MagicMock(), 22050)
        mock_librosa.feature.melspectrogram.return_value = MagicMock()
        mock_librosa.power_to_db.return_value = MagicMock()

        # Call method
        fingerprint = service.compute_fingerprint("test.mp3")

        # Verify calls
        mock_librosa.load.assert_called_with("test.mp3", sr=22050, mono=True, duration=60)
        mock_librosa.feature.melspectrogram.assert_called()
        mock_librosa.power_to_db.assert_called()

        # Verify result (should not be None)
        assert fingerprint is not None

    def test_compute_chroma_hash(self, service, mock_dependencies):
        """Test compute chroma hash logic"""
        mock_acoustid = sys.modules["acoustid"]
        mock_chromaprint = sys.modules["chromaprint"]

        mock_acoustid.fingerprint_file.return_value = (10, b"base64fp")
        mock_chromaprint.decode_fingerprint.return_value = ([1, 2, 3], 1)
        mock_chromaprint.hash_fingerprint.return_value = 123456

        fp_hash = service.compute_chroma_hash("test.mp3")

        assert fp_hash == 123456
        mock_acoustid.fingerprint_file.assert_called_with("test.mp3")
        mock_chromaprint.decode_fingerprint.assert_called_with(b"base64fp")
        mock_chromaprint.hash_fingerprint.assert_called_with([1, 2, 3])

        # Test caching
        fp_hash_cached = service.compute_chroma_hash("test.mp3")
        assert fp_hash_cached == 123456
        assert mock_acoustid.fingerprint_file.call_count == 1  # Should not be called again

    def test_compute_similarity(self, service, mock_dependencies):
        """Test similarity computation"""
        # We need to ensure sklearn.metrics.pairwise.cosine_similarity is mocked
        # The mock setup created mocks for sklearn.metrics.pairwise
        mock_cosine = sys.modules["sklearn.metrics.pairwise"].cosine_similarity

        fp1 = MagicMock()
        fp2 = MagicMock()

        # Mock return value of cosine_similarity: [[0.9]]
        mock_cosine.return_value = [[0.9]]

        similarity = service.compute_similarity(fp1, fp2)

        assert similarity == 0.9
        mock_cosine.assert_called()

    def test_find_duplicates_empty(self, service):
        """Test finding duplicates with empty input"""
        assert service.find_duplicates([]) == []

    def test_find_duplicates_no_duration(self, service, mock_dependencies):
        """Test finding duplicates when duration is missing and pydub fails"""
        files = [{"path": "test.mp3", "metadata": {}}]

        mock_pydub = sys.modules["pydub"]
        mock_pydub.AudioSegment.from_file.side_effect = Exception("Error")

        assert service.find_duplicates(files) == []

    def test_find_duplicates_logic(self, service, mock_dependencies):
        """Test the core duplicate finding logic falling back to compute_fingerprint"""
        mock_numpy = sys.modules["numpy"]

        # Setup files
        file1 = {
            "path": "song1.mp3",
            "metadata": {"duration": 180, "bitrate": 128000},
            "size": 1000,
        }
        file2 = {
            "path": "song1_copy.mp3",
            "metadata": {"duration": 182, "bitrate": 320000},
            "size": 2000,
        }
        file3 = {"path": "song2.mp3", "metadata": {"duration": 240}, "size": 1500}

        files = [file1, file2, file3]

        # Mock compute_fingerprint
        fp1 = mock_numpy.ones(128)
        fp2 = mock_numpy.ones(128)
        fp3 = mock_numpy.zeros(128)

        def mock_compute_fp(path):
            if path == "song1.mp3":
                return fp1
            if path == "song1_copy.mp3":
                return fp2
            if path == "song2.mp3":
                return fp3
            return None

        # Mock compute_chroma_hash to return None to fallback to compute_fingerprint
        service.compute_chroma_hash = MagicMock(return_value=None)

        service.compute_fingerprint = MagicMock(side_effect=mock_compute_fp)

        # Mock compute_similarity
        def mock_compute_sim(f1, f2):
            if f1 is f2 or (f1 is fp1 and f2 is fp2):
                return 0.95
            return 0.1

        service.compute_similarity = MagicMock(side_effect=mock_compute_sim)

        # Run
        duplicates = service.find_duplicates(files)

        # Verify
        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2
        # Sorting prefers higher bitrate/quality (song1_copy has higher bitrate)
        assert duplicates[0][0]["path"] == "song1_copy.mp3"
        assert duplicates[0][1]["path"] == "song1.mp3"

    def test_find_duplicates_with_chroma_hash(self, service, mock_dependencies):
        """Test finding duplicates using fast chroma hash"""
        file1 = {
            "path": "song1.mp3",
            "metadata": {"duration": 180, "bitrate": 128000},
            "size": 1000,
        }
        file2 = {
            "path": "song1_exact_dup.mp3",
            "metadata": {"duration": 180, "bitrate": 320000},
            "size": 2000,
        }
        file3 = {
            "path": "song2.mp3",
            "metadata": {"duration": 180},
            "size": 1500,
        }

        files = [file1, file2, file3]

        # Let's pick hashes with specific distances
        # 0b00000000000000000000000000000000 (0)
        # 0b00000000000000000000000000000001 (1) -> Diff 1
        # 0b00000000000000000000000000000111 (7) -> Diff 3

        def mock_compute_chroma_hash_specific(path):
            if path == "song1.mp3":
                return 0
            if path == "song1_exact_dup.mp3":
                return 1  # diff is 1 (<= 2)
            if path == "song2.mp3":
                return 7  # diff is 3 (> 2)
            return None

        service.compute_chroma_hash = MagicMock(side_effect=mock_compute_chroma_hash_specific)
        service.compute_fingerprint = MagicMock(return_value=None)  # Ensure it doesn't fallback

        duplicates = service.find_duplicates(files)

        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2
        assert duplicates[0][0]["path"] == "song1_exact_dup.mp3"
        assert duplicates[0][1]["path"] == "song1.mp3"
        # Deep compare should only be called once, for song1.mp3 when comparing with song2.mp3
        assert service.compute_fingerprint.call_count == 1

    def test_sort_by_quality(self, service):
        """Test quality sorting logic"""
        file1 = {
            "path": "song.flac",
            "metadata": {
                "duration": 180,
                "bitrate": 320000,
                "artist": "A",
                "title": "T",
                "album": "A",
            },
            "size": 10000000,
        }
        file2 = {
            "path": "song.mp3",
            "metadata": {"duration": 180, "bitrate": 128000},
            "size": 3000000,
        }

        sorted_files = service._sort_by_quality([file2, file1])
        assert sorted_files[0] == file1
        assert sorted_files[1] == file2
