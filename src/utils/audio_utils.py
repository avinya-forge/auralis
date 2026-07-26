"""
Auralis - Audio Utilities Module
"""

import os
from typing import Any, Dict, Optional, Tuple

import acoustid
import mutagen
import requests  # type: ignore
from mutagen.flac import FLAC, Picture

try:
    from pydub import AudioSegment

    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
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

    def _load_audio(self) -> None:
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
        if self.audio is None:
            return {}

        if isinstance(self.audio, MP3):
            return self._extract_mp3_metadata()
        elif isinstance(self.audio, FLAC):
            return self._extract_flac_metadata()
        else:
            return self._extract_generic_metadata()

    def set_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Set metadata for the audio file"""
        if self.audio is None:
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
        if self.audio is None:
            return {}
        metadata: Dict[str, Any] = {}
        for key, tag in MP3_TAG_MAP.items():
            if tag in self.audio:
                metadata[key] = str(self.audio[tag])

        self._add_audio_info(metadata)
        return metadata

    def _extract_flac_metadata(self) -> Dict[str, Any]:
        """Extract metadata from FLAC file"""
        if self.audio is None:
            return {}
        metadata: Dict[str, Any] = {}
        for key, tag in FLAC_TAG_MAP.items():
            if tag in self.audio:
                metadata[key] = str(self.audio[tag][0])

        self._add_audio_info(metadata)
        return metadata

    def _extract_generic_metadata(self) -> Dict[str, Any]:
        """Extract metadata from generic audio file"""
        if self.audio is None:
            return {}
        metadata: Dict[str, Any] = {}
        for key in ["artist", "title", "album", "date", "genre", "tracknumber"]:
            if key in self.audio:
                metadata[key] = str(self.audio[key][0])

        self._add_audio_info(metadata)
        return metadata

    def _add_audio_info(self, metadata: Dict[str, Any]) -> None:
        """Add audio info (bitrate, length, etc.) to metadata dict"""
        if self.audio is None:
            return
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

    def _apply_mp3_metadata(self, metadata: Dict[str, Any]) -> None:
        """Apply metadata to MP3 file"""
        if self.audio is None:
            return
        for key, tag_class in MP3_TAG_CLASSES.items():
            if key in metadata:
                tag_name = MP3_TAG_MAP[key]
                self.audio[tag_name] = tag_class(encoding=3, text=metadata[key])

    def _apply_flac_metadata(self, metadata: Dict[str, Any]) -> None:
        """Apply metadata to FLAC file"""
        if self.audio is None:
            return
        for key, tag in FLAC_TAG_MAP.items():
            if key in metadata:
                self.audio[tag] = metadata[key]

    def _apply_generic_metadata(self, metadata: Dict[str, Any]) -> None:
        """Apply metadata to generic audio file"""
        if self.audio is None:
            return
        for key, value in metadata.items():
            if key in ["artist", "title", "album", "year", "genre", "track"]:
                self.audio[key] = value

    def set_album_art(
        self, image_url: Optional[str] = None, image_data: Optional[bytes] = None
    ) -> bool:
        """Set album art for the audio file"""
        if self.audio is None:
            return False

        try:
            if not image_data and image_url:
                image_data = self._download_image(image_url)

            if not image_data:
                return False

            return self._set_cover_data(image_data)

        except Exception as e:
            print(f"Error setting album art for {self.file_path}: {str(e)}")
            return False

    def _download_image(self, image_url: str) -> Optional[bytes]:
        response = requests.get(image_url)
        if response.status_code != 200:
            return None
        return bytes(response.content)

    def _set_cover_data(self, image_data: bytes) -> bool:
        if self.audio is None:
            return False

        if self.ext == ".mp3":
            # Ensure we have ID3 tags
            if not getattr(self.audio, "tags", None):
                try:
                    if hasattr(self.audio, "add_tags"):
                        self.audio.add_tags()
                except Exception as e:
                    _ = e
                    pass
            self._add_mp3_cover(image_data)
        elif self.ext == ".flac":
            self._add_flac_cover(image_data)
        else:
            return False

        self.audio.save()
        return True

    def _add_mp3_cover(self, image_data: bytes) -> None:
        """Add cover art to MP3"""
        if self.audio is None or not hasattr(self.audio, "tags"):
            return
        self.audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime="image/jpeg",
                type=3,  # Cover (front)
                desc="Cover",
                data=image_data,
            )
        )

    def _add_flac_cover(self, image_data: bytes) -> None:
        """Add cover art to FLAC"""
        if self.audio is None:
            return
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.mime = "image/jpeg"
        picture.desc = "Cover"
        picture.data = image_data
        self.audio.add_picture(picture)

    def get_album_art(self) -> Optional[bytes]:
        """Get album art from the audio file"""
        if self.audio is None:
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
        if self.audio is None or not self.audio.tags:
            return None
        for tag in self.audio.tags.values():
            if tag.FrameID == "APIC":
                return tag.data
        return None

    def _extract_flac_cover(self) -> Optional[bytes]:
        """Extract cover from FLAC"""
        if self.audio is None:
            return None
        if hasattr(self.audio, "pictures") and self.audio.pictures:
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
    except Exception as e:
        _ = e
        return False


class AudioUtils:
    """Utility class for audio processing."""

    @staticmethod
    def detect_leading_silence(
        sound: "AudioSegment", silence_threshold: float = -50.0, chunk_size: int = 10
    ) -> int:
        """
        Detect silence at the beginning of an audio segment.

        Args:
            sound (AudioSegment): The audio segment.
            silence_threshold (float): Silence threshold in dBFS.
            chunk_size (int): Resolution in ms.

        Returns:
            int: Duration of silence in ms.
        """
        trim_ms = 0  # ms

        assert chunk_size > 0  # to avoid infinite loop

        while (
            trim_ms < len(sound) and sound[trim_ms : trim_ms + chunk_size].dBFS < silence_threshold
        ):
            trim_ms += chunk_size

        return trim_ms

    @staticmethod
    def trim_silence(
        file_path: str,
        threshold: float = -50.0,
        chunk_size: int = 10,
        padding: int = 100,
    ) -> bool:
        """
        Trim silence from the beginning and end of an audio file.

        Args:
            file_path (str): Path to the audio file.
            threshold (float): Silence threshold in dBFS.
            chunk_size (int): Resolution in ms.
            padding (int): Padding in ms to keep at start/end.

        Returns:
            bool: True if successful (file modified), False otherwise.
        """
        if not HAS_PYDUB:
            return False

        try:
            # Load audio
            # pydub auto-detects format, but for export we might need explicit format
            audio = AudioSegment.from_file(file_path)

            # Detect silence
            start_trim = AudioUtils.detect_leading_silence(
                audio, silence_threshold=threshold, chunk_size=chunk_size
            )
            end_trim = AudioUtils.detect_leading_silence(
                audio.reverse(), silence_threshold=threshold, chunk_size=chunk_size
            )

            duration = len(audio)

            # Check if trimming is needed
            # (start_trim + end_trim) < duration ensures we don't trim everything if silence detection is aggressive
            if (start_trim > padding or end_trim > padding) and (start_trim + end_trim < duration):
                # Adjust trim with padding
                start_trim = max(0, start_trim - padding)
                end_trim = max(0, end_trim - padding)

                trimmed_audio = audio[start_trim : duration - end_trim]

                # Export
                # Determine format from extension
                ext = os.path.splitext(file_path)[1].lower()
                fmt = ext.lstrip(".")
                if fmt == "m4a":
                    fmt = "ipod"  # ffmpeg format for m4a

                trimmed_audio.export(file_path, format=fmt)
                return True

            return False

        except Exception as e:
            _ = e
            return False
