import os
import tempfile

import numpy as np
import pytest

from src.services.audio.dsp_engine import DSPEngine


@pytest.fixture
def synthetic_audio_path():
    """Generate a synthetic sine wave and save to a temporary file using simple wave module."""
    import struct
    import wave

    sr = 22050
    t = np.linspace(0, 1.0, sr)
    y = 0.5 * np.sin(2 * np.pi * 440.0 * t)

    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)

        # Convert to 16-bit integers
        y_int = np.int16(y * 32767)
        for sample in y_int:
            w.writeframesraw(struct.pack("<h", sample))

    yield path

    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def synthetic_rhythm_audio_path():
    """Generate a synthetic rhythmic signal (clicks/beats) and save to a temp file using simple wave module."""
    import struct
    import wave

    sr = 22050
    t = np.linspace(0, 5.0, sr * 5)  # 5 seconds
    y = np.zeros_like(t)

    bpm = 120
    interval = 60 / bpm

    for i in range(int(5.0 / interval)):
        idx = int(i * interval * sr)
        if idx < len(y):
            y[idx : min(idx + 100, len(y))] = 1.0

    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)

        # Convert to 16-bit integers
        y_int = np.int16(y * 32767)
        for sample in y_int:
            w.writeframesraw(struct.pack("<h", sample))

    yield path

    if os.path.exists(path):
        os.remove(path)


def test_extract_chroma(synthetic_audio_path):
    assert os.path.exists(synthetic_audio_path)
    chroma = DSPEngine.extract_chroma(synthetic_audio_path)

    assert chroma is not None, f"Extraction failed for {synthetic_audio_path}"
    assert isinstance(chroma, np.ndarray)
    assert chroma.shape[0] == 12
    assert chroma.shape[1] > 0


def test_extract_chroma_invalid_path():
    chroma = DSPEngine.extract_chroma("non_existent_file.wav")
    assert chroma is None


def test_extract_rhythm(synthetic_rhythm_audio_path):
    assert os.path.exists(synthetic_rhythm_audio_path)
    rhythm_data = DSPEngine.extract_rhythm(synthetic_rhythm_audio_path)

    assert rhythm_data is not None, f"Extraction failed for {synthetic_rhythm_audio_path}"
    assert "bpm" in rhythm_data
    assert "onset_strength" in rhythm_data

    assert isinstance(rhythm_data["bpm"], float)
    assert isinstance(rhythm_data["onset_strength"], np.ndarray)
    assert rhythm_data["bpm"] > 0
    assert rhythm_data["onset_strength"].size > 0


def test_extract_rhythm_invalid_path():
    rhythm_data = DSPEngine.extract_rhythm("non_existent_file.wav")
    assert rhythm_data is None
