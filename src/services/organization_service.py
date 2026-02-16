"""
Auralis - Organization Service
Handles file scanning, filename sanitization, and library organization.
"""

import logging
import os
import re
import shutil
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger("auralis.organization")

AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg", ".aiff", ".wma", ".aac"}


class OrganizationService:
    """Service for organizing music files"""

    def __init__(self):
        pass

    def scan_directory(self, root_dir: str) -> List[str]:
        """
        recursively scan a directory for music files.

        Args:
            root_dir (str): Root directory to scan.

        Returns:
            List[str]: List of absolute paths to music files.
        """
        music_files = []
        try:
            for root, _, files in os.walk(root_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in AUDIO_EXTENSIONS:
                        music_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"Error scanning directory {root_dir}: {str(e)}")

        return music_files

    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize a filename component (e.g. Artist, Title).
        Removes invalid filesystem characters and trims whitespace.

        Args:
            name (str): The string to sanitize.

        Returns:
            str: Sanitized string.
        """
        if not name:
            return "Unknown"

        # Remove invalid filesystem characters for Windows/Linux/macOS
        # Windows invalid: < > : " / \ | ? *
        # We also replace control characters
        cleaned = re.sub(r'[<>:"/\\|?*]', "_", name)

        # Remove leading/trailing periods and spaces
        cleaned = cleaned.strip(". ")

        # Replace multiple spaces with single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned or "Unknown"

    def organize_file(
        self, file_path: str, metadata: Dict, target_root_dir: str, move: bool = False
    ) -> Optional[str]:
        """
        Organize a single file into the library structure.
        Structure: target_root_dir/Artist/Album/Title.ext

        Args:
            file_path (str): Current absolute path of the file.
            metadata (Dict): Metadata dictionary (must contain 'artist', 'title', 'album').
            target_root_dir (str): Root directory of the organized library.
            move (bool): If True, move the file. If False, copy.

        Returns:
            Optional[str]: New path if successful, None otherwise.
        """
        try:
            # Extract metadata
            artist = metadata.get("artist", "Unknown Artist")
            album = metadata.get("album", "Unknown Album")
            title = metadata.get("title", "Unknown Title")

            # Sanitize components
            clean_artist = self.sanitize_filename(artist)
            clean_album = self.sanitize_filename(album)
            clean_title = self.sanitize_filename(title)

            # Get extension
            ext = os.path.splitext(file_path)[1].lower()

            # Construct new filename
            new_filename = f"{clean_title}{ext}"

            # Construct target directory
            target_dir = os.path.join(target_root_dir, clean_artist, clean_album)

            # Create target directory
            os.makedirs(target_dir, exist_ok=True)

            # Target path
            target_path = os.path.join(target_dir, new_filename)

            # Avoid overwriting existing files (append counter if needed)
            counter = 1
            base_target_path = target_path
            while os.path.exists(target_path) and os.path.abspath(target_path) != os.path.abspath(
                file_path
            ):
                name, ext = os.path.splitext(base_target_path)
                target_path = f"{name} ({counter}){ext}"
                counter += 1

            if os.path.abspath(target_path) == os.path.abspath(file_path):
                # File is already in place
                return target_path

            # Move or Copy
            if move:
                shutil.move(file_path, target_path)
                logger.info(f"Moved: {file_path} -> {target_path}")
            else:
                shutil.copy2(file_path, target_path)
                logger.info(f"Copied: {file_path} -> {target_path}")

            return target_path

        except Exception as e:
            logger.error(f"Error organizing file {file_path}: {str(e)}")
            return None
