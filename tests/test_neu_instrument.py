import sys
from unittest.mock import MagicMock

# Mock torch if missing
if "torch" not in sys.modules:
    sys.modules["torch"] = MagicMock()
    sys.modules["torch.nn"] = MagicMock()


def test_resnet_init():
    from src.services.ai.instrument_classifier import InstrumentResNet

    model = InstrumentResNet()
    assert model is not None


def test_inference_init():
    from src.services.ai.instrument_classifier import InstrumentInference

    inference = InstrumentInference()
    assert inference is not None
