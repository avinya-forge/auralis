import subprocess
from unittest.mock import MagicMock, patch


from src.services.audio.demixer import DemucsWrapper


def test_demucs_wrapper_success():
    wrapper = DemucsWrapper()
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        stems = wrapper.demix("test.mp3", "/out")

        mock_run.assert_called_once()
        assert stems is not None
        assert "vocals" in stems
        assert "drums" in stems


def test_demucs_wrapper_oom_error():
    wrapper = DemucsWrapper()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            137, "cmd", stderr="CUDA out of memory"
        )

        stems = wrapper.demix("test.mp3", "/out")

        assert stems is None


def test_demucs_wrapper_other_error():
    wrapper = DemucsWrapper()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Unexpected")

        stems = wrapper.demix("test.mp3", "/out")

        assert stems is None
