import os
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.services.ai.instrument_classifier import (
    InstrumentResNet,
    InstrumentInferenceWrapper,
    InstrumentClassifier,
)

def test_resnet_init_and_forward():
    # Test without torch
    resnet = InstrumentResNet()

    # Forward should raise RuntimeError if nn is None (or torch is None, but the mock will handle it)
    with pytest.raises(RuntimeError):
        resnet.forward(MagicMock())

    # Test with torch mocked
    mock_torch = MagicMock()
    mock_nn = MagicMock()

    class MockModule:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return args[0]

    mock_nn.Module = MockModule
    mock_nn.Conv2d = lambda *args, **kwargs: MagicMock()
    mock_nn.BatchNorm2d = lambda *args, **kwargs: MagicMock()
    mock_nn.ReLU = lambda *args, **kwargs: MagicMock()
    mock_nn.MaxPool2d = lambda *args, **kwargs: MagicMock()
    mock_nn.AdaptiveAvgPool2d = lambda *args, **kwargs: MagicMock()
    mock_nn.Linear = lambda *args, **kwargs: MagicMock()
    mock_nn.Sequential = lambda *args, **kwargs: MagicMock()

    with patch("src.services.ai.instrument_classifier.nn", mock_nn), \
         patch("src.services.ai.instrument_classifier.torch", mock_torch):
        resnet_with_torch = InstrumentResNet()
        assert resnet_with_torch.conv1 is not None

        # Test forward pass
        dummy_input = MagicMock()
        mock_torch.flatten.return_value = dummy_input
        output = resnet_with_torch.forward(dummy_input)
        assert output is not None

def test_inference_wrapper_classify():
    wrapper = InstrumentInferenceWrapper()

    # Test file not found
    assert wrapper.classify("/nonexistent/file.wav") == []

    # Test classify with mock engine
    with patch("os.path.exists", return_value=True):
        wrapper.engine.run_classification = MagicMock(return_value=[{"label": "guitar", "score": 0.9}])
        result = wrapper.classify("dummy.wav")
        assert result == [{"label": "guitar", "score": 0.9}]

        # Test fallback when engine returns empty
        wrapper.engine.run_classification = MagicMock(return_value=[])
        result_empty = wrapper.classify("dummy.wav")
        assert result_empty == [{"label": "guitar", "score": 0.8}]

        # Test mapping labels
        wrapper.engine.run_classification = MagicMock(return_value=[{"label": "unknown_inst", "score": 0.9}])
        result_unmapped = wrapper.classify("dummy.wav")
        assert result_unmapped == [{"label": "unknown_inst", "score": 0.9}]

def test_classifier_init_and_load():
    # Test without torch
    classifier = InstrumentClassifier()
    assert classifier.mel_transform is None

    # Test load_model without torch (should not raise)
    classifier.load_model("dummy.pth")

    # Test with torch
    mock_torch = MagicMock()
    mock_torch.device.return_value = "cpu"
    mock_torch.cuda.is_available.return_value = False

    with patch("src.services.ai.instrument_classifier.torch", mock_torch), \
         patch("src.services.ai.instrument_classifier.nn", MagicMock()):
        # Mock InstrumentResNet inside the module
        with patch("src.services.ai.instrument_classifier.InstrumentResNet") as mock_resnet_class:
            mock_resnet_inst = MagicMock()
            mock_resnet_class.return_value.to.return_value = mock_resnet_inst

            classifier_with_torch = InstrumentClassifier(model_path="dummy.pth")
            mock_torch.load.assert_called_with("dummy.pth", map_location=mock_torch.device())
            mock_resnet_inst.load_state_dict.assert_called()

            # Test exception path for load_model
            mock_torch.load.side_effect = Exception("Load exception")
            classifier_with_torch.load_model("dummy2.pth")

def test_classifier_fine_tune():
    classifier = InstrumentClassifier()

    # Test without torch
    assert classifier.fine_tune("Guitar") is False

    mock_torch = MagicMock()
    with patch("src.services.ai.instrument_classifier.torch", mock_torch), \
         patch("src.services.ai.instrument_classifier.nn", MagicMock()):

        with patch("src.services.ai.instrument_classifier.InstrumentResNet") as mock_resnet:
            classifier_with_torch = InstrumentClassifier()

            # Invalid instrument
            assert classifier_with_torch.fine_tune("InvalidInst") is False

            # Valid instrument
            assert classifier_with_torch.fine_tune("Guitar") is True

def test_classifier_predict():
    classifier = InstrumentClassifier()
    audio = np.zeros(1024)

    # Test without torchaudio/torch (should return mock)
    results = classifier.predict(audio)
    assert len(results) == 3
    assert results[0]["instrument"] == "Guitar"

    # Test with torch and torchaudio mocked
    mock_torch = MagicMock()
    mock_torch.device.return_value = "cpu"
    mock_T = MagicMock()

    with patch("src.services.ai.instrument_classifier.torch", mock_torch), \
         patch("src.services.ai.instrument_classifier.T", mock_T), \
         patch("src.services.ai.instrument_classifier.nn", MagicMock()):

        with patch("src.services.ai.instrument_classifier.InstrumentResNet") as mock_resnet_cls:
            classifier_with_torch = InstrumentClassifier()
            classifier_with_torch.mel_transform = mock_T

            mock_tensor = MagicMock()
            mock_tensor.dim.return_value = 1
            mock_torch.from_numpy.return_value.float.return_value = mock_tensor

            mock_logits = MagicMock()
            classifier_with_torch.model.return_value = mock_logits

            # Mock softmax returning probabilities
            mock_probs = MagicMock()
            mock_probs.squeeze.return_value.cpu.return_value.numpy.return_value = [0.1, 0.8, 0.1] + [0.0]*7
            mock_torch.softmax.return_value = mock_probs

            results_torch = classifier_with_torch.predict(audio)

            assert len(results_torch) == 10
            # Since probabilities are mocked, we can check that it sorted correctly
            assert results_torch[0]["probability"] == 0.8
            assert results_torch[0]["instrument"] == "Piano"  # second item in instrument list

            # Test dim == 2 path
            mock_tensor.dim.return_value = 2
            classifier_with_torch.predict(audio)

            # Test exception path
            mock_torch.from_numpy.side_effect = Exception("Prediction error")
            results_err = classifier_with_torch.predict(audio)
            assert len(results_err) == 3
            assert results_err[0]["instrument"] == "Guitar"
