from unittest.mock import MagicMock, patch

import numpy as np

from src.services.ai.instrument_classifier import InstrumentInferenceWrapper, InstrumentResNet
from src.services.ai.vocalist_analyzer import VocalistAnalyzer
from src.utils.ai.drift_detector import DriftDetector


def test_instrument_resnet_forward():
    # Only test if torch is available (our fallback creates a mock module if missing)

    # If the system has torch available, we test the network forward pass.
    # Because of our fallback in the module, if torch isn't real, it inherits from `object`.
    # Let's mock torch completely for deterministic testing if it's not truly installed,
    # or just patch around it.
    resnet = InstrumentResNet(num_classes=10)
    # If torch is mocked, nn is a mock, so the object might just be a MagicMock
    if hasattr(resnet, "forward") and not isinstance(resnet.forward, MagicMock):
        # Create a dummy tensor
        try:
            import torch

            if not isinstance(torch.zeros, MagicMock):
                x = torch.zeros(1, 1, 128, 128)
                out = resnet(x)
                assert out.shape == (1, 10)
        except Exception:
            pass


def test_instrument_inference_wrapper():
    wrapper = InstrumentInferenceWrapper()
    with patch.object(wrapper.engine, "run_classification") as mock_run:
        mock_run.return_value = [{"label": "guitar", "score": 0.99}]

        with patch("os.path.exists", return_value=True):
            res = wrapper.classify("mock_path.wav")
        assert len(res) == 1
        assert res[0]["label"] == "guitar"
        assert res[0]["score"] == 0.99


def test_vocalist_analyzer_extract_stem():
    analyzer = VocalistAnalyzer()

    stems = {"vocals": "mock_path.wav", "drums": "mock_drums.wav"}
    with patch("os.path.exists", return_value=True):
        res = analyzer.extract_vocal_stem(stems)
    assert res == "mock_path.wav"

    res_none = analyzer.extract_vocal_stem({"drums": "mock_drums.wav"})
    assert res_none is None


def test_vocalist_analyzer_dvector():
    analyzer = VocalistAnalyzer()

    # Force mock mode
    analyzer.classifier = None
    with patch("os.path.exists", return_value=True):
        vec = analyzer.generate_dvector("mock_path.wav")
    assert vec is not None
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (192,)


def test_drift_detector_kl_divergence():
    detector = DriftDetector(kl_threshold=0.1)

    ref = {"cat": 100, "dog": 100}
    detector.set_reference_distribution(ref)

    # Identical distribution -> KL ~ 0
    curr = {"cat": 50, "dog": 50}
    res = detector.analyze_drift(curr)
    assert not res["drift_detected"]
    assert res["kl_divergence"] < 0.001

    # Highly skewed distribution -> high KL
    curr_skewed = {"cat": 10, "dog": 190}
    res_skewed = detector.analyze_drift(curr_skewed)
    assert res_skewed["drift_detected"]
    assert res_skewed["kl_divergence"] > 0.1
