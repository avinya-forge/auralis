"""
Auralis - Audio Similarity Service

This module provides functionality to detect duplicate audio files based on
audio content similarity rather than just metadata or filenames.
"""

import logging
import os
from typing import Dict, List, Optional, Set, cast

import numpy as np  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

# Set up logging
logger = logging.getLogger("auralis.similarity")

# Try to import optional dependencies
try:
    import librosa
    import mutagen
    import pydub
    from sklearn.metrics.pairwise import cosine_similarity  # noqa: F811

    HAS_AUDIO_FINGERPRINTING = True
except ImportError:
    HAS_AUDIO_FINGERPRINTING = False


class AudioSimilarityService:
    """Service for detecting similar audio content across files"""

    def __init__(self):
        """Initialize the audio similarity service"""
        self.available = HAS_AUDIO_FINGERPRINTING
        if not self.available:
            logger.warning(
                "Audio similarity detection dependencies not installed. "
                "Please install: librosa, soundfile, scikit-learn, mutagen, pydub"
            )
        # Cache for fingerprints to avoid recomputing
        self.fingerprint_cache = {}

        # Threshold for similarity (0.0 to 1.0)
        self.similarity_threshold = 0.85

    def compute_fingerprint(self, file_path: str) -> Optional["np.ndarray"]:
        """
        Compute audio fingerprint for a file

        Args:
            file_path (str): Path to the audio file

        Returns:
            np.ndarray or None: Audio fingerprint or None if computation fails
        """
        if not self.available:
            return None

        try:
            # Check cache first
            if file_path in self.fingerprint_cache:
                return cast("np.ndarray", self.fingerprint_cache[file_path])

            # Load audio file
            y, sr = librosa.load(file_path, sr=22050, mono=True, duration=60)

            # Compute mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)

            # Convert to log scale
            log_mel_spec = librosa.power_to_db(mel_spec)

            # Compute mean of each mel band to get a compact fingerprint
            fingerprint = np.mean(log_mel_spec, axis=1)

            # Normalize fingerprint
            std_dev = np.std(fingerprint)
            if std_dev > 0:
                fingerprint = (fingerprint - np.mean(fingerprint)) / std_dev
            else:
                fingerprint = fingerprint - np.mean(fingerprint)

            # Cache the fingerprint
            self.fingerprint_cache[file_path] = fingerprint

            return cast("np.ndarray", fingerprint)

        except Exception as e:
            logger.error(f"Error computing fingerprint for {file_path}: {str(e)}")
            return None

    def compute_similarity(self, fingerprint1: "np.ndarray", fingerprint2: "np.ndarray") -> float:
        """
        Compute similarity between two audio fingerprints

        Args:
            fingerprint1 (np.ndarray): First fingerprint
            fingerprint2 (np.ndarray): Second fingerprint

        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        if not self.available:
            return 0.0

        try:
            # Reshape fingerprints for cosine similarity
            fp1 = fingerprint1.reshape(1, -1)
            fp2 = fingerprint2.reshape(1, -1)

            # Compute cosine similarity
            similarity = cosine_similarity(fp1, fp2)[0][0]

            return float(similarity)

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0

    def _get_duration(self, file_info: Dict) -> float:
        """
        Get duration from metadata or compute it using pydub

        Args:
            file_info (dict): File information dictionary

        Returns:
            float: Duration in seconds, or 0 if determination failed
        """
        duration = file_info.get("metadata", {}).get("duration", 0)
        if duration:
            return float(duration)

        try:
            if "pydub" in globals():
                audio = pydub.AudioSegment.from_file(file_info["path"])
                return float(len(audio) / 1000)  # convert to seconds
        except Exception:
            pass

        return 0.0

    def _group_files_by_duration(self, music_files: List[Dict]) -> Dict[float, List[Dict]]:
        """
        Group files by approximate duration to reduce comparisons

        Args:
            music_files (list): List of file info dictionaries

        Returns:
            dict: Dictionary mapping rounded duration to list of files
        """
        duration_groups: Dict[float, List[Dict]] = {}
        for file_info in music_files:
            duration = self._get_duration(file_info)
            if not duration:
                continue

            # Round duration to nearest 5 seconds to group similar-length
            rounded_duration = round(duration / 5) * 5
            if rounded_duration not in duration_groups:
                duration_groups[rounded_duration] = []
            duration_groups[rounded_duration].append(file_info)

        return duration_groups

    def _find_duplicates_in_group(
        self, files: List[Dict], processed_files: Set[str]
    ) -> List[List[Dict]]:
        """
        Find duplicates within a group of files with similar duration

        Args:
            files (list): List of files in the group
            processed_files (set): Set of paths of already processed files

        Returns:
            list: List of duplicate groups found in this duration group
        """
        duplicates = []

        for i, file1 in enumerate(files):
            if file1["path"] in processed_files:
                continue

            fingerprint1 = self.compute_fingerprint(file1["path"])
            if fingerprint1 is None:
                continue

            current_duplicates = [file1]

            for j in range(i + 1, len(files)):
                file2 = files[j]
                if file2["path"] in processed_files:
                    continue

                fingerprint2 = self.compute_fingerprint(file2["path"])
                if fingerprint2 is None:
                    continue

                similarity = self.compute_similarity(fingerprint1, fingerprint2)

                if similarity >= self.similarity_threshold:
                    current_duplicates.append(file2)

            if len(current_duplicates) > 1:
                # Sort duplicates by quality (prefer higher bitrate)
                sorted_duplicates = self._sort_by_quality(current_duplicates)
                duplicates.append(sorted_duplicates)

                # Mark all duplicates as processed to avoid re-checking
                for dup in sorted_duplicates:
                    processed_files.add(dup["path"])

        return duplicates

    def find_duplicates(self, music_files: List[Dict]) -> List[List[Dict]]:
        """
        Find duplicate audio files based on content similarity

        Args:
            music_files (list): List of file info dictionaries

        Returns:
            list: List of groups of duplicate files
        """
        if not self.available or not music_files:
            return []

        duplicates = []
        processed_files: Set[str] = set()

        try:
            logger.info(f"Computing fingerprints for {len(music_files)} files")
            # Group files by approximate duration first to reduce comparisons
            duration_groups: Dict[float, List[Dict]] = {}
            for file_info in music_files:
                # Get duration from metadata or compute it
                duration = file_info.get("metadata", {}).get("duration", 0)
                if not duration:
                    try:
                        audio = mutagen.File(file_info["path"])
                        if audio and audio.info:
                            duration = audio.info.length
                        else:
                            # If we can't get duration, try pydub (fallback) or skip
                            try:
                                if "pydub" in globals():
                                    audio_segment = pydub.AudioSegment.from_file(file_info["path"])
                                    duration = len(audio_segment) / 1000
                            except Exception:
                                pass

                            if not duration:
                                continue
                    except Exception as e:
                        logger.error(f"Error getting duration for {file_info['path']}: {str(e)}")
                        # If we can't get duration, skip this file
                        continue

                # Round duration to nearest 5 seconds to group similar-length files
                rounded_duration = round(duration / 5) * 5
                if rounded_duration not in duration_groups:
                    duration_groups[rounded_duration] = []
                duration_groups[rounded_duration].append(file_info)
            # Process each duration group
            for duration, files in duration_groups.items():
                if len(files) < 2:
                    continue  # Skip groups with only one file

                group_duplicates = self._find_duplicates_in_group(files, processed_files)
                duplicates.extend(group_duplicates)

            return duplicates

        except Exception as e:
            logger.error(f"Error finding duplicates: {str(e)}")
            return []

    def _sort_by_quality(self, files: List[Dict]) -> List[Dict]:
        """
        Sort files by quality (best first)

        Args:
            files (list): List of file info dictionaries

        Returns:
            list: Sorted list with best quality first
        """

        def quality_score(file_info):
            # Higher score = better quality
            score = 0

            # Format preference
            extension = os.path.splitext(file_info["path"])[1].lower()
            format_scores = {
                ".flac": 50,
                ".wav": 45,
                ".aiff": 40,
                ".m4a": 30,
                ".ogg": 25,
                ".mp3": 20,
                ".aac": 15,
                ".wma": 10,
            }
            score += format_scores.get(extension, 0)

            # Bitrate (higher is better)
            bitrate = file_info.get("metadata", {}).get("bitrate", 0)
            if bitrate:
                score += min(bitrate / 32000, 30)  # max 30 points for bitrate

            # File size (larger is generally better for same duration)
            size_mb = file_info.get("size", 0) / (1024 * 1024)
            score += min(size_mb, 10)  # max 10 points for size

            # Duration (longer version is generally preferred)
            duration = file_info.get("metadata", {}).get("duration", 0)
            score += min(duration / 60, 5)  # max 5 points for duration

            # Complete metadata is a good sign
            metadata = file_info.get("metadata", {})
            if metadata.get("artist") and metadata.get("title") and metadata.get("album"):
                score += 5

            return score

        return sorted(files, key=quality_score, reverse=True)

    def get_best_quality_version(self, duplicate_group: List[Dict]) -> Optional[Dict]:
        """
        Get the best quality version from a group of duplicates

        Args:
            duplicate_group (list): List of duplicate file info dictionaries

        Returns:
            dict: Best quality file info
        """
        if not duplicate_group:
            return None

        sorted_files = self._sort_by_quality(duplicate_group)
        return sorted_files[0]


# Singleton instance
audio_similarity_service = AudioSimilarityService()


def find_duplicates(music_files: List[Dict]) -> List[List[Dict]]:
    """Find duplicate audio files based on content similarity"""
    return audio_similarity_service.find_duplicates(music_files)


def get_best_quality_version(duplicate_group: List[Dict]) -> Optional[Dict]:
    """Get the best quality version from a group of duplicates"""
    return audio_similarity_service.get_best_quality_version(duplicate_group)


def is_available() -> bool:
    """Check if audio similarity detection is available"""
    return bool(audio_similarity_service.available)
