import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QCoreApplication

# Import the class to test
from src.core.organizer import MusicOrganizer

# Mock external dependencies
if "PyQt6" not in sys.modules:
    mock_pyqt6 = MagicMock()
    mock_qtcore = MagicMock()

    class MockQObject:
        def __init__(self, parent=None):
            pass

    class MockSignal:
        def __init__(self, *args, **kwargs):
            self.slots = []

        def connect(self, slot):
            self.slots.append(slot)

        def emit(self, *args):
            for slot in self.slots:
                slot(*args)

    class MockQCoreApplication:
        _instance = None

        def __init__(self, args):
            MockQCoreApplication._instance = self

        @staticmethod
        def instance():
            return MockQCoreApplication._instance

    mock_qtcore.QObject = MockQObject
    mock_qtcore.pyqtSignal = MockSignal
    mock_qtcore.QCoreApplication = MockQCoreApplication

    mock_pyqt6.QtCore = mock_qtcore

    sys.modules["PyQt6"] = mock_pyqt6
    sys.modules["PyQt6.QtCore"] = mock_qtcore

if "numpy" not in sys.modules:
    sys.modules["numpy"] = MagicMock()

modules_to_mock = [
    "librosa",
    "soundfile",
    "sklearn",
    "sklearn.metrics",
    "sklearn.metrics.pairwise",
    "pydub",
    "speech_recognition",
    "langdetect",
]
for module in modules_to_mock:
    if module not in sys.modules:
        sys.modules[module] = MagicMock()


@pytest.fixture(scope="session")
def qapp():
    """Create a QCoreApplication instance for QObject signals"""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


class TestMusicOrganizerTemplate:

    @pytest.fixture
    def mock_services(self):
        with patch("src.core.organizer.is_language_detection_available", return_value=True), \
             patch("src.core.organizer.get_language_folder", return_value="English"), \
             patch("src.core.organizer.is_audio_similarity_available", return_value=True), \
             patch("src.core.organizer.find_similar_audio", return_value=[]), \
             patch("src.core.organizer.get_best_quality_version", return_value=None):
            yield

    @pytest.fixture
    def organizer(self, qapp, mock_services):
        return MusicOrganizer(dry_run=True)

    def test_generate_path_simple_template(self, organizer):
        """Test simple template generation"""
        file_info = {
            "metadata": {
                "artist": "The Artist",
                "title": "My Song",
                "album": "Greatest Hits"
            },
            "extension": ".mp3"
        }
        template = "{artist}/{album}/{title}"

        # We need to test the private method or public interface
        # Assuming we will add _generate_path_from_template

        # Since the method doesn't exist yet, we can't call it directly in this test file
        # unless we add it first. But we are writing tests first.
        # So we will wrap the call in a try/except or just expect it to fail if run now.

        # However, for the purpose of the plan, I will write the test assuming the method exists.
        # When I run `pytest` it will fail, which is correct TDD.

        try:
            result = organizer._generate_path_from_template(file_info, template)
            # Normalize path separators for cross-platform test consistency
            expected = os.path.join("The_Artist", "Greatest_Hits", "My_Song.mp3")
            assert result == expected
        except AttributeError:
            pytest.fail("Method _generate_path_from_template not implemented yet")

    def test_generate_path_with_missing_metadata(self, organizer):
        """Test template generation with missing metadata"""
        file_info = {
            "metadata": {
                "title": "My Song"
                # Missing artist, album
            },
            "extension": ".mp3"
        }
        template = "{artist}/{album}/{title}"

        try:
            result = organizer._generate_path_from_template(file_info, template)
            expected = os.path.join("Unknown_Artist", "Unknown_Album", "My_Song.mp3")
            assert result == expected
        except AttributeError:
            pytest.fail("Method _generate_path_from_template not implemented yet")

    def test_generate_path_all_placeholders(self, organizer):
        """Test all supported placeholders"""
        file_info = {
            "path": "/path/to/song.flac",
            "metadata": {
                "artist": "Artist",
                "title": "Title",
                "album": "Album",
                "year": "2023",
                "genre": "Rock",
                "language": "English"
            },
            "extension": ".flac"
        }
        template = "{genre}/{year}/{language}/{artist}/{album}/{title}"

        try:
            result = organizer._generate_path_from_template(file_info, template)
            expected = os.path.join("Rock", "2023", "English", "Artist", "Album", "Title.flac")
            assert result == expected
        except AttributeError:
            pytest.fail("Method _generate_path_from_template not implemented yet")

    def test_get_destination_path_uses_template(self, organizer):
        """Test that _get_destination_path uses template when provided in options"""
        file_info = {
            "metadata": {
                "artist": "Artist",
                "title": "Title"
            },
            "extension": ".mp3",
            "filename": "original.mp3"
        }

        organizer.dest_root = "/tmp/music"
        organizer.options = {
            "directory_template": "{artist}/{title}",
            "organize_by_language": False
        }

        try:
            # We assume _get_destination_path returns full path
            result = organizer._get_destination_path(file_info)
            expected = os.path.join("/tmp/music", "Artist", "Title.mp3")
            # We need to handle potential ensure_unique_filename modifications
            # But in test environment with dry_run and non-existent files, it should be exact
            assert result == expected
        except AttributeError:
             pytest.fail("Method might not be using template yet")
