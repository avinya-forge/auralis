"""
Auralis - Playlist Service

This module provides functionality to generate smart playlists based on
audio analysis data (BPM, Key, Mood).
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("auralis.playlist")


class PlaylistGenerator:
    """Generates playlists based on various criteria."""

    def __init__(self) -> None:
        """Initialize the PlaylistGenerator."""
        pass

    def generate_upbeat_playlist(
        self, files: List[Dict[str, Any]], min_bpm: float = 120.0
    ) -> List[Dict[str, Any]]:
        """
        Generate a playlist of upbeat tracks (high BPM).

        Args:
            files (List[Dict[str, Any]]): List of file info dictionaries.
            min_bpm (float): Minimum BPM to include.

        Returns:
            List[Dict[str, Any]]: Filtered list of files.
        """
        playlist = []
        for file_info in files:
            bpm = self._get_bpm(file_info)
            if bpm and bpm >= min_bpm:
                playlist.append(file_info)
        return playlist

    def generate_chill_playlist(
        self, files: List[Dict[str, Any]], max_bpm: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Generate a playlist of chill tracks (low BPM).

        Args:
            files (List[Dict[str, Any]]): List of file info dictionaries.
            max_bpm (float): Maximum BPM to include.

        Returns:
            List[Dict[str, Any]]: Filtered list of files.
        """
        playlist = []
        for file_info in files:
            bpm = self._get_bpm(file_info)
            if bpm and bpm <= max_bpm:
                playlist.append(file_info)
        return playlist

    def generate_playlist_by_mood(
        self, files: List[Dict[str, Any]], target_mood: str
    ) -> List[Dict[str, Any]]:
        """
        Generate a playlist of tracks matching a specific mood.

        Args:
            files (List[Dict[str, Any]]): List of file info dictionaries.
            target_mood (str): Mood to filter by (e.g., 'Energetic', 'Calm').

        Returns:
            List[Dict[str, Any]]: Filtered list of files.
        """
        playlist = []
        for file_info in files:
            mood = self._get_mood(file_info)
            if mood and mood.lower() == target_mood.lower():
                playlist.append(file_info)
        return playlist

    def _get_bpm(self, file_info: Dict[str, Any]) -> Optional[float]:
        """
        Get BPM from file metadata.

        Args:
            file_info (Dict[str, Any]): File info dictionary.

        Returns:
            Optional[float]: BPM value or None.
        """
        metadata = file_info.get("metadata", {})
        # Check 'bpm' or 'TBPM'
        bpm = metadata.get("bpm")
        if bpm:
            try:
                return float(bpm)
            except (ValueError, TypeError):
                pass
        return None

    def _get_mood(self, file_info: Dict[str, Any]) -> Optional[str]:
        """
        Get Mood from file metadata.

        Args:
            file_info (Dict[str, Any]): File info dictionary.

        Returns:
            Optional[str]: Mood value or None.
        """
        metadata = file_info.get("metadata", {})
        return metadata.get("mood")
