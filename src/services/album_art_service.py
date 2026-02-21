"""
Auralis - Album Art Service

Handles fetching and filtering album art images.
"""

import logging
from io import BytesIO
from typing import Optional, Tuple

import requests  # type: ignore
from PIL import Image  # type: ignore

# Set up logging
logger = logging.getLogger("auralis.album_art")


class AlbumArtFetcher:
    """Fetcher for album art with size filtering capabilities."""

    @staticmethod
    def fetch_art(
        url: str, min_size: Tuple[int, int] = (500, 500), timeout: int = 10
    ) -> Optional[Tuple[bytes, str]]:
        """
        Fetch album art from URL and verify size.

        Args:
            url (str): URL of the image.
            min_size (Tuple[int, int]): Minimum (width, height).
            timeout (int): Request timeout in seconds.

        Returns:
            Optional[Tuple[bytes, str]]: Tuple of (image_data, mime_type) if successful and meets criteria, else None.
        """
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch art from {url}: Status {response.status_code}")
                return None

            image_data = response.content

            # Check size
            try:
                img = Image.open(BytesIO(image_data))
                width, height = img.size

                if width < min_size[0] or height < min_size[1]:
                    logger.info(f"Image too small: {width}x{height} < {min_size}")
                    return None

                mime_type = response.headers.get("Content-Type", "image/jpeg")
                # Normalize mime type if needed, but usually headers are fine or we can guess from img.format
                if not mime_type or "image" not in mime_type:
                    mime_type = Image.MIME.get(img.format, "image/jpeg")

                return image_data, mime_type

            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Error fetching art: {str(e)}")
            return None
