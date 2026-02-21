import sys
from unittest.mock import MagicMock, patch
import pytest

# Helper to ensure we can mock imports before they happen
# We need to mock langdetect, speech_recognition, and pydub before importing the service


class TestLanguageService:

    @pytest.fixture
    def mock_deps(self):
        """Mock external dependencies"""
        mock_langdetect = MagicMock()
        mock_sr = MagicMock()
        mock_pydub = MagicMock()

        # Setup specific mocks
        mock_audio = MagicMock()
        mock_pydub.AudioSegment.from_file.return_value = mock_audio
        mock_audio.__len__.return_value = 60000  # 60 seconds
        mock_audio.__getitem__.return_value = mock_audio  # Slicing

        mock_recognizer = MagicMock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.AudioFile.return_value.__enter__.return_value = MagicMock()

        mocks = {
            "langdetect": mock_langdetect,
            "speech_recognition": mock_sr,
            "pydub": mock_pydub,
        }

        with patch.dict(sys.modules, mocks):
            # Reload module to apply mocks
            if "src.services.language_service" in sys.modules:
                del sys.modules["src.services.language_service"]

            import src.services.language_service

            yield src.services.language_service

    @pytest.fixture
    def service(self, mock_deps):
        """Get service instance with deps available"""
        # Force HAS_LANGUAGE_DETECTION to True for testing
        with patch("src.services.language_service.HAS_LANGUAGE_DETECTION", True):
            service = mock_deps.LanguageDetectionService()
            service.available = True
            return service

    def test_init_available(self, mock_deps):
        """Test initialization when deps are present"""
        with patch("src.services.language_service.HAS_LANGUAGE_DETECTION", True):
            service = mock_deps.LanguageDetectionService()
            assert service.available is True

    def test_init_unavailable(self, mock_deps):
        """Test initialization when deps are missing"""
        with patch("src.services.language_service.HAS_LANGUAGE_DETECTION", False):
            service = mock_deps.LanguageDetectionService()
            assert service.available is False

    def test_detect_language_success(self, service):
        """Test successful language detection"""
        mock_sr = sys.modules["speech_recognition"]
        mock_langdetect = sys.modules["langdetect"]

        # Mock SR result
        mock_recognizer = mock_sr.Recognizer.return_value
        mock_recognizer.recognize_google.return_value = "This is an English text"

        # Mock detection result
        mock_langdetect.detect.return_value = "en"

        with patch("pathlib.Path.exists", return_value=True):
            code, name = service.detect_language("/path/to/audio.mp3")

            assert code == "en"
            assert name == "English"

            mock_recognizer.recognize_google.assert_called()
            mock_langdetect.detect.assert_called_with("This is an English text")

    def test_detect_language_file_not_found(self, service):
        """Test detection when file doesn't exist"""
        with patch("pathlib.Path.exists", return_value=False):
            code, name = service.detect_language("/nonexistent.mp3")
            assert code == "unknown"
            assert name == "Unknown"

    def test_detect_language_short_text(self, service):
        """Test detection when extracted text is too short"""
        mock_sr = sys.modules["speech_recognition"]
        mock_recognizer = mock_sr.Recognizer.return_value
        mock_recognizer.recognize_google.return_value = "Hi"

        with patch("pathlib.Path.exists", return_value=True):
            code, name = service.detect_language("/path/to/audio.mp3")
            assert code == "unknown"
            assert name == "Unknown"

    def test_detect_language_recognition_error(self, service):
        """Test detection when speech recognition fails"""
        mock_sr = sys.modules["speech_recognition"]
        mock_recognizer = mock_sr.Recognizer.return_value
        mock_recognizer.recognize_google.side_effect = Exception("SR Error")

        with patch("pathlib.Path.exists", return_value=True):
            code, name = service.detect_language("/path/to/audio.mp3")
            assert code == "unknown"
            assert name == "Unknown"

    def test_detect_language_unavailable(self, service):
        """Test detection when service is unavailable"""
        service.available = False
        code, name = service.detect_language("/path/to/audio.mp3")
        assert code == "unknown"
        assert name == "Unknown"

    def test_get_language_folder(self, service):
        """Test getting language folder name"""
        # Mock detect_language via patching the service instance method?
        # Better to mock the underlying calls to test full flow or patch the method.
        # Let's patch detect_language on the instance for simplicity in this unit test.

        with patch.object(service, "detect_language", return_value=("es", "Spanish")):
            folder = service.get_language_folder("/path/to/audio.mp3")
            assert folder == "Spanish"

    def test_get_language_folder_unknown(self, service):
        """Test getting language folder name for unknown language"""
        with patch.object(service, "detect_language", return_value=("unknown", "Unknown")):
            folder = service.get_language_folder("/path/to/audio.mp3", default="Misc")
            assert folder == "Misc"

    def test_module_functions(self, mock_deps):
        """Test module level wrapper functions"""
        # We need to patch the singleton instance in the module
        mock_service_instance = MagicMock()

        with patch("src.services.language_service.language_service", mock_service_instance):
            import src.services.language_service as module

            module.detect_language("/path")
            mock_service_instance.detect_language.assert_called_with("/path")

            module.get_language_folder("/path")
            mock_service_instance.get_language_folder.assert_called_with("/path", "Unknown")

            module.is_available()
            # logic for is_available property access
            _ = mock_service_instance.available
