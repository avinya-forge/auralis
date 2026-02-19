import sys
import types
from unittest.mock import MagicMock

# --- Mock PyQt6 ---
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

        def exec(self):
            return 0

    mock_qtcore.QObject = MockQObject
    mock_qtcore.pyqtSignal = MockSignal
    mock_qtcore.QCoreApplication = MockQCoreApplication

    # Add other needed QtCore classes
    mock_qtcore.QThread = MagicMock
    mock_qtcore.QTimer = MagicMock
    mock_qtcore.Qt = MagicMock()

    mock_pyqt6.QtCore = mock_qtcore

    # Mock QtWidgets
    mock_qtwidgets = MagicMock()
    mock_qtwidgets.QApplication = MockQCoreApplication
    mock_qtwidgets.QMainWindow = MagicMock
    mock_qtwidgets.QWidget = MagicMock
    mock_pyqt6.QtWidgets = mock_qtwidgets

    # Mock QtGui
    mock_qtgui = MagicMock()
    mock_qtgui.QAction = MagicMock
    mock_qtgui.QIcon = MagicMock
    mock_pyqt6.QtGui = mock_qtgui

    sys.modules["PyQt6"] = mock_pyqt6
    sys.modules["PyQt6.QtCore"] = mock_qtcore
    sys.modules["PyQt6.QtWidgets"] = mock_qtwidgets
    sys.modules["PyQt6.QtGui"] = mock_qtgui


# --- Mock Mutagen ---
# Always mock mutagen for unit tests to avoid I/O and dependency issues
mock_mutagen = types.ModuleType("mutagen")
mock_mutagen.__path__ = []

# Submodules
mock_flac = types.ModuleType("mutagen.flac")


class FLAC(MagicMock):
    pass  # Inherit from MagicMock so instances are mocks


class Picture(MagicMock):
    pass


mock_flac.FLAC = FLAC
mock_flac.Picture = Picture
mock_mutagen.flac = mock_flac

mock_mp3 = types.ModuleType("mutagen.mp3")


class MP3(MagicMock):
    pass


mock_mp3.MP3 = MP3
mock_mutagen.mp3 = mock_mp3

mock_id3 = types.ModuleType("mutagen.id3")
for name in ["APIC", "TALB", "TCON", "TDRC", "TIT2", "TPE1", "TRCK"]:
    setattr(mock_id3, name, MagicMock)  # Assign class not instance
mock_mutagen.id3 = mock_id3

# Register in sys.modules
sys.modules["mutagen"] = mock_mutagen
sys.modules["mutagen.flac"] = mock_flac
sys.modules["mutagen.mp3"] = mock_mp3
sys.modules["mutagen.id3"] = mock_id3

# Also patch mutagen.File
mock_mutagen.File = MagicMock()


# --- Mock Psutil ---
# Always mock psutil
mock_psutil = MagicMock()
# Ensure iterators work
mock_psutil.process_iter.return_value = []
mock_psutil.cpu_percent.return_value = 0.0
mock_psutil.virtual_memory.return_value.percent = 0.0
mock_psutil.virtual_memory.return_value.available = 1024 * 1024 * 1024
mock_psutil.net_io_counters.return_value.bytes_sent = 0
mock_psutil.net_io_counters.return_value.bytes_recv = 0

sys.modules["psutil"] = mock_psutil


# --- Mock Other Dependencies ---
if "numpy" not in sys.modules:
    mock_numpy = MagicMock()

    class ndarray:
        pass

    mock_numpy.ndarray = ndarray
    sys.modules["numpy"] = mock_numpy

for lib in [
    "librosa",
    "soundfile",
    "sklearn",
    "pydub",
    "dotenv",
    "acoustid",
    "discogs_client",
    "musicbrainzngs",
    "spotipy",
    "pylast",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "requests",
    "bs4",
    "lxml",
]:
    if lib not in sys.modules:
        sys.modules[lib] = MagicMock()
