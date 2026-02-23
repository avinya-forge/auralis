"""
Auralis - Playlist Service

This module provides functionality to generate smart playlists based on
audio analysis data (BPM, Key, Mood).
"""

import logging
import random
from typing import Any, Dict, List, Optional, Set, cast

logger = logging.getLogger("auralis.playlist")


class PlaylistGenerator:
    """Generates playlists based on various criteria."""

    # Key compatibility map (Simplified Circle of Fifths + Relative Major/Minor)
    KEY_COMPATIBILITY: Dict[str, List[str]] = {
        # Major Keys
        "C Major": ["C Major", "A Minor", "F Major", "G Major"],
        "G Major": ["G Major", "E Minor", "C Major", "D Major"],
        "D Major": ["D Major", "B Minor", "G Major", "A Major"],
        "A Major": ["A Major", "F# Minor", "D Major", "E Major"],
        "E Major": ["E Major", "C# Minor", "A Major", "B Major"],
        "B Major": ["B Major", "G# Minor", "E Major", "F# Major"],
        "F# Major": ["F# Major", "D# Minor", "B Major", "C# Major"],
        "C# Major": ["C# Major", "A# Minor", "F# Major", "G# Major"],
        "F Major": ["F Major", "D Minor", "Bb Major", "C Major"],
        "Bb Major": ["Bb Major", "G Minor", "Eb Major", "F Major"],
        "Eb Major": ["Eb Major", "C Minor", "Ab Major", "Bb Major"],
        "Ab Major": ["Ab Major", "F Minor", "Db Major", "Eb Major"],
        "Db Major": ["Db Major", "Bb Minor", "Gb Major", "Ab Major"],
        "Gb Major": ["Gb Major", "Eb Minor", "Cb Major", "Db Major"],  # Enharmonic to F#
        "Cb Major": ["Cb Major", "Ab Minor", "Gb Major", "Db Major"],  # Enharmonic to B
        # Minor Keys
        "A Minor": ["A Minor", "C Major", "D Minor", "E Minor"],
        "E Minor": ["E Minor", "G Major", "A Minor", "B Minor"],
        "B Minor": ["B Minor", "D Major", "E Minor", "F# Minor"],
        "F# Minor": ["F# Minor", "A Major", "B Minor", "C# Minor"],
        "C# Minor": ["C# Minor", "E Major", "F# Minor", "G# Minor"],
        "G# Minor": ["G# Minor", "B Major", "C# Minor", "D# Minor"],
        "D# Minor": ["D# Minor", "F# Major", "G# Minor", "A# Minor"],
        "A# Minor": ["A# Minor", "C# Major", "D# Minor", "F Minor"],
        "D Minor": ["D Minor", "F Major", "G Minor", "A Minor"],
        "G Minor": ["G Minor", "Bb Major", "C Minor", "D Minor"],
        "C Minor": ["C Minor", "Eb Major", "F Minor", "G Minor"],
        "F Minor": ["F Minor", "Ab Major", "Bb Minor", "C Minor"],
        "Bb Minor": ["Bb Minor", "Db Major", "Eb Minor", "F Minor"],
        "Eb Minor": ["Eb Minor", "Gb Major", "Ab Minor", "Bb Minor"],
        "Ab Minor": ["Ab Minor", "Cb Major", "Db Minor", "Eb Minor"],
    }

    def __init__(self) -> None:
        """Initialize the PlaylistGenerator."""
        pass

    def generate_flow_mode_playlist(
        self,
        files: List[Dict[str, Any]],
        start_track: Optional[Dict[str, Any]] = None,
        length_minutes: int = 60,
        tolerance_bpm: float = 0.05,
    ) -> List[Dict[str, Any]]:
        """
        Generate a 'Flow Mode' playlist using harmonic mixing (BPM + Key).

        Args:
            files (List[Dict[str, Any]]): Available files.
            start_track (Optional[Dict[str, Any]]): Starting track (optional).
            length_minutes (int): Target length in minutes.
            tolerance_bpm (float): BPM tolerance (percentage).

        Returns:
            List[Dict[str, Any]]: Generated playlist.
        """
        # Filter files with valid BPM and Key
        valid_files = [
            f for f in files if self._get_bpm(f) is not None and self._get_key(f) is not None
        ]

        if not valid_files:
            return []

        playlist = []
        current_track = start_track if start_track in valid_files else random.choice(valid_files)
        playlist.append(current_track)

        # Keep track of used files to avoid duplicates
        used_paths = {current_track["path"]}

        current_duration = self._get_duration(current_track)
        target_duration = length_minutes * 60

        while current_duration < target_duration:
            next_track = self._find_next_track(
                current_track, valid_files, used_paths, tolerance_bpm
            )

            if next_track:
                playlist.append(next_track)
                used_paths.add(next_track["path"])
                current_duration += self._get_duration(next_track)
                current_track = next_track
            else:
                break

        return playlist

    def _find_next_track(
        self,
        current_track: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        used_paths: Set[str],
        tolerance_bpm: float,
    ) -> Optional[Dict[str, Any]]:
        """Find the best next track based on BPM and Key."""
        current_bpm = self._get_bpm(current_track)
        current_key = self._get_key(current_track)

        if current_bpm is None or current_key is None:
            return None

        compatible_keys = self.KEY_COMPATIBILITY.get(current_key, [])

        # First try: Compatible Key AND BPM within tolerance
        next_track = self._get_random_compatible_track(
            candidates, used_paths, current_bpm, compatible_keys, tolerance_bpm
        )
        if next_track:
            return next_track

        # Fallback: Relax BPM tolerance slightly (2x)
        return self._get_random_compatible_track(
            candidates, used_paths, current_bpm, compatible_keys, tolerance_bpm * 2
        )

    def _get_random_compatible_track(
        self,
        candidates: List[Dict[str, Any]],
        used_paths: Set[str],
        target_bpm: float,
        compatible_keys: List[str],
        tolerance: float,
    ) -> Optional[Dict[str, Any]]:
        """Helper to find a random track matching criteria."""
        matches = []
        for track in candidates:
            if track["path"] in used_paths:
                continue

            bpm = self._get_bpm(track)
            key = self._get_key(track)

            if bpm is None or key is None:
                continue

            bpm_diff = abs(bpm - target_bpm) / target_bpm

            if bpm_diff <= tolerance and key in compatible_keys:
                matches.append(track)

        if matches:
            return random.choice(matches)
        return None

    def export_playlist(self, playlist: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Export playlist to .m3u8 file.

        Args:
            playlist (List[Dict[str, Any]]): List of file info dicts.
            filepath (str): Output file path.

        Returns:
            bool: True if successful.
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for track in playlist:
                    duration = int(self._get_duration(track))
                    artist = track.get("metadata", {}).get("artist", "Unknown Artist")
                    title = track.get("metadata", {}).get("title", "Unknown Title")
                    path = track["path"]

                    f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                    f.write(f"{path}\n")
            return True
        except Exception as e:
            logger.error(f"Error exporting playlist: {e}")
            return False

    def import_playlist(self, filepath: str) -> List[str]:
        """
        Import playlist from .m3u/.m3u8 file.

        Args:
            filepath (str): Path to playlist file.

        Returns:
            List[str]: List of file paths.
        """
        paths = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        paths.append(line)
        except Exception as e:
            logger.error(f"Error importing playlist: {e}")
        return paths

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
        mood = metadata.get("mood")
        if mood and isinstance(mood, str):
            return cast(str, mood)
        return None

    def _get_key(self, file_info: Dict[str, Any]) -> Optional[str]:
        """
        Get Key from file metadata.

        Args:
            file_info (Dict[str, Any]): File info dictionary.

        Returns:
            Optional[str]: Key value or None.
        """
        metadata = file_info.get("metadata", {})
        key = metadata.get("key")
        if key and isinstance(key, str):
            return cast(str, key)
        return None

    def _get_duration(self, file_info: Dict[str, Any]) -> float:
        """
        Get duration from file info (placeholder if not available).

        Args:
            file_info (Dict[str, Any]): File info dictionary.

        Returns:
            float: Duration in seconds.
        """
        if "duration" in file_info:
            return float(file_info["duration"])

        metadata = file_info.get("metadata", {})
        if "duration" in metadata:
            return float(metadata["duration"])

        return 180.0  # Default 3 minutes
