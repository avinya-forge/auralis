from unittest.mock import MagicMock, patch

import numpy as np

from src.services.audio.dsp_engine import DSPEngine


def test_dspe_init():
    # Test different init parameters
    engine = DSPEngine(sr=16000)
    assert engine.sr == 16000
    assert engine.sample_rate == 16000

    engine = DSPEngine(sample_rate=44100)
    assert engine.sr == 44100
    assert engine.sample_rate == 44100

    engine = DSPEngine(sr=48000, sample_rate=48000)
    assert engine.sr == 48000
    assert engine.sample_rate == 48000


def test_extract_chroma():
    y = np.zeros(1024)
    engine = DSPEngine()

    # Test without librosa
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", False):
        assert engine.extract_chroma(y) is None

    # Test with librosa
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", True):
        mock_librosa = MagicMock()
        mock_librosa.feature.chroma_cqt.return_value = np.zeros((12, 10))

        with patch("src.services.audio.dsp_engine.librosa", mock_librosa):
            chroma = engine.extract_chroma(y)
            assert chroma is not None
            assert chroma.shape == (12, 10)

            # Test exception
            mock_librosa.feature.chroma_cqt.side_effect = Exception("CQT Error")
            assert engine.extract_chroma(y) is None


def test_extract_rhythm():
    y = np.zeros(1024)
    engine = DSPEngine()

    # Test without librosa
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", False):
        assert engine.extract_rhythm(y) is None

    # Test with librosa (tempo as array)
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", True):
        mock_librosa = MagicMock()
        mock_librosa.onset.onset_strength.return_value = np.zeros(10)
        mock_librosa.beat.beat_track.return_value = (np.array([120.0]), np.array([10, 20]))

        with patch("src.services.audio.dsp_engine.librosa", mock_librosa):
            rhythm = engine.extract_rhythm(y)
            assert rhythm is not None
            assert rhythm["bpm"] == 120.0

            # Test with tempo as float
            mock_librosa.beat.beat_track.return_value = (130.0, np.array([10, 20]))
            rhythm2 = engine.extract_rhythm(y)
            assert rhythm2["bpm"] == 130.0

            # Test exception
            mock_librosa.beat.beat_track.side_effect = Exception("Rhythm Error")
            assert engine.extract_rhythm(y) is None


def test_extract_features():
    engine = DSPEngine()

    # Test without librosa
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", False):
        features = engine.extract_features("dummy.wav")
        assert features is not None
        assert features["bpm"] == 120.0
        assert features["key"] == "C"

    # Test with librosa
    with patch("src.services.audio.dsp_engine.LIBROSA_AVAILABLE", True):
        mock_librosa = MagicMock()
        mock_librosa.load.return_value = (np.zeros(1024), 22050)
        mock_librosa.beat.beat_track.return_value = (np.array([120.0]), None)

        # Mock chroma
        mock_chroma = np.zeros((12, 10))
        mock_chroma[0, :] = 1.0  # Make 'C' the dominant key
        mock_librosa.feature.chroma_stft.return_value = mock_chroma

        with patch("src.services.audio.dsp_engine.librosa", mock_librosa):
            features = engine.extract_features("dummy.wav")
            assert features is not None
            assert features["bpm"] == 120.0
            assert features["key"] == "C"

            # Test exception
            mock_librosa.load.side_effect = Exception("Load Error")
            assert engine.extract_features("dummy.wav") is None


def test_estimate_key():
    engine = DSPEngine()

    # Test invalid chroma mean
    assert engine._estimate_key([]) == "Unknown"
    assert engine._estimate_key([1.0] * 11) == "Unknown"

    # Test valid keys
    chroma = [0.0] * 12
    chroma[0] = 1.0  # C
    assert engine._estimate_key(chroma) == "C"

    chroma = [0.0] * 12
    chroma[2] = 1.0  # D
    assert engine._estimate_key(chroma) == "D"
