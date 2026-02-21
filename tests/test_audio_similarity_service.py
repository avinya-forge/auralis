import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


# Helper to create a mock module with a class for type checking
def create_mock_module_with_class(class_name):
    mock_module = MagicMock()
    mock_type = type(class_name, (MagicMock,), {})
    setattr(mock_module, class_name, mock_type)
    return mock_module


class TestAudioSimilarityService:

    @pytest.fixture
    def mock_dependencies(self):
        """Fixture to mock dependencies and ensure clean import"""
        # Create mocks that support type checking
        mock_numpy = MagicMock()
        mock_numpy.ndarray = type("ndarray", (MagicMock,), {})
        # Ensure std returns a float to avoid comparison errors
        mock_numpy.std.return_value = 1.0

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
        service_cls = mock_dependencies.AudioSimilarityService

        # Force availability logic since we are controlling the environment
        with patch.object(service_cls, "__init__", return_value=None):
            service = service_cls()
            service.available = True
            service.fingerprint_cache = {}
            service.similarity_threshold = 0.85
            return service

    def test_initialization(self, mock_dependencies):
        """Test initialization logic"""
        # We need to manually trigger logic since we mocked __init__ in the other fixture
        # Here we test the real __init__ but with controlled HAS_AUDIO_FINGERPRINTING

        # Test when dependencies are available (default in our mock env)
        # Note: The module logic sets HAS_AUDIO_FINGERPRINTING on import based on imports success
        # Since we mocked imports successfully, it should be True

        service = mock_dependencies.AudioSimilarityService()
        assert service.available is True
        assert service.similarity_threshold == 0.85

        # Test when dependencies are missing
        # We need to simulate import failure.
        # This is hard with the current fixture structure.
        # Simpler: just patch the HAS_AUDIO_FINGERPRINTING constant
        with patch.object(mock_dependencies, "HAS_AUDIO_FINGERPRINTING", False):
            service = mock_dependencies.AudioSimilarityService()
            assert service.available is False

    def test_compute_fingerprint(self, service, mock_dependencies):
        """Test fingerprint computation"""
        # Mock librosa functions via the module mock we injected
        mock_librosa = sys.modules["librosa"]
        mock_numpy = sys.modules["numpy"]

        # Setup mocks
        mock_librosa.load.return_value = (mock_numpy.zeros(100), 22050)
        mock_librosa.feature.melspectrogram.return_value = mock_numpy.zeros((128, 100))
        mock_librosa.power_to_db.return_value = mock_numpy.zeros((128, 100))

        # Call method
        fingerprint = service.compute_fingerprint("test.mp3")

        # Verify calls
        mock_librosa.load.assert_called_with("test.mp3", sr=22050, mono=True, duration=60)
        mock_librosa.feature.melspectrogram.assert_called()
        mock_librosa.power_to_db.assert_called()

        # Verify result
        assert isinstance(fingerprint, mock_numpy.ndarray) or isinstance(fingerprint, MagicMock)

    def test_compute_similarity(self, service, mock_dependencies):
        """Test similarity computation"""
        mock_numpy = sys.modules["numpy"]
        mock_cosine = sys.modules["sklearn.metrics.pairwise"].cosine_similarity

        fp1 = mock_numpy.random.rand(128)
        fp2 = mock_numpy.random.rand(128)

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
        # We need to mock it on the service instance because we replaced the class method
        # Actually in `find_duplicates` it calls `self.compute_similarity`.

        def mock_compute_sim(f1, f2):
            # Simple identity check for test
            if f1 is f2 or (f1 is fp1 and f2 is fp2):  # simplified equality
                return 0.95
            return 0.1

        service.compute_similarity = MagicMock(side_effect=mock_compute_sim)

        # Run
        duplicates = service.find_duplicates(files)

        # Verify
        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2
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
