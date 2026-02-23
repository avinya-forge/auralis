import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestAudioSimilarityService:

    @pytest.fixture
    def mock_dependencies(self):
        """Fixture to mock dependencies and ensure clean import"""
        mock_numpy = MagicMock()
        mock_numpy.ndarray = MagicMock # Use MagicMock as type placeholder
        mock_numpy.std.return_value = 1.0
        mock_numpy.zeros.return_value = MagicMock()
        mock_numpy.ones.return_value = MagicMock()
        mock_numpy.mean.return_value = MagicMock()

        mock_mutagen = MagicMock()
        mock_librosa = MagicMock()
        mock_soundfile = MagicMock()
        mock_sklearn = MagicMock()
        mock_pydub = MagicMock()

        mocks = {
            "numpy": mock_numpy,
            "mutagen": mock_mutagen,
            "librosa": mock_librosa,
            "soundfile": mock_soundfile,
            "sklearn": mock_sklearn,
            "sklearn.metrics": MagicMock(),
            "sklearn.metrics.pairwise": MagicMock(),
            "pydub": mock_pydub,
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
        mock_numpy = sys.modules["numpy"]

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

    def test_compute_similarity(self, service, mock_dependencies):
        """Test similarity computation"""
        mock_numpy = sys.modules["numpy"]
        # We need to mock the import inside the method if it was lazy loaded?
        # But since we patched sys.modules, import inside method should get our mock.

        mock_sklearn = sys.modules["sklearn"]
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
        """Test the core duplicate finding logic"""
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
