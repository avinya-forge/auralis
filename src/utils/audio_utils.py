"""
Auralis - Audio Utilities Module
"""

import os

import acoustid
import mutagen
import requests  # type: ignore
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TCON, TDRC, TIT2, TPE1, TRCK

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


def _extract_mp3_metadata(audio):
    """Extract metadata from MP3 file"""
    metadata = {}
    for key, tag in MP3_TAG_MAP.items():
        if tag in audio:
            metadata[key] = str(audio[tag])

    if audio.info:
        metadata["bitrate"] = audio.info.bitrate
        metadata["length"] = audio.info.length
        metadata["sample_rate"] = audio.info.sample_rate
    return metadata


def _extract_flac_metadata(audio):
    """Extract metadata from FLAC file"""
    metadata = {}
    for key, tag in FLAC_TAG_MAP.items():
        if tag in audio:
            metadata[key] = str(audio[tag][0])

    if audio.info:
        metadata["bitrate"] = audio.info.bits_per_sample * audio.info.sample_rate
        metadata["length"] = audio.info.length
        metadata["sample_rate"] = audio.info.sample_rate
    return metadata


def _extract_generic_metadata(audio):
    """Extract metadata from generic audio file"""
    metadata = {}
    for key in ["artist", "title", "album", "date", "genre", "tracknumber"]:
        if key in audio:
            metadata[key] = str(audio[key][0])

    if hasattr(audio, "info"):
        if hasattr(audio.info, "bitrate"):
            metadata["bitrate"] = audio.info.bitrate
        if hasattr(audio.info, "length"):
            metadata["length"] = audio.info.length
        if hasattr(audio.info, "sample_rate"):
            metadata["sample_rate"] = audio.info.sample_rate
    return metadata


def get_audio_metadata(file_path):
    """
    Get metadata from an audio file

    Args:
        file_path (str): Path to the audio file

    Returns:
        dict: Dictionary of metadata
    """
    try:
        audio = mutagen.File(file_path)

        if not audio:
            return {}

        if isinstance(audio, mutagen.mp3.MP3):
            return _extract_mp3_metadata(audio)
        elif isinstance(audio, mutagen.flac.FLAC):
            return _extract_flac_metadata(audio)
        else:
            return _extract_generic_metadata(audio)

    except Exception as e:
        print(f"Error getting metadata for {file_path}: {str(e)}")
        return {}


def _apply_mp3_metadata(audio, metadata):
    """Apply metadata to MP3 file"""
    for key, tag_class in MP3_TAG_CLASSES.items():
        if key in metadata:
            tag_name = MP3_TAG_MAP[key]
            audio[tag_name] = tag_class(encoding=3, text=metadata[key])


def _apply_flac_metadata(audio, metadata):
    """Apply metadata to FLAC file"""
    for key, tag in FLAC_TAG_MAP.items():
        if key in metadata:
            audio[tag] = metadata[key]


def _apply_generic_metadata(audio, metadata):
    """Apply metadata to generic audio file"""
    for key, value in metadata.items():
        if key in ["artist", "title", "album", "year", "genre", "track"]:
            audio[key] = value


def set_audio_metadata(file_path, metadata):
    """
    Set metadata for an audio file

    Args:
        file_path (str): Path to the audio file
        metadata (dict): Dictionary of metadata

    Returns:
        bool: True if successful
    """
    try:
        audio = mutagen.File(file_path)

        if not audio:
            return False

        if isinstance(audio, mutagen.mp3.MP3):
            _apply_mp3_metadata(audio, metadata)
        elif isinstance(audio, mutagen.flac.FLAC):
            _apply_flac_metadata(audio, metadata)
        else:
            _apply_generic_metadata(audio, metadata)

        audio.save()
        return True

    except Exception as e:
        print(f"Error setting metadata for {file_path}: {str(e)}")
        return False


def get_audio_fingerprint(file_path):
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


def _add_mp3_cover(audio, image_data):
    """Add cover art to MP3"""
    audio.add(
        APIC(
            encoding=3,  # UTF-8
            mime="image/jpeg",
            type=3,  # Cover (front)
            desc="Cover",
            data=image_data,
        )
    )


def _add_flac_cover(audio, image_data):
    """Add cover art to FLAC"""
    picture = Picture()
    picture.type = 3  # Cover (front)
    picture.mime = "image/jpeg"
    picture.desc = "Cover"
    picture.data = image_data
    audio.add_picture(picture)


def _get_audio_handler(file_path):
    """
    Get the appropriate audio handler based on file extension

    Args:
        file_path (str): Path to the audio file

    Returns:
        tuple: (audio_handler, extension) or (None, extension)
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext == ".mp3":
            return ID3(file_path), ext
        elif ext == ".flac":
            return FLAC(file_path), ext
    except Exception:
        pass
    return None, ext


def set_album_art(file_path, image_url=None, image_data=None):
    """
    Set album art for an audio file

    Args:
        file_path (str): Path to the audio file
        image_url (str): URL of the image to download
        image_data (bytes): Raw image data

    Returns:
        bool: True if successful
    """
    try:
        if not image_data and image_url:
            response = requests.get(image_url)
            if response.status_code != 200:
                return False
            image_data = response.content

        if not image_data:
            return False

        audio, ext = _get_audio_handler(file_path)
        if not audio:
            return False

        if ext == ".mp3":
            _add_mp3_cover(audio, image_data)
        elif ext == ".flac":
            _add_flac_cover(audio, image_data)
        else:
            return False

        audio.save()
        return True

    except Exception as e:
        print(f"Error setting album art for {file_path}: {str(e)}")
        return False


def _extract_mp3_cover(audio):
    """Extract cover from MP3"""
    for tag in audio.values():
        if tag.FrameID == "APIC":
            return tag.data
    return None


def _extract_flac_cover(audio):
    """Extract cover from FLAC"""
    if audio.pictures:
        return audio.pictures[0].data
    return None


def get_album_art(file_path):
    """
    Get album art from an audio file

    Args:
        file_path (str): Path to the audio file

    Returns:
        bytes: Raw image data or None if not found
    """
    try:
        audio, ext = _get_audio_handler(file_path)
        if not audio:
            return None

        if ext == ".mp3":
            return _extract_mp3_cover(audio)
        elif ext == ".flac":
            return _extract_flac_cover(audio)
        return None

    except Exception as e:
        print(f"Error getting album art for {file_path}: {str(e)}")
        return None


def is_audio_file(file_path):
    """
    Check if a file is a supported audio file

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if file is a supported audio file
    """
    supported_extensions = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma", ".aiff"}
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in supported_extensions:
        return False

    try:
        audio = mutagen.File(file_path)
        return audio is not None
    except Exception:
        return False
