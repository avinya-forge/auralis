import sys
from unittest.mock import MagicMock

# Mock librosa if missing
if "librosa" not in sys.modules:
    sys.modules["librosa"] = MagicMock()
if "librosa.feature" not in sys.modules:
    sys.modules["librosa.feature"] = MagicMock()


def test_demixer_init():
    from src.services.audio.demixer import Demixer

    d = Demixer()
    assert d is not None


def test_dsp_engine_imports():
    from src.services.audio.dsp_engine import extract_chroma

    assert extract_chroma is not None
