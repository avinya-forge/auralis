from src.utils.audio_utils import get_audio_metadata, is_audio_file


def test_is_audio_file():
    assert is_audio_file("t.mp3") is True


def test_get_audio_metadata_missing():
    try:
        get_audio_metadata("missing.mp3")
    except Exception:
        pass
