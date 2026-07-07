import sys
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.services.ai.instrument_classifier import InstrumentClassifier, InstrumentInferenceWrapper


def test_fine_tune_success():
    """Test fine tuning an instrument when torch is available."""
    classifier = InstrumentClassifier()
    # Assuming torch is available in test env, this should return True for Sitar
    # If torch is not available, it might return False. We check sys.modules for torch.
    if "torch" in sys.modules and sys.modules["torch"] is not None:
        assert classifier.fine_tune("Sitar", num_epochs=5, data_path="/data") is True
    else:
        assert classifier.fine_tune("Sitar", num_epochs=5, data_path="/data") is False


def test_fine_tune_invalid_instrument():
    """Test fine tuning an unsupported instrument."""
    classifier = InstrumentClassifier()
    if "torch" in sys.modules and sys.modules["torch"] is not None:
        assert classifier.fine_tune("Kazoo") is False


@patch("src.services.ai.instrument_classifier.torch", None)
def test_fine_tune_no_torch():
    """Test fine tuning when torch is mocked as None."""
    classifier = InstrumentClassifier()
    assert classifier.fine_tune("Sitar") is False


def test_predict_mock():
    """Test prediction when mock is forced (e.g. torchaudio missing)."""
    with patch("src.services.ai.instrument_classifier.T", None):
        classifier = InstrumentClassifier()
        predictions = classifier.predict(np.zeros(10))
        assert len(predictions) > 0
        assert predictions[0]["instrument"] == "Guitar"


@patch("src.services.ai.instrument_classifier.InstrumentResNet")
def test_predict_torch(mock_resnet):
    """Test prediction with mocked torch behavior."""
    if "torch" not in sys.modules or sys.modules["torch"] is None:
        pytest.skip("torch not available")

    import torch

    mock_model_instance = MagicMock()
    mock_model_instance.return_value = torch.tensor([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    mock_resnet.return_value = mock_model_instance

    classifier = InstrumentClassifier()
    classifier.device = torch.device("cpu")
    classifier.model = mock_model_instance

    # Mock torchaudio transform
    with patch("src.services.ai.instrument_classifier.T") as mock_T:
        mock_transform = MagicMock()
        mock_transform.return_value = torch.zeros((1, 1, 128, 100))
        mock_T.MelSpectrogram.return_value = mock_transform

        # Reinject mock_T if it's currently None
        classifier.mel_transform = mock_transform

        predictions = classifier.predict(np.zeros(22050))
        assert len(predictions) == 10
        # The probability calculation might vary based on softmax,
        # but Guitar should be the top since its logit is 1.0 vs 0.0 for others.
        assert predictions[0]["instrument"] == "Guitar"


@patch("src.services.ai.instrument_classifier.NeuralInferenceEngine")
def test_inference_wrapper_classify(mock_engine_cls):
    """Test InstrumentInferenceWrapper classify method."""
    mock_engine = MagicMock()
    mock_engine_cls.return_value = mock_engine

    # Setup mock results
    mock_engine.run_classification.return_value = [
        {"label": "Sitar", "score": 0.95},
        {"label": "Tabla", "score": 0.05}
    ]

    wrapper = InstrumentInferenceWrapper()

    # Patch os.path.exists to return True
    with patch("os.path.exists", return_value=True):
        results = wrapper.classify("/fake/path.wav")
        assert len(results) == 2
        assert results[0]["label"] == "Sitar"
        assert results[0]["score"] == 0.95


@patch("src.services.ai.instrument_classifier.NeuralInferenceEngine")
def test_inference_wrapper_classify_fallback(mock_engine_cls):
    """Test InstrumentInferenceWrapper fallback."""
    mock_engine = MagicMock()
    mock_engine_cls.return_value = mock_engine

    # Return empty results to trigger fallback
    mock_engine.run_classification.return_value = []

    wrapper = InstrumentInferenceWrapper()

    with patch("os.path.exists", return_value=True):
        results = wrapper.classify("/fake/path.wav")
        assert len(results) == 1
        assert results[0]["label"] == "guitar"
