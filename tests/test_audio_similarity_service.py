import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Mock dependencies
modules_to_mock = [
    "librosa",
    "soundfile",
    "sklearn",
    "sklearn.metrics",
    "sklearn.metrics.pairwise",
    "pydub",
]
for module in modules_to_mock:
    if module not in sys.modules:
        sys.modules[module] = MagicMock()

# Import after mocking
from src.services.audio_similarity_service import AudioSimilarityService  # noqa: E402


class TestAudioSimilarityService:

    @pytest.fixture
    def service(self):
        """Fixture to provide a fresh service instance with mocked availability"""
        # Force availability to True for testing logic
        with patch.object(AudioSimilarityService, "__init__", return_value=None):
            service = AudioSimilarityService()
            service.available = True
            service.fingerprint_cache = {}
            service.similarity_threshold = 0.85
            return service

    def test_initialization(self):
        """Test initialization logic"""
        # Test when dependencies are available
        with patch("src.services.audio_similarity_service.HAS_AUDIO_FINGERPRINTING", True):
            service = AudioSimilarityService()
            assert service.available is True
            assert service.similarity_threshold == 0.85

        # Test when dependencies are missing
        with patch("src.services.audio_similarity_service.HAS_AUDIO_FINGERPRINTING", False):
            service = AudioSimilarityService()
            assert service.available is False

    def test_compute_fingerprint(self, service):
        """Test fingerprint computation"""
        # Configure np mock to return numbers for std to avoid comparison errors
        np.std.return_value = 1.0

        # Mock librosa functions
        with patch("src.services.audio_similarity_service.librosa") as mock_librosa:
            # Setup mocks
            mock_librosa.load.return_value = (np.zeros(100), 22050)
            mock_librosa.feature.melspectrogram.return_value = np.zeros((128, 100))
            mock_librosa.power_to_db.return_value = np.zeros((128, 100))

            # Call method
            fingerprint = service.compute_fingerprint("test.mp3")

            # Verify calls
            mock_librosa.load.assert_called_with("test.mp3", sr=22050, mono=True, duration=60)
            mock_librosa.feature.melspectrogram.assert_called()
            mock_librosa.power_to_db.assert_called()

            # Verify result
            assert isinstance(fingerprint, np.ndarray) or isinstance(fingerprint, MagicMock)

    def test_compute_similarity(self, service):
        """Test similarity computation"""
        fp1 = np.random.rand(128)
        fp2 = np.random.rand(128)

        with patch("src.services.audio_similarity_service.cosine_similarity") as mock_cosine:
            # Mock return value of cosine_similarity: [[0.9]]
            mock_cosine.return_value = [[0.9]]

            similarity = service.compute_similarity(fp1, fp2)

            assert similarity == 0.9
            mock_cosine.assert_called()

    def test_find_duplicates_empty(self, service):
        """Test finding duplicates with empty input"""
        assert service.find_duplicates([]) == []

    def test_find_duplicates_no_duration(self, service):
        """Test finding duplicates when duration is missing and pydub fails"""
        files = [{"path": "test.mp3", "metadata": {}}]

        with patch(
            "src.services.audio_similarity_service.pydub.AudioSegment.from_file",
            side_effect=Exception("Error"),
        ):
            assert service.find_duplicates(files) == []

    def test_find_duplicates_logic(self, service):
        """Test the core duplicate finding logic"""
        # Setup files
        # Group 1: Two similar files (duplicates)
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

        # Group 2: One unique file
        file3 = {"path": "song2.mp3", "metadata": {"duration": 240}, "size": 1500}

        files = [file1, file2, file3]

        # Mock compute_fingerprint to return consistent fingerprints
        fp1 = np.ones(128)
        fp2 = np.ones(128)  # Identical to fp1
        fp3 = np.zeros(128)  # Different

        def mock_compute_fp(path):
            if path == "song1.mp3":
                return fp1
            if path == "song1_copy.mp3":
                return fp2
            if path == "song2.mp3":
                return fp3
            return None

        service.compute_fingerprint = MagicMock(side_effect=mock_compute_fp)

        # Mock compute_similarity
        def mock_compute_sim(f1, f2):
            if np.array_equal(f1, fp1) and np.array_equal(f2, fp2):
                return 0.95
            return 0.1

        service.compute_similarity = MagicMock(side_effect=mock_compute_sim)

        # Run
        duplicates = service.find_duplicates(files)

        # Verify
        assert len(duplicates) == 1
        # The group should contain file1 and file2
        # file2 has higher bitrate (320k vs 128k) and size (2000 vs 1000), so it should be first (best quality)
        assert len(duplicates[0]) == 2
        assert duplicates[0][0]["path"] == "song1_copy.mp3"
        assert duplicates[0][1]["path"] == "song1.mp3"

    def test_sort_by_quality(self, service):
        """Test quality sorting logic"""
        # file1: flac, high bitrate
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
        # file2: mp3, low bitrate
        file2 = {
            "path": "song.mp3",
            "metadata": {"duration": 180, "bitrate": 128000},
            "size": 3000000,
        }

        sorted_files = service._sort_by_quality([file2, file1])
        assert sorted_files[0] == file1
        assert sorted_files[1] == file2
