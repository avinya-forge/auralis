"""
Unit tests for Album Art Service
"""

from unittest.mock import MagicMock, patch

from src.services.album_art_service import AlbumArtFetcher


class TestAlbumArtFetcher:

    @patch("src.services.album_art_service.Image")
    @patch("src.services.album_art_service.requests.get")
    def test_fetch_art_success(self, mock_get, mock_image_cls):
        """Test successful art fetch"""
        # Configure Image mock
        mock_img_instance = MagicMock()
        mock_img_instance.size = (600, 600)
        mock_image_cls.open.return_value = mock_img_instance

        # Create dummy bytes
        img_bytes = b"fake_image_data"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = img_bytes
        mock_response.headers.get.return_value = "image/jpeg"

        mock_get.return_value = mock_response

        result = AlbumArtFetcher.fetch_art("http://example.com/image.jpg")

        assert result is not None
        assert result[0] == img_bytes
        assert result[1] == "image/jpeg"

    @patch("src.services.album_art_service.Image")
    @patch("src.services.album_art_service.requests.get")
    def test_fetch_art_too_small(self, mock_get, mock_image_cls):
        """Test filtering of small images"""
        # Configure Image mock
        mock_img_instance = MagicMock()
        mock_img_instance.size = (400, 400)
        mock_image_cls.open.return_value = mock_img_instance

        img_bytes = b"fake_small_image"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = img_bytes

        mock_get.return_value = mock_response

        result = AlbumArtFetcher.fetch_art("http://example.com/image.jpg", min_size=(500, 500))

        assert result is None
