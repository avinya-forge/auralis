import sys
import types
from unittest.mock import MagicMock


# --- Helper for recursive module mocking ---
def mock_module(name):
    if name in sys.modules:
        return sys.modules[name]
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m


# --- Mock PyQt6 ---
if "PyQt6" not in sys.modules:
    mock_pyqt6 = mock_module("PyQt6")
    mock_qtcore = mock_module("PyQt6.QtCore")
    mock_qtwidgets = mock_module("PyQt6.QtWidgets")
    mock_qtgui = mock_module("PyQt6.QtGui")

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
    mock_qtcore.pyqtSlot = lambda *a, **k: (lambda f: f)
    mock_qtcore.QCoreApplication = MockQCoreApplication
    mock_qtcore.QThread = MagicMock
    mock_qtcore.QTimer = MagicMock
    mock_qtcore.Qt = MagicMock()
    mock_qtcore.QRunnable = MagicMock
    mock_qtcore.QThreadPool = MagicMock

    mock_qtwidgets.QApplication = MockQCoreApplication
    mock_qtwidgets.QMainWindow = MagicMock
    mock_qtwidgets.QWidget = MagicMock
    mock_qtwidgets.QVBoxLayout = MagicMock
    mock_qtwidgets.QHBoxLayout = MagicMock
    mock_qtwidgets.QLabel = MagicMock
    mock_qtwidgets.QPushButton = MagicMock
    mock_qtwidgets.QScrollArea = MagicMock
    mock_qtwidgets.QLineEdit = MagicMock

    mock_qtgui.QAction = MagicMock
    mock_qtgui.QIcon = MagicMock

# --- Mock Other Dependencies ---
for lib in [
    "mutagen",
    "mutagen.flac",
    "mutagen.mp3",
    "mutagen.id3",
    "mutagen.easyid3",
    "psutil",
    "numpy",
    "librosa",
    "librosa.feature",
    "librosa.onset",
    "librosa.beat",
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
    "torchvision.models",
    "transformers",
    "fastapi",
    "fastapi.middleware",
    "fastapi.middleware.cors",
    "fastapi.responses",
    "starlette",
    "starlette.middleware",
    "starlette.middleware.base",
    "starlette.testclient",
    "pydantic",
    "uvicorn",
    "demucs",
    "musicbrainzngs",
]:
    mock_module(lib)
    # Ensure attributes exist
    parts = lib.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[:i])
        child = parts[i]
        if parent in sys.modules:
            setattr(sys.modules[parent], child, sys.modules[lib])

# Patch specific attributes needed
sys.modules["fastapi"].FastAPI = MagicMock
sys.modules["pydantic"].BaseModel = MagicMock
sys.modules["starlette.middleware.base"].BaseHTTPMiddleware = MagicMock
sys.modules["torch.nn"].Module = MagicMock
sys.modules["torch.nn"].Sequential = MagicMock
sys.modules["torch.nn"].Conv2d = MagicMock
sys.modules["torch.nn"].ReLU = MagicMock
sys.modules["torch.nn"].MaxPool2d = MagicMock
sys.modules["torch.nn"].Linear = MagicMock
sys.modules["torch"].device = MagicMock
sys.modules["torch"].no_grad = MagicMock
