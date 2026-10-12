"""
Spectrogram Service

This module provides functionality to generate Mel-spectrograms from audio files
using librosa and compute distinct Song IDs based on these features for deduplication.
It also provides concurrent batch processing capabilities.
"""

import concurrent.futures
import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SpectrogramService:
    """
    Generates Mel-spectrograms and unique Song IDs for audio deduplication.
    """

    def __init__(self) -> None:
        """Initialize the SpectrogramService."""
        self.has_dependencies = self._check_dependencies()
        self.has_acoustid = self._check_acoustid_dependency()

    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        try:
            import librosa  # noqa: F401
            import numpy as np  # noqa: F401

            # torch is optional but recommended
            try:
                import torch  # noqa: F401
            except ImportError:
                pass
            return True
        except ImportError:
            logger.warning("Librosa or numpy not installed. Spectrogram features disabled.")
            return False

    def _check_acoustid_dependency(self) -> bool:
        """Check if acoustid is available for fast chromaprint hash."""
        try:
            import acoustid  # noqa: F401

            return True
        except ImportError:
            logger.warning("acoustid not installed. Fast chromaprint hashing disabled.")
            return False

    def generate_mel_spectrogram(
        self, file_path: str, n_mels: int = 128, duration: int = 30
    ) -> Optional[Any]:
        """
        Generate a Mel-spectrogram from an audio file.

        Args:
            file_path (str): Path to the audio file.
            n_mels (int): Number of Mel bands to generate.
            duration (int): Duration in seconds to analyze (from start).

        Returns:
            Optional[Any]: Numpy array or Torch tensor of the flattened/pooled spectrogram features,
                           or None if generation fails.
        """
        if not self.has_dependencies:
            return None

        try:
            import librosa
            import numpy as np

            # Load audio file. librosa.load resamples to 22050Hz and converts to mono by default.
            # Analyze a fixed duration to ensure consistent feature sizes for comparison.
            y, sr = librosa.load(file_path, duration=duration)

            # Compute Mel-scaled spectrogram
            # S is the power spectrogram
            S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)

            # Convert power to decibels for log-scale scaling
            S_dB = librosa.power_to_db(S, ref=np.max)

            return S_dB
        except Exception as e:
            logger.error(f"Error generating Mel-spectrogram for {file_path}: {e}")
            return None

    def generate_chroma_hash(self, file_path: str) -> Optional[str]:
        """
        Generate a fast chromaprint hash using acoustid.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[str]: The chromaprint hash, or None if it failed.
        """
        if not self.has_acoustid:
            return None

        try:
            import acoustid

            duration, fingerprint = acoustid.fingerprint_file(file_path)
            if fingerprint:
                if isinstance(fingerprint, bytes):
                    return fingerprint.decode("utf-8")
                return str(fingerprint)
            return None
        except Exception as e:
            logger.error(f"Error generating chroma hash for {file_path}: {e}")
            return None

    def generate_song_id(self, file_path: str) -> Optional[str]:
        """
        Generate a unique Song ID based on distinct spectrogram features.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[str]: SHA-256 hash representing the Song ID, or None if failed.
        """
        spectrogram = self.generate_mel_spectrogram(file_path)
        if spectrogram is None:
            return None

        import numpy as np

        # To make the ID robust to minor variations, we can summarize the spectrogram
        # For instance, taking the mean and variance across the time axis.
        # This provides a 2D statistical summary that is relatively stable.
        mean_features = np.mean(spectrogram, axis=1)
        var_features = np.var(spectrogram, axis=1)

        # Concatenate and round the features to reduce sensitivity to tiny floating point differences
        combined_features = np.concatenate([mean_features, var_features])
        rounded_features = np.round(combined_features, decimals=2)

        # Create a SHA-256 hash of the bytes representation
        feature_bytes = rounded_features.tobytes()
        song_id = hashlib.sha256(feature_bytes).hexdigest()

        return song_id

    def process_batch(
        self, file_paths: List[str], max_workers: int = 4
    ) -> Dict[str, Optional[str]]:
        """
        Process a batch of audio files concurrently to generate their Song IDs.

        Args:
            file_paths (List[str]): List of paths to audio files.
            max_workers (int): Maximum number of concurrent workers.

        Returns:
            Dict[str, Optional[str]]: A dictionary mapping file paths to their generated Song IDs.
        """
        results = {}
        if not self.has_dependencies:
            return {path: None for path in file_paths}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all generation tasks
            future_to_path = {
                executor.submit(self.generate_song_id, path): path for path in file_paths
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    song_id = future.result()
                    results[path] = song_id
                except Exception as e:
                    logger.error(f"Error processing {path} in batch: {e}")
                    results[path] = None

        return results

    def _process_chroma_batch(
        self, file_paths: List[str], max_workers: int = 4
    ) -> Dict[str, Optional[str]]:
        """
        Process a batch of audio files concurrently to generate their chroma hashes.

        Args:
            file_paths (List[str]): List of paths to audio files.
            max_workers (int): Maximum number of concurrent workers.

        Returns:
            Dict[str, Optional[str]]: A dictionary mapping file paths to their generated chroma hashes.
        """
        results = {}
        if not self.has_acoustid:
            return {path: None for path in file_paths}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.generate_chroma_hash, path): path for path in file_paths
            }
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    chroma_hash = future.result()
                    results[path] = chroma_hash
                except Exception as e:
                    logger.error(f"Error processing chroma hash for {path} in batch: {e}")
                    results[path] = None

        return results

    def _group_by_chroma(
        self, chroma_results: Dict[str, Optional[str]]
    ) -> tuple[Dict[str, List[str]], List[str], Dict[str, List[str]]]:
        """Helper to group files by chroma hash and separate fallback paths."""
        chroma_id_to_paths: Dict[str, List[str]] = {}
        fallback_paths: List[str] = []

        for path, chroma_hash in chroma_results.items():
            if chroma_hash is None:
                fallback_paths.append(path)
            else:
                if chroma_hash not in chroma_id_to_paths:
                    chroma_id_to_paths[chroma_hash] = []
                chroma_id_to_paths[chroma_hash].append(path)

        duplicates: Dict[str, List[str]] = {}
        for chroma_hash, paths in chroma_id_to_paths.items():
            if len(paths) > 1:
                duplicates[f"chroma_{chroma_hash}"] = paths
            elif len(paths) == 1:
                fallback_paths.append(paths[0])

        return chroma_id_to_paths, fallback_paths, duplicates

    def _process_fallback_paths(
        self, fallback_paths: List[str], max_workers: int, duplicates: Dict[str, List[str]]
    ) -> None:
        """Helper to process fallback paths with deep spectrogram computation."""
        song_ids_map = self.process_batch(fallback_paths, max_workers)
        id_to_paths: Dict[str, List[str]] = {}

        for path, song_id in song_ids_map.items():
            if song_id is None:
                continue
            if song_id not in id_to_paths:
                id_to_paths[song_id] = []
            id_to_paths[song_id].append(path)

        for song_id, paths in id_to_paths.items():
            if len(paths) > 1:
                duplicates[song_id] = paths

    def find_duplicates_in_batch(
        self, file_paths: List[str], max_workers: int = 4
    ) -> Dict[str, List[str]]:
        """
        Identify duplicate files within a batch using their generated Song IDs.
        Uses fast chroma hash first, and falls back to spectrogram for the rest.

        Args:
            file_paths (List[str]): List of paths to audio files.
            max_workers (int): Maximum number of concurrent workers.

        Returns:
            Dict[str, List[str]]: A dictionary mapping each unique Song ID (or chroma hash) to a list
                                  of duplicate file paths that share that ID.
                                  Only IDs with more than one file are returned.
        """
        # First pass: Fast chroma hash
        chroma_results = self._process_chroma_batch(file_paths, max_workers)

        _, fallback_paths, duplicates = self._group_by_chroma(chroma_results)

        # Second pass: Deep spectrogram computation for the rest
        if fallback_paths:
            self._process_fallback_paths(fallback_paths, max_workers, duplicates)

        return duplicates
