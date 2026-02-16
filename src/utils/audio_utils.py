"""
Auralis - Audio Utilities Module
"""

import os

import acoustid
import mutagen
import requests  # type: ignore
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3


def _extract_mp3_metadata(audio):
    """Extract metadata from MP3 file"""
    metadata = {}
    if "TPE1" in audio:  # Artist
        metadata["artist"] = str(audio["TPE1"])
    if "TIT2" in audio:  # Title
        metadata["title"] = str(audio["TIT2"])
    if "TALB" in audio:  # Album
        metadata["album"] = str(audio["TALB"])
    if "TDRC" in audio:  # Year
        metadata["year"] = str(audio["TDRC"])
    if "TCON" in audio:  # Genre
        metadata["genre"] = str(audio["TCON"])
    if "TRCK" in audio:  # Track number
        metadata["track"] = str(audio["TRCK"])

    if audio.info:
        metadata["bitrate"] = audio.info.bitrate
        metadata["length"] = audio.info.length
        metadata["sample_rate"] = audio.info.sample_rate
    return metadata


def _extract_flac_metadata(audio):
    """Extract metadata from FLAC file"""
    metadata = {}
    if "artist" in audio:
        metadata["artist"] = str(audio["artist"][0])
    if "title" in audio:
        metadata["title"] = str(audio["title"][0])
    if "album" in audio:
        metadata["album"] = str(audio["album"][0])
    if "date" in audio:
        metadata["year"] = str(audio["date"][0])
    if "genre" in audio:
        metadata["genre"] = str(audio["genre"][0])
    if "tracknumber" in audio:
        metadata["track"] = str(audio["tracknumber"][0])

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
    if "artist" in metadata:
        audio["TPE1"] = mutagen.id3.TPE1(encoding=3, text=metadata["artist"])
    if "title" in metadata:
        audio["TIT2"] = mutagen.id3.TIT2(encoding=3, text=metadata["title"])
    if "album" in metadata:
        audio["TALB"] = mutagen.id3.TALB(encoding=3, text=metadata["album"])
    if "year" in metadata:
        audio["TDRC"] = mutagen.id3.TDRC(encoding=3, text=metadata["year"])
    if "genre" in metadata:
        audio["TCON"] = mutagen.id3.TCON(encoding=3, text=metadata["genre"])
    if "track" in metadata:
        audio["TRCK"] = mutagen.id3.TRCK(encoding=3, text=metadata["track"])


def _apply_flac_metadata(audio, metadata):
    """Apply metadata to FLAC file"""
    if "artist" in metadata:
        audio["artist"] = metadata["artist"]
    if "title" in metadata:
        audio["title"] = metadata["title"]
    if "album" in metadata:
        audio["album"] = metadata["album"]
    if "year" in metadata:
        audio["date"] = metadata["year"]
    if "genre" in metadata:
        audio["genre"] = metadata["genre"]
    if "track" in metadata:
        audio["tracknumber"] = metadata["track"]


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

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".mp3":
            audio = ID3(file_path)
            _add_mp3_cover(audio, image_data)
            audio.save()
        elif ext == ".flac":
            audio = FLAC(file_path)
            _add_flac_cover(audio, image_data)
            audio.save()
        else:
            return False

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
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".mp3":
            audio = ID3(file_path)
            return _extract_mp3_cover(audio)
        elif ext == ".flac":
            audio = FLAC(file_path)
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
