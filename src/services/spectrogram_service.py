"""
Spectrogram Service

This module provides functionality to generate Mel-spectrograms from audio files
using librosa and compute distinct Song IDs based on these features for deduplication.
It also provides concurrent batch processing capabilities.
"""

import logging
from typing import Any, Dict, List, Optional
import hashlib
import concurrent.futures

logger = logging.getLogger(__name__)


class SpectrogramService:
    """
    Generates Mel-spectrograms and unique Song IDs for audio deduplication.
    """

    def __init__(self) -> None:
        """Initialize the SpectrogramService."""
        self.has_dependencies = self._check_dependencies()

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

    def find_duplicates_in_batch(
        self, file_paths: List[str], max_workers: int = 4
    ) -> Dict[str, List[str]]:
        """
        Identify duplicate files within a batch using their generated Song IDs.

        Args:
            file_paths (List[str]): List of paths to audio files.
            max_workers (int): Maximum number of concurrent workers.

        Returns:
            Dict[str, List[str]]: A dictionary mapping each unique Song ID to a list
                                  of duplicate file paths that share that ID.
                                  Only IDs with more than one file are returned.
        """
        song_ids_map = self.process_batch(file_paths, max_workers)

        id_to_paths: Dict[str, List[str]] = {}
        for path, song_id in song_ids_map.items():
            if song_id is None:
                continue
            if song_id not in id_to_paths:
                id_to_paths[song_id] = []
            id_to_paths[song_id].append(path)

        # Filter for only those with multiple files
        duplicates = {song_id: paths for song_id, paths in id_to_paths.items() if len(paths) > 1}

        return duplicates
