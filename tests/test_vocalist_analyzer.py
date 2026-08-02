import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.services.ai.vocalist_analyzer import VocalistAnalyzer


@pytest.fixture
def vocalist_analyzer():
    # Force speechbrain mock during initialization to prevent download attempts
    with patch("src.services.ai.vocalist_analyzer.speechbrain", None):
        return VocalistAnalyzer()


def test_extract_vocal_stem(vocalist_analyzer):
    # Missing stem
    assert vocalist_analyzer.extract_vocal_stem({"drums": "path"}) is None

    # Missing file
    assert vocalist_analyzer.extract_vocal_stem({"vocals": "/nonexistent/path/vocals.wav"}) is None

    # Valid file
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
        assert vocalist_analyzer.extract_vocal_stem({"vocals": tmp_file.name}) == tmp_file.name


def test_generate_dvector(vocalist_analyzer):
    # Non-existent file
    assert vocalist_analyzer.generate_dvector("/nonexistent/path.wav") is None

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
        # Mock mode (classifier is None)
        vocalist_analyzer.classifier = None
        dvector = vocalist_analyzer.generate_dvector(tmp_file.name)
        assert dvector is not None
        assert isinstance(dvector, np.ndarray)
        assert dvector.shape == (192,)

        # Mock mode with np = None
        with patch("src.services.ai.vocalist_analyzer.np", None):
            assert vocalist_analyzer.generate_dvector(tmp_file.name) is None

        # With mock classifier
        mock_classifier = MagicMock()
        mock_classifier.load_audio.return_value = "signal"
        mock_embeddings = MagicMock()
        mock_embeddings.squeeze.return_value.cpu.return_value.numpy.return_value = np.zeros(192)
        mock_classifier.encode_batch.return_value = mock_embeddings

        vocalist_analyzer.classifier = mock_classifier
        result = vocalist_analyzer.generate_dvector(tmp_file.name)
        assert np.array_equal(result, np.zeros(192))

        # Exception path
        mock_classifier.encode_batch.side_effect = Exception("Test Exception")
        assert vocalist_analyzer.generate_dvector(tmp_file.name) is None


def test_extract_signature(vocalist_analyzer):
    dummy_audio = np.zeros(16000, dtype=np.float32)

    # Mock mode
    vocalist_analyzer.classifier = None
    sig = vocalist_analyzer.extract_signature(dummy_audio)
    assert sig is not None
    assert sig.shape == (192,)

    # With mock classifier and torch
    mock_classifier = MagicMock()
    mock_embeddings = MagicMock()
    mock_embeddings.squeeze.return_value.cpu.return_value.numpy.return_value = np.ones(192)
    mock_classifier.encode_batch.return_value = mock_embeddings

    vocalist_analyzer.classifier = mock_classifier

    # We patch torch in sys.modules
    mock_torch = MagicMock()
    mock_tensor = MagicMock()
    mock_tensor.dim.return_value = 1
    mock_torch.from_numpy.return_value.float.return_value = mock_tensor
    mock_torch.no_grad = MagicMock()

    with patch.dict("sys.modules", {"torch": mock_torch}):
        sig2 = vocalist_analyzer.extract_signature(dummy_audio)
        assert np.array_equal(sig2, np.ones(192))

        # Exception path
        mock_torch.from_numpy.side_effect = Exception("Torch Exception")
        assert vocalist_analyzer.extract_signature(dummy_audio) is None


def test_compare_signatures(vocalist_analyzer):
    sig1 = np.ones(192)
    sig2 = np.ones(192)

    # Identical signatures
    similarity = vocalist_analyzer.compare_signatures(sig1, sig2)
    assert pytest.approx(similarity) == 1.0

    # Zero division
    sig_zero = np.zeros(192)
    assert vocalist_analyzer.compare_signatures(sig1, sig_zero) == 0.0

    # Exception
    assert vocalist_analyzer.compare_signatures(None, sig2) == 0.0


def test_load_model():
    # Test loading model when speechbrain is available
    mock_speechbrain = MagicMock()
    mock_classifier = MagicMock()
    mock_classifier.from_hparams.return_value = "classifier_instance"

    with patch.dict("sys.modules", {"speechbrain": mock_speechbrain}):
        with patch("src.services.ai.vocalist_analyzer.speechbrain", mock_speechbrain):
            with patch(
                "src.services.ai.vocalist_analyzer.EncoderClassifier", mock_classifier, create=True
            ):
                analyzer = VocalistAnalyzer()
                assert analyzer.classifier == "classifier_instance"

                # Test exception path
                mock_classifier.from_hparams.side_effect = Exception("Load error")
                analyzer_fail = VocalistAnalyzer()
                assert analyzer_fail.classifier is None


def test_analyze_vocal_characteristics(vocalist_analyzer):
    dummy_audio = np.zeros(16000, dtype=np.float32)

    # Mock mode
    vocalist_analyzer.classifier = None
    results = vocalist_analyzer.analyze_vocal_characteristics(dummy_audio)

    assert results["has_vocals"] is True
    assert results["vocal_intensity"] == 0.75
    assert results["estimated_gender"] == "Unknown"
    assert isinstance(results["signature_vector"], list)
    assert len(results["signature_vector"]) == 192

    # None signature fallback (should return empty list for vector)
    with patch.object(vocalist_analyzer, "extract_signature", return_value=None):
        results_none = vocalist_analyzer.analyze_vocal_characteristics(dummy_audio)
        assert results_none["signature_vector"] == []
