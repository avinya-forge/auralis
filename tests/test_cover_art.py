import sys
from unittest.mock import MagicMock, patch
import pytest

# Define Mock Classes
class MockMP3(MagicMock):
    pass

class MockFLAC(MagicMock):
    pass

# We don't need to patch sys.modules here if we patch explicitly in the test methods,
# provided we can import MetadataService safely.
# If MetadataService import fails due to missing modules, we still need sys.modules patches.
# Assuming conftest.py handles basic mocking, we can rely on it or override specific parts.

# But conftest.py might mock things in a way incompatible with our specific needs (like MP3 class).
# So we patch where used.

from src.services.metadata_service import MetadataService

class TestCoverArt:
    @pytest.fixture
    def service(self):
        with patch.object(MetadataService, "_init_sources"), \
             patch.object(MetadataService, "_load_stats"):
            service = MetadataService()
            service.sources = {}
            return service

    def test_apply_metadata_with_cover_art_mp3(self, service):
        """Test embedding cover art in MP3"""
        mock_audio = MockMP3()

        # Patch the classes used in the service
        with patch("src.services.metadata_service.mutagen.File", return_value=mock_audio), \
             patch("src.services.metadata_service.mutagen.mp3.MP3", MockMP3), \
             patch("src.services.metadata_service.mutagen.id3.APIC") as mock_apic:

            metadata = {
                "artist": "Artist",
                "title": "Title",
                "cover_art": b"image_data",
                "cover_art_mime": "image/jpeg"
            }

            service._apply_metadata_to_file("/path/to/file.mp3", metadata)

            mock_apic.assert_called()
            mock_audio.__setitem__.assert_any_call("APIC", mock_apic.return_value)
            mock_audio.save.assert_called()

    def test_apply_metadata_with_cover_art_flac(self, service):
        """Test embedding cover art in FLAC"""
        mock_audio = MockFLAC()

        with patch("src.services.metadata_service.mutagen.File", return_value=mock_audio), \
             patch("src.services.metadata_service.mutagen.flac.FLAC", MockFLAC), \
             patch("src.services.metadata_service.mutagen.flac.Picture") as mock_picture:

            metadata = {
                "artist": "Artist",
                "title": "Title",
                "cover_art": b"image_data",
                "cover_art_mime": "image/jpeg"
            }

            mock_pic_instance = MagicMock()
            mock_picture.return_value = mock_pic_instance

            service._apply_metadata_to_file("/path/to/file.flac", metadata)

            mock_picture.assert_called()
            mock_audio.add_picture.assert_called_with(mock_pic_instance)
            mock_audio.save.assert_called()
