"""
Auralis - Audio Utilities Module
"""

import os
from typing import Any, Dict, Optional, Tuple

import acoustid
import mutagen
import requests  # type: ignore
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC, TIT2, TPE1, TRCK
from mutagen.mp3 import MP3

# Constants for metadata mapping
MP3_TAG_MAP = {
    "artist": "TPE1",
    "title": "TIT2",
    "album": "TALB",
    "year": "TDRC",
    "genre": "TCON",
    "track": "TRCK",
}

FLAC_TAG_MAP = {
    "artist": "artist",
    "title": "title",
    "album": "album",
    "year": "date",
    "genre": "genre",
    "track": "tracknumber",
}

# Mapping for MP3 tag classes
MP3_TAG_CLASSES = {
    "artist": TPE1,
    "title": TIT2,
    "album": TALB,
    "year": TDRC,
    "genre": TCON,
    "track": TRCK,
}


class AudioMetadataHandler:
    """
    Handler for audio file metadata operations.
    Encapsulates logic for extracting and applying metadata for different formats.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.audio = None
        self.ext = os.path.splitext(file_path)[1].lower()
        self._load_audio()

    def _load_audio(self):
        """Load the audio file using mutagen"""
        try:
            self.audio = mutagen.File(self.file_path)
        except Exception as e:
            print(f"Error loading audio file {self.file_path}: {str(e)}")
            self.audio = None

    def is_valid(self) -> bool:
        """Check if audio file was loaded successfully"""
        return self.audio is not None

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata from the audio file"""
        if not self.is_valid():
            return {}

        if isinstance(self.audio, MP3):
            return self._extract_mp3_metadata()
        elif isinstance(self.audio, FLAC):
            return self._extract_flac_metadata()
        else:
            return self._extract_generic_metadata()

    def set_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Set metadata for the audio file"""
        if not self.is_valid():
            return False

        try:
            if isinstance(self.audio, MP3):
                self._apply_mp3_metadata(metadata)
            elif isinstance(self.audio, FLAC):
                self._apply_flac_metadata(metadata)
            else:
                self._apply_generic_metadata(metadata)

            self.audio.save()
            return True
        except Exception as e:
            print(f"Error setting metadata for {self.file_path}: {str(e)}")
            return False

    def _extract_mp3_metadata(self) -> Dict[str, Any]:
        """Extract metadata from MP3 file"""
        metadata = {}
        for key, tag in MP3_TAG_MAP.items():
            if tag in self.audio:
                metadata[key] = str(self.audio[tag])

        self._add_audio_info(metadata)
        return metadata

    def _extract_flac_metadata(self) -> Dict[str, Any]:
        """Extract metadata from FLAC file"""
        metadata = {}
        for key, tag in FLAC_TAG_MAP.items():
            if tag in self.audio:
                metadata[key] = str(self.audio[tag][0])

        self._add_audio_info(metadata)
        return metadata

    def _extract_generic_metadata(self) -> Dict[str, Any]:
        """Extract metadata from generic audio file"""
        metadata = {}
        for key in ["artist", "title", "album", "date", "genre", "tracknumber"]:
            if key in self.audio:
                metadata[key] = str(self.audio[key][0])

        self._add_audio_info(metadata)
        return metadata

    def _add_audio_info(self, metadata: Dict[str, Any]):
        """Add audio info (bitrate, length, etc.) to metadata dict"""
        if hasattr(self.audio, "info"):
            if hasattr(self.audio.info, "bitrate"):
                metadata["bitrate"] = self.audio.info.bitrate
            elif hasattr(self.audio.info, "bits_per_sample") and hasattr(
                self.audio.info, "sample_rate"
            ):
                metadata["bitrate"] = self.audio.info.bits_per_sample * self.audio.info.sample_rate

            if hasattr(self.audio.info, "length"):
                metadata["length"] = self.audio.info.length
            if hasattr(self.audio.info, "sample_rate"):
                metadata["sample_rate"] = self.audio.info.sample_rate

    def _apply_mp3_metadata(self, metadata: Dict[str, Any]):
        """Apply metadata to MP3 file"""
        for key, tag_class in MP3_TAG_CLASSES.items():
            if key in metadata:
                tag_name = MP3_TAG_MAP[key]
                self.audio[tag_name] = tag_class(encoding=3, text=metadata[key])

    def _apply_flac_metadata(self, metadata: Dict[str, Any]):
        """Apply metadata to FLAC file"""
        for key, tag in FLAC_TAG_MAP.items():
            if key in metadata:
                self.audio[tag] = metadata[key]

    def _apply_generic_metadata(self, metadata: Dict[str, Any]):
        """Apply metadata to generic audio file"""
        for key, value in metadata.items():
            if key in ["artist", "title", "album", "year", "genre", "track"]:
                self.audio[key] = value

    def set_album_art(
        self, image_url: Optional[str] = None, image_data: Optional[bytes] = None
    ) -> bool:
        """Set album art for the audio file"""
        if not self.is_valid():
            return False

        try:
            if not image_data and image_url:
                response = requests.get(image_url)
                if response.status_code != 200:
                    return False
                image_data = response.content

            if not image_data:
                return False

            # Get appropriate handler for cover art
            # Note: For MP3, we need ID3 specifically, which might be different from self.audio if it's just 'File'
            # But self.audio from mutagen.File() usually returns specific type.

            if self.ext == ".mp3":
                # Ensure we have ID3 tags
                if not self.audio.tags:
                    try:
                        self.audio.add_tags()
                    except Exception:
                        pass
                self._add_mp3_cover(image_data)
            elif self.ext == ".flac":
                self._add_flac_cover(image_data)
            else:
                return False

            self.audio.save()
            return True

        except Exception as e:
            print(f"Error setting album art for {self.file_path}: {str(e)}")
            return False

    def _add_mp3_cover(self, image_data: bytes):
        """Add cover art to MP3"""
        self.audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime="image/jpeg",
                type=3,  # Cover (front)
                desc="Cover",
                data=image_data,
            )
        )

    def _add_flac_cover(self, image_data: bytes):
        """Add cover art to FLAC"""
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.mime = "image/jpeg"
        picture.desc = "Cover"
        picture.data = image_data
        self.audio.add_picture(picture)

    def get_album_art(self) -> Optional[bytes]:
        """Get album art from the audio file"""
        if not self.is_valid():
            return None

        try:
            if self.ext == ".mp3":
                return self._extract_mp3_cover()
            elif self.ext == ".flac":
                return self._extract_flac_cover()
            return None
        except Exception as e:
            print(f"Error getting album art for {self.file_path}: {str(e)}")
            return None

    def _extract_mp3_cover(self) -> Optional[bytes]:
        """Extract cover from MP3"""
        if not self.audio.tags:
            return None
        for tag in self.audio.tags.values():
            if tag.FrameID == "APIC":
                return tag.data
        return None

    def _extract_flac_cover(self) -> Optional[bytes]:
        """Extract cover from FLAC"""
        if self.audio.pictures:
            return self.audio.pictures[0].data
        return None


# Helper functions that use the class


def get_audio_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata from an audio file

    Args:
        file_path (str): Path to the audio file

    Returns:
        dict: Dictionary of metadata
    """
    handler = AudioMetadataHandler(file_path)
    return handler.get_metadata()


def set_audio_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
    """
    Set metadata for an audio file

    Args:
        file_path (str): Path to the audio file
        metadata (dict): Dictionary of metadata

    Returns:
        bool: True if successful
    """
    handler = AudioMetadataHandler(file_path)
    return handler.set_metadata(metadata)


def set_album_art(
    file_path: str, image_url: Optional[str] = None, image_data: Optional[bytes] = None
) -> bool:
    """
    Set album art for an audio file

    Args:
        file_path (str): Path to the audio file
        image_url (str): URL of the image to download
        image_data (bytes): Raw image data

    Returns:
        bool: True if successful
    """
    handler = AudioMetadataHandler(file_path)
    return handler.set_album_art(image_url, image_data)


def get_album_art(file_path: str) -> Optional[bytes]:
    """
    Get album art from an audio file

    Args:
        file_path (str): Path to the audio file

    Returns:
        bytes: Raw image data or None if not found
    """
    handler = AudioMetadataHandler(file_path)
    return handler.get_album_art()


def get_audio_fingerprint(file_path: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Get acoustic fingerprint for an audio file

    Args:
        file_path (str): Path to the audio file

    Returns:
        tuple: (duration, fingerprint) or (None, None) if failed
    """
    try:
        duration, fingerprint = acoustid.fingerprint_file(file_path)
        return duration, fingerprint
    except Exception as e:
        print(f"Error getting fingerprint for {file_path}: {str(e)}")
        return None, None


def is_audio_file(file_path: str) -> bool:
    """
    Check if a file is a supported audio file

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if file is a supported audio file
    """
    supported_extensions = {
        ".mp3",
        ".flac",
        ".wav",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
        ".aiff",
    }
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in supported_extensions:
        return False

    try:
        audio = mutagen.File(file_path)
        return audio is not None
    except Exception:
        return False
