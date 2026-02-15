import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from PyQt6.QtCore import QCoreApplication

# Import the class to test
from src.core.organizer import MusicOrganizer


# Mock external dependencies that might be missing in the test environment
# We do this aggressively to ensure tests can run even without heavy dependencies

# Mock PyQt6
if 'PyQt6' not in sys.modules:
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

    # Mock QCoreApplication
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

    sys.modules['PyQt6'] = mock_pyqt6
    sys.modules['PyQt6.QtCore'] = mock_qtcore

# Mock numpy
if 'numpy' not in sys.modules:
    sys.modules['numpy'] = MagicMock()

# Mock other audio libs just in case
modules_to_mock = [
    'librosa', 'soundfile', 'sklearn', 'sklearn.metrics',
    'sklearn.metrics.pairwise', 'pydub', 'speech_recognition', 'langdetect'
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


class TestMusicOrganizer:

    @pytest.fixture
    def mock_services(self):
        """Mock external services imported in organizer.py"""
        with patch('src.core.organizer.is_language_detection_available', return_value=True) as m1, \
             patch('src.core.organizer.get_language_folder', return_value="English") as m2, \
             patch('src.core.organizer.is_audio_similarity_available', return_value=True) as m3, \
             patch('src.core.organizer.find_similar_audio', return_value=[]) as m4, \
             patch('src.core.organizer.get_best_quality_version', return_value=None) as m5:

            yield {
                'lang_avail': m1,
                'get_lang': m2,
                'audio_avail': m3,
                'find_similar': m4,
                'best_quality': m5
            }

    @pytest.fixture
    def organizer(self, qapp, mock_services):
        """Create a MusicOrganizer instance with mocks"""
        return MusicOrganizer(dry_run=True)

    def test_init(self, organizer, mock_services):
        """Test initialization and service availability detection"""
        assert organizer.dry_run is True
        assert organizer.language_detection_available is True
        assert organizer.audio_similarity_available is True

        # Test with services unavailable
        with patch('src.core.organizer.is_language_detection_available', return_value=False), \
             patch('src.core.organizer.is_audio_similarity_available', return_value=False):
            org = MusicOrganizer()
            assert org.language_detection_available is False
            assert org.audio_similarity_available is False

    def test_organize_files_dry_run(self, organizer, tmp_path):
        """Test dry run doesn't move files but emits signals"""
        # Create a dummy file
        source_file = tmp_path / "test.mp3"
        source_file.write_text("content")

        file_info = {
            'path': str(source_file),
            'filename': "test.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': 'Song', 'artist': 'Artist'}
        }

        dest_root = str(tmp_path / "Output")
        options = {
            'organize_by_language': False,
            'rename_files': False,
            'handle_duplicates': True,
            'remove_empty_dirs': False
        }

        # Connect signal to verify emission
        received_signals = []
        organizer.file_organized.connect(lambda src, dest: received_signals.append((src, dest)))

        result = organizer.organize_files([file_info], dest_root, options)

        # Verify results
        assert result['organized_files'] == 1
        assert len(received_signals) >= 1  # Might have extra signals for manual review etc.
        # Check that file was NOT moved (it's dry run)
        assert source_file.exists()
        assert not os.path.exists(os.path.join(dest_root, "test.mp3"))

    def test_organize_files_basic(self, qapp, mock_services, tmp_path):
        """Test basic file organization (move/copy simulation)"""
        organizer = MusicOrganizer(dry_run=False)

        source_file = tmp_path / "test.mp3"
        source_file.write_text("content")

        file_info = {
            'path': str(source_file),
            'filename': "test.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': 'Song', 'artist': 'Artist'}
        }

        dest_root = tmp_path / "Output"
        options = {
            'organize_by_language': False,
            'rename_files': False
        }

        # We need to ensure shutil.copy2 works or is mocked if we don't want real file ops
        # But using tmp_path is fine for integration-style test

        result = organizer.organize_files([file_info], str(dest_root), options)

        assert result['organized_files'] == 1
        expected_dest = dest_root / "test.mp3"
        assert expected_dest.exists()
        # Original file should still exist because code uses shutil.copy2
        assert source_file.exists()

    def test_organize_files_with_language(self, organizer, mock_services, tmp_path):
        """Test organization into language folders"""
        mock_services['get_lang'].return_value = "Spanish"

        file_info = {
            'path': "/path/to/test.mp3",
            'filename': "test.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': 'Song', 'artist': 'Artist'}
        }

        dest_root = str(tmp_path / "Output")
        options = {
            'organize_by_language': True,
            'use_audio_language_detection': True,
            'rename_files': False
        }

        # Mocking shutil.copy2 and os.makedirs to avoid errors with fake paths
        with patch('os.makedirs'), patch('shutil.copy2'):
            result = organizer.organize_files([file_info], dest_root, options)

        assert result['organized_files'] == 1
        # Check that get_language_folder was called
        mock_services['get_lang'].assert_called_with("/path/to/test.mp3", default="Unknown")

    def test_organize_files_renaming(self, organizer, tmp_path):
        """Test file renaming logic"""
        file_info = {
            'path': "/path/to/original.mp3",
            'filename': "original.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': 'My Song', 'artist': 'The Artist'}
        }

        dest_root = str(tmp_path / "Output")
        options = {
            'organize_by_language': False,
            'rename_files': True
        }

        received_signals = []
        organizer.file_organized.connect(lambda src, dest: received_signals.append(dest))

        with patch('os.makedirs'), patch('shutil.copy2'):
            organizer.organize_files([file_info], dest_root, options)

        assert len(received_signals) == 1
        # Expected filename: My_Song-The_Artist.mp3 (sanitized)
        expected_filename = "My_Song-The_Artist.mp3"
        assert expected_filename in received_signals[0]

    def test_duplicate_handling_metadata(self, organizer, tmp_path):
        """Test duplicate detection based on metadata"""
        file1 = {
            'path': "/path/1.mp3",
            'filename': "1.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': 'Song', 'artist': 'Artist', 'bitrate': 128000}
        }

        # Duplicate of file1, but higher quality
        file2 = {
            'path': "/path/2.mp3",
            'filename': "2.mp3",
            'extension': ".mp3",
            'size': 200,
            'hash': "hash2",  # Different hash but same metadata
            'metadata': {'title': 'Song', 'artist': 'Artist', 'bitrate': 320000}
        }

        dest_root = str(tmp_path / "Output")
        options = {
            'handle_duplicates': True,
            'detect_audio_similarity': False,
            'organize_by_language': False,
            'rename_files': False
        }

        with patch('os.makedirs'), patch('shutil.copy2'):
            # Pass both files at once, with the higher quality file first.
            # Logic:
            # 1. file2 (better quality) is processed and added to organized_files.
            # 2. file1 is processed. It is identified as a duplicate of file2.
            # 3. is_higher_quality(file1, file2) is False.
            # 4. file1 is marked as a duplicate and skipped.

            result = organizer.organize_files([file2, file1], dest_root, options)

            assert result['organized_files'] == 1  # Only file2 organized
            assert result['metadata_duplicates'] == 1  # file1 is duplicate
            assert result['duplicates'] == 1

    def test_manual_review(self, organizer, tmp_path):
        """Test manual review logic for missing metadata"""
        file_info = {
            'path': "/path/unknown.mp3",
            'filename': "unknown.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "hash1",
            'metadata': {'title': '', 'artist': ''}  # Missing metadata
        }

        dest_root = str(tmp_path / "Output")
        options = {}

        received_signals = []
        organizer.file_organized.connect(lambda src, dest: received_signals.append(dest))

        with patch('os.makedirs'), patch('shutil.copy2'):
            result = organizer.organize_files([file_info], dest_root, options)

        assert result['manual_review'] == 1
        assert "Manual_Review" in received_signals[0]

    def test_audio_similarity(self, organizer, mock_services, tmp_path):
        """Test audio similarity integration"""
        file1 = {
            'path': "/path/1.mp3",
            'filename': "1.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "h1",
            'metadata': {}
        }
        file2 = {
            'path': "/path/2.mp3",
            'filename': "2.mp3",
            'extension': ".mp3",
            'size': 100,
            'hash': "h2",
            'metadata': {}
        }

        # Mock finding duplicates
        mock_services['find_similar'].return_value = [[file1, file2]]
        mock_services['best_quality'].return_value = file1

        dest_root = str(tmp_path / "Output")
        options = {
            'detect_audio_similarity': True,
            'keep_all_duplicates': False
        }

        # We need to pass mock file objects that match what find_similar expects/returns
        # The organizer calls find_similar_audio(music_files)

        with patch('os.makedirs'), patch('shutil.copy2'):
            result = organizer.organize_files([file1, file2], dest_root, options)

        # Expect file1 to be organized, file2 to be skipped as duplicate
        assert result['audio_duplicates'] == 1
        assert result['duplicates'] == 1
        # Since file2 is removed from music_files list inside organize_files,
        # organized_files count depends on whether file1 needs review etc.
        # file1 has empty metadata -> Manual Review
        assert result['manual_review'] == 1
