"""
Auralis - Genre Service Module

Handles genre classification and management using mutagen.
"""

import logging
from typing import Optional

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


class GenreClassifier:
    """
    Service for managing and classifying music genres.
    """

    def __init__(self) -> None:
        """Initialize the GenreClassifier."""
        self.logger = logging.getLogger(__name__)

    def get_genre(self, file_path: str) -> Optional[str]:
        """
        Get the genre of a music file.

        Args:
            file_path (str): Path to the music file.

        Returns:
            Optional[str]: The genre if found, None otherwise.
        """
        try:
            # Try with EasyID3/Easy wrapper first
            audio = mutagen.File(file_path, easy=True)

            if audio and "genre" in audio and audio["genre"]:
                return str(audio["genre"][0])

            return None
        except Exception as e:
            self.logger.warning(f"Error reading genre from {file_path}: {e}")
            return None

    def set_genre(self, file_path: str, genre: str) -> bool:  # noqa: C901
        """
        Set the genre of a music file.

        Args:
            file_path (str): Path to the music file.
            genre (str): The genre to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not genre:
            return False

        normalized_genre = self.normalize_genre(genre)

        try:
            # Try to load with easy=True
            audio = mutagen.File(file_path, easy=True)

            if audio is None:
                # If valid mp3 but no tags, mutagen.File might return None or fail
                if file_path.lower().endswith(".mp3"):
                    try:
                        audio = EasyID3(file_path)
                    except ID3NoHeaderError:
                        audio = EasyID3()
                        audio.save(file_path)
                else:
                    self.logger.warning(f"Unsupported file type or no handler for: {file_path}")
                    return False

            audio["genre"] = normalized_genre
            audio.save()
            return True

        except Exception as e:
            # Fallback for MP3s with no tags if mutagen.File failed
            if file_path.lower().endswith(".mp3"):
                try:
                    audio = EasyID3(file_path)
                    audio["genre"] = normalized_genre
                    audio.save()
                    return True
                except ID3NoHeaderError:
                    try:
                        audio = EasyID3()
                        audio["genre"] = normalized_genre
                        audio.save(file_path)
                        return True
                    except Exception as e2:
                        self.logger.error(f"Failed to save genre to {file_path}: {e2}")
                        return False
                except Exception as e2:
                    self.logger.error(f"Failed to save genre to {file_path}: {e2}")
                    return False

            self.logger.error(f"Error setting genre for {file_path}: {e}")
            return False

    def normalize_genre(self, genre: str) -> str:
        """
        Normalize genre string (Title Case).

        Args:
            genre (str): The genre string.

        Returns:
            str: Normalized genre string.
        """
        if not genre:
            return ""
        return genre.strip().title()
