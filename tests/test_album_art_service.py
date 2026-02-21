"""
Unit tests for Album Art Service
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

from PIL import Image

from src.services.album_art_service import AlbumArtFetcher


class TestAlbumArtFetcher:

    @patch("src.services.album_art_service.requests.get")
    def test_fetch_art_success(self, mock_get):
        """Test successful art fetch"""
        # Create a valid image
        img = Image.new("RGB", (600, 600), color="red")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_bytes = img_byte_arr.getvalue()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = img_bytes
        mock_response.headers.get.return_value = "image/jpeg"

        mock_get.return_value = mock_response

        result = AlbumArtFetcher.fetch_art("http://example.com/image.jpg")

        assert result is not None
        assert result[0] == img_bytes
        assert result[1] == "image/jpeg"

    @patch("src.services.album_art_service.requests.get")
    def test_fetch_art_too_small(self, mock_get):
        """Test filtering of small images"""
        # Create a small image
        img = Image.new("RGB", (400, 400), color="red")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_bytes = img_byte_arr.getvalue()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = img_bytes

        mock_get.return_value = mock_response

        result = AlbumArtFetcher.fetch_art("http://example.com/image.jpg", min_size=(500, 500))

        assert result is None
