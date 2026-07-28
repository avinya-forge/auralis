from unittest.mock import MagicMock, PropertyMock, patch

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

from src.utils.audio_utils import (
    FLAC_TAG_MAP,
    MP3_TAG_MAP,
    AudioMetadataHandler,
    get_album_art,
    get_audio_fingerprint,
    get_audio_metadata,
    is_audio_file,
    set_album_art,
    set_audio_metadata,
)


class TestAudioMetadataHandler:
    @patch("src.utils.audio_utils.mutagen.File")
    def test_init_and_load_audio_success(self, mock_mutagen_file):
        mock_mutagen_file.return_value = MagicMock()
        handler = AudioMetadataHandler("test.mp3")
        assert handler.is_valid()
        assert handler.ext == ".mp3"
        mock_mutagen_file.assert_called_once_with("test.mp3")

    @patch("src.utils.audio_utils.mutagen.File", side_effect=Exception("Load error"))
    def test_init_and_load_audio_failure(self, mock_mutagen_file):
        handler = AudioMetadataHandler("test.mp3")
        assert not handler.is_valid()
        assert handler.audio is None

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_none(self, mock_mutagen_file):
        mock_mutagen_file.side_effect = Exception("Load error")
        handler = AudioMetadataHandler("test.mp3")
        assert handler.get_metadata() == {}

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_mp3(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_audio.__class__ = FLAC
        mock_audio.__class__ = MP3
        mock_audio.__contains__.side_effect = lambda x: x in MP3_TAG_MAP.values()
        mock_audio.__getitem__.side_effect = lambda x: f"value_{x}"
        mock_audio.info = MagicMock(bitrate=128000, length=120)
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        metadata = handler.get_metadata()

        assert metadata["artist"] == "value_TPE1"
        assert metadata["title"] == "value_TIT2"
        assert metadata["bitrate"] == 128000
        assert metadata["length"] == 120

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_flac(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_audio.__contains__.side_effect = lambda x: x in FLAC_TAG_MAP.values()
        mock_audio.__getitem__.side_effect = lambda x: [f"value_{x}"]
        mock_audio.info = MagicMock(bits_per_sample=16, sample_rate=44100, length=180)
        del mock_audio.info.bitrate
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.flac")
        metadata = handler.get_metadata()

        assert metadata["artist"] == "value_artist"
        assert metadata["bitrate"] == 16 * 44100
        assert metadata["length"] == 180

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_metadata_generic(self, mock_mutagen_file):
        mock_audio = MagicMock()  # generic
        mock_audio.__contains__.side_effect = lambda x: x in [
            "artist",
            "title",
            "album",
            "date",
            "genre",
            "tracknumber",
        ]
        mock_audio.__getitem__.side_effect = lambda x: [f"value_{x}"]
        mock_audio.info = MagicMock(length=200)
        del mock_audio.info.bitrate
        del mock_audio.info.bits_per_sample
        del mock_audio.info.sample_rate
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.ogg")
        metadata = handler.get_metadata()

        assert metadata["artist"] == "value_artist"
        assert metadata["title"] == "value_title"
        assert metadata["length"] == 200
        assert "bitrate" not in metadata

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_none(self, mock_mutagen_file):
        mock_mutagen_file.side_effect = Exception("Load error")
        handler = AudioMetadataHandler("test.mp3")
        assert handler.set_metadata({"artist": "test"}) is False

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_mp3(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        success = handler.set_metadata({"artist": "Test Artist", "title": "Test Title"})

        assert success
        assert mock_audio.__setitem__.call_count == 2
        mock_audio.save.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_flac(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.flac")
        success = handler.set_metadata({"artist": "Test Artist", "year": "2023"})

        assert success
        assert mock_audio.__setitem__.call_count == 2
        mock_audio.save.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_generic(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.ogg")
        success = handler.set_metadata({"artist": "Test Artist", "invalid_tag": "Test"})

        assert success
        # Only valid generic tags should be set
        mock_audio.__setitem__.assert_called_once_with("artist", "Test Artist")
        mock_audio.save.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_metadata_exception(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_audio.save.side_effect = Exception("Save error")
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        success = handler.set_metadata({"artist": "Test Artist"})
        assert not success

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_album_art_none(self, mock_mutagen_file):
        mock_mutagen_file.side_effect = Exception("Load error")
        handler = AudioMetadataHandler("test.mp3")
        assert handler.set_album_art(image_data=b"data") is False

    @patch("src.utils.audio_utils.mutagen.File")
    @patch("src.utils.audio_utils.requests.get")
    def test_set_album_art_download_success(self, mock_get, mock_mutagen_file):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"image_data"
        mock_get.return_value = mock_response

        mock_audio = MagicMock()
        mock_audio.tags = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        success = handler.set_album_art(image_url="http://example.com/image.jpg")

        assert success
        mock_audio.tags.add.assert_called_once()
        mock_audio.save.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    @patch("src.utils.audio_utils.requests.get")
    def test_set_album_art_download_fail(self, mock_get, mock_mutagen_file):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        handler = AudioMetadataHandler("test.mp3")
        assert handler.set_album_art(image_url="http://example.com/image.jpg") is False

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_album_art_mp3_no_tags(self, mock_mutagen_file):
        mock_audio = MagicMock()
        del mock_audio.tags
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        success = handler.set_album_art(image_data=b"data")

        assert success
        mock_audio.add_tags.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_album_art_flac(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.flac")
        success = handler.set_album_art(image_data=b"data")

        assert success
        mock_audio.add_picture.assert_called_once()
        mock_audio.save.assert_called_once()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_set_album_art_invalid_format(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.ogg")
        success = handler.set_album_art(image_data=b"data")
        assert not success

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_none(self, mock_mutagen_file):
        mock_mutagen_file.side_effect = Exception("Load error")
        handler = AudioMetadataHandler("test.mp3")
        assert handler.get_album_art() is None

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_mp3_success(self, mock_mutagen_file):
        mock_tag = MagicMock()
        mock_tag.FrameID = "APIC"
        mock_tag.data = b"image_data"

        mock_audio = MagicMock()
        mock_audio.tags.values.return_value = [mock_tag]
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        assert handler.get_album_art() == b"image_data"

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_flac_success(self, mock_mutagen_file):
        mock_pic = MagicMock()
        mock_pic.data = b"image_data"

        mock_audio = MagicMock()
        mock_audio.pictures = [mock_pic]
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.flac")
        assert handler.get_album_art() == b"image_data"

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_invalid_format(self, mock_mutagen_file):
        mock_audio = MagicMock()
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.ogg")
        assert handler.get_album_art() is None

    @patch("src.utils.audio_utils.mutagen.File")
    def test_get_album_art_exception(self, mock_mutagen_file):
        mock_audio = MagicMock()
        type(mock_audio).tags = PropertyMock(side_effect=Exception("Access error"))
        mock_mutagen_file.return_value = mock_audio

        handler = AudioMetadataHandler("test.mp3")
        assert handler.get_album_art() is None


class TestHelperFunctions:
    @patch("src.utils.audio_utils.AudioMetadataHandler")
    def test_get_audio_metadata(self, mock_handler_class):
        mock_handler = MagicMock()
        mock_handler.get_metadata.return_value = {"title": "Test"}
        mock_handler_class.return_value = mock_handler

        assert get_audio_metadata("test.mp3") == {"title": "Test"}
        mock_handler_class.assert_called_once_with("test.mp3")

    @patch("src.utils.audio_utils.AudioMetadataHandler")
    def test_set_audio_metadata(self, mock_handler_class):
        mock_handler = MagicMock()
        mock_handler.set_metadata.return_value = True
        mock_handler_class.return_value = mock_handler

        assert set_audio_metadata("test.mp3", {"title": "Test"}) is True
        mock_handler_class.assert_called_once_with("test.mp3")

    @patch("src.utils.audio_utils.AudioMetadataHandler")
    def test_set_album_art(self, mock_handler_class):
        mock_handler = MagicMock()
        mock_handler.set_album_art.return_value = True
        mock_handler_class.return_value = mock_handler

        assert set_album_art("test.mp3", image_url="url", image_data=b"data") is True
        mock_handler_class.assert_called_once_with("test.mp3")

    @patch("src.utils.audio_utils.AudioMetadataHandler")
    def test_get_album_art(self, mock_handler_class):
        mock_handler = MagicMock()
        mock_handler.get_album_art.return_value = b"data"
        mock_handler_class.return_value = mock_handler

        assert get_album_art("test.mp3") == b"data"
        mock_handler_class.assert_called_once_with("test.mp3")

    @patch("src.utils.audio_utils.acoustid.fingerprint_file")
    def test_get_audio_fingerprint_success(self, mock_fingerprint):
        mock_fingerprint.return_value = (120.0, "fingerprint_string")
        assert get_audio_fingerprint("test.mp3") == (120.0, "fingerprint_string")

    @patch("src.utils.audio_utils.acoustid.fingerprint_file")
    def test_get_audio_fingerprint_failure(self, mock_fingerprint):
        mock_fingerprint.side_effect = Exception("Fingerprint error")
        assert get_audio_fingerprint("test.mp3") == (None, None)

    @patch("src.utils.audio_utils.mutagen.File")
    def test_is_audio_file_valid(self, mock_mutagen_file):
        mock_mutagen_file.return_value = MagicMock()
        assert is_audio_file("test.mp3") is True

    @patch("src.utils.audio_utils.mutagen.File")
    def test_is_audio_file_invalid_ext(self, mock_mutagen_file):
        assert is_audio_file("test.txt") is False
        mock_mutagen_file.assert_not_called()

    @patch("src.utils.audio_utils.mutagen.File")
    def test_is_audio_file_exception(self, mock_mutagen_file):
        mock_mutagen_file.side_effect = Exception("Load error")
        assert is_audio_file("test.mp3") is False
