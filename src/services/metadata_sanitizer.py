"""
Auralis - Metadata Sanitizer Service

Handles sanitization of metadata tags in music files.
"""

import logging
from typing import Any, Dict, List, Optional

import mutagen
from mutagen.flac import FLAC
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3


class MetadataSanitizer:
    """
    Service for sanitizing metadata in music files.
    """

    def __init__(self) -> None:
        """Initialize the MetadataSanitizer."""
        self.logger = logging.getLogger(__name__)

    def sanitize(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sanitize metadata in a music file based on options.

        Args:
            file_path (str): Path to the music file.
            options (Dict[str, Any]): options for sanitization.
                - remove_comments (bool): Remove comment tags. Default True.
                - remove_id3v1 (bool): Remove ID3v1 tags (MP3 only). Default True.
                - remove_padding (bool): Remove padding (MP3 only). Default False.
                - trim_whitespace (bool): Trim whitespace from text tags. Default True.

        Returns:
            bool: True if changes were saved, False if no changes or error.
        """
        if options is None:
            options = {}

        remove_comments = options.get("remove_comments", True)
        remove_id3v1 = options.get("remove_id3v1", True)
        remove_padding = options.get("remove_padding", False)
        trim_whitespace = options.get("trim_whitespace", True)

        try:
            # Handle MP3 specific actions (ID3v1 removal)
            if file_path.lower().endswith(".mp3") and remove_id3v1:
                try:
                    # ID3(file_path).delete_v1() handles removal of v1 tags
                    # But we need to check if we can open it first
                    audio_id3 = ID3(file_path)
                    audio_id3.delete_v1()
                    # We need to save if we want to persist the deletion of v1?
                    # delete_v1() usually saves immediately if it's a method on ID3(filename).
                    # Checking mutagen docs: delete_v1() deletes ID3v1 tags from the file.
                except ID3NoHeaderError:
                    pass
                except Exception as e:
                    self.logger.warning(f"Error removing ID3v1 from {file_path}: {e}")

            audio = mutagen.File(file_path)
            if not audio:
                return False

            modified = False

            # Remove comments
            if remove_comments:
                if self._remove_comments(audio):
                    modified = True

            # Trim whitespace
            if trim_whitespace:
                if self._trim_whitespace(audio):
                    modified = True

            # Save if modified or if we need to remove padding
            if modified or (remove_padding and file_path.lower().endswith(".mp3")):
                if file_path.lower().endswith(".mp3") and isinstance(audio, MP3):
                    # For MP3, we can control padding via ID3 save options
                    if remove_padding:
                        # Re-save tags with 0 padding
                        # mutagen.id3.ID3.save(v2_version=3, padding=0)
                        if audio.tags:
                            audio.tags.save(file_path, padding=0)
                            return True
                    else:
                        audio.save()
                        return True
                else:
                    audio.save()
                    return True

            return modified

        except Exception as e:
            self.logger.error(f"Error sanitizing {file_path}: {e}")
            return False

    def _remove_comments(self, audio: Any) -> bool:
        """
        Remove comment tags from audio object.

        Args:
            audio: Mutagen audio object.

        Returns:
            bool: True if comments were removed.
        """
        modified = False

        # ID3 (MP3)
        if hasattr(audio, "tags") and isinstance(audio.tags, ID3):
            keys_to_remove = [k for k in audio.tags.keys() if k.startswith("COMM")]
            for k in keys_to_remove:
                del audio.tags[k]
                modified = True

        # FLAC / Vorbis
        elif isinstance(audio, FLAC) or hasattr(audio, "comments"):
            # FLAC uses Vorbis comments. 'DESCRIPTION' or 'COMMENT' are common.
            # Mutagen FLAC maps keys to lists of strings.
            # Check for keys case-insensitively? Vorbis keys are case-insensitive.
            # Mutagen usually normalizes them?

            # Common comment keys
            comment_keys = ["comment", "description", "notes", "remarks"]

            # Get existing keys
            existing_keys = list(audio.keys()) if hasattr(audio, "keys") else []

            for key in existing_keys:
                if key.lower() in comment_keys:
                    del audio[key]
                    modified = True

        return modified

    def _trim_whitespace(self, audio: Any) -> bool:
        """
        Trim whitespace from text tags.

        Args:
            audio: Mutagen audio object.

        Returns:
            bool: True if tags were modified.
        """
        modified = False

        # ID3 (MP3)
        if hasattr(audio, "tags") and isinstance(audio.tags, ID3):
            for key in audio.tags.keys():
                frame = audio.tags[key]
                # Check if it's a text frame (APIC is image, etc.)
                # Text frames usually have a 'text' attribute which is a list of strings
                if hasattr(frame, "text") and isinstance(frame.text, list):
                    new_text = []
                    frame_modified = False
                    for val in frame.text:
                        if isinstance(val, str):
                            stripped = val.strip()
                            if stripped != val:
                                new_text.append(stripped)
                                frame_modified = True
                            else:
                                new_text.append(val)
                        else:
                            new_text.append(val)

                    if frame_modified:
                        frame.text = new_text
                        modified = True

        # FLAC / Vorbis (Dict-like)
        elif isinstance(audio, FLAC) or hasattr(audio, "comments"):
            keys = list(audio.keys()) if hasattr(audio, "keys") else []
            for key in keys:
                # Vorbis comments are lists of strings
                try:
                    values = audio[key]
                except Exception:
                    continue

                if isinstance(values, list):
                    new_values = []
                    key_modified = False
                    for val in values:
                        if isinstance(val, str):
                            stripped = val.strip()
                            if stripped != val:
                                new_values.append(stripped)
                                key_modified = True
                            else:
                                new_values.append(val)
                        else:
                            new_values.append(val)

                    if key_modified:
                        audio[key] = new_values
                        modified = True

        return modified
