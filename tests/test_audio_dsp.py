from unittest.mock import MagicMock, patch

import pytest

from src.services.audio.dsp_engine import DSPEngine
from src.utils.audio.cache import AudioCacheManager
from src.utils.audio.spectrogram import generate_mel_spectrogram


@pytest.fixture
def engine():
    return DSPEngine(sr=22050)


def test_extract_chroma(engine):
    with patch("src.services.audio.dsp_engine.librosa") as mock_librosa, patch(
        "src.services.audio.dsp_engine.np"
    ) as mock_np:

        mock_array = [1, 2, 3]
        mock_librosa.feature.chroma_cqt.return_value = mock_array

        # We need np.array to return the mock_array, since that's what we assert
        mock_np.array.return_value = mock_array

        y = MagicMock()
        mock_np.random.randn.return_value = 0

        chroma = engine.extract_chroma(y)

        assert chroma == mock_array


def test_extract_rhythm(engine):
    with patch("src.services.audio.dsp_engine.librosa") as mock_librosa:
        mock_librosa.onset.onset_strength.return_value = "onset"
        mock_librosa.beat.beat_track.return_value = (120.0, "beats")

        y = MagicMock()
        rhythm = engine.extract_rhythm(y)

        assert rhythm is not None
        assert rhythm["bpm"] == 120.0
        assert rhythm["onset_strength"] == "onset"
        assert rhythm["beats"] == "beats"


def test_generate_mel_spectrogram():
    with patch("src.utils.audio.spectrogram.torch") as mock_torch, patch(
        "src.utils.audio.spectrogram.T"
    ) as mock_T, patch("src.utils.audio.spectrogram.np") as mock_np:

        mock_tensor = MagicMock()
        mock_tensor.dim.return_value = 1
        mock_torch.from_numpy.return_value.float.return_value = mock_tensor
        mock_tensor.unsqueeze.return_value = mock_tensor

        mock_transform = MagicMock()
        mock_T.MelSpectrogram.return_value = mock_transform
        mock_transform.return_value = MagicMock()

        mock_db_transform = MagicMock()
        mock_T.AmplitudeToDB.return_value = mock_db_transform

        mock_db = MagicMock()
        mock_db.min.return_value = -80.0
        mock_db.max.return_value = 0.0

        mock_math_result = MagicMock()
        mock_db.__sub__.return_value = mock_math_result
        mock_math_result.__truediv__.return_value = mock_math_result
        mock_db_transform.return_value = mock_db

        # When calling np.array on the numpy representation, return our expected list
        mock_final_array = [1, 2, 3]
        mock_np.array.return_value = mock_final_array

        y = MagicMock()
        mel = generate_mel_spectrogram(y)

        assert mel == mock_final_array


def test_audio_cache_manager(tmp_path):
    manager = AudioCacheManager(str(tmp_path), max_size_bytes=100)

    file1 = tmp_path / "file1.wav"
    file1.write_bytes(b"0" * 60)

    file2 = tmp_path / "file2.wav"
    file2.write_bytes(b"0" * 50)

    with patch.object(
        manager,
        "_get_files_with_stats",
        return_value=[(file1, 100, 60), (file2, 200, 50)],  # older  # newer
    ):
        freed = manager.cleanup()
        assert freed == 60
