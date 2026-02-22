"""
Audio Analysis Service

This module provides functionality to analyze audio files for musical properties
such as BPM (Beats Per Minute) and Key (Tonality).
It uses the `librosa` library for audio signal processing.
"""

import logging
from typing import Any, Optional

import numpy as np

try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Analyzes audio files for musical properties.
    """

    def __init__(self) -> None:
        """Initialize the AudioAnalyzer."""
        if not HAS_LIBROSA:
            logger.warning("Librosa not installed. Audio analysis will not work.")

    def get_bpm(self, file_path: str) -> Optional[float]:
        """
        Detect BPM (Beats Per Minute) of an audio file.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[float]: The detected BPM, or None if detection failed.
        """
        if not HAS_LIBROSA:
            return None

        try:
            # Load audio (only first 60 seconds to speed up)
            y, sr = librosa.load(file_path, sr=None, duration=60)

            # Detect tempo
            # beat_track returns tempo as a float or array of floats
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            if isinstance(tempo, np.ndarray):
                # Ensure we return a scalar float
                return float(tempo[0]) if tempo.size > 0 else 0.0
            return float(tempo)

        except Exception as e:
            logger.error(f"Error detecting BPM for {file_path}: {e}")
            return None

    def get_key(self, file_path: str) -> Optional[str]:
        """
        Detect Key of an audio file.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[str]: The detected Key (e.g., 'C Major', 'A Minor'), or None.
        """
        if not HAS_LIBROSA:
            return None

        try:
            # Load audio (first 60 seconds)
            y, sr = librosa.load(file_path, sr=None, duration=60)

            # Compute chroma features
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Sum chroma over time
            chroma_sum = np.sum(chroma, axis=1)

            # Detect key
            return self._detect_key_from_chroma(chroma_sum)

        except Exception as e:
            logger.error(f"Error detecting Key for {file_path}: {e}")
            return None

    def _detect_key_from_chroma(self, chroma_sum: Any) -> str:
        """
        Detect key from summed chroma features using Krumhansl-Schmuckler profiles.

        Args:
            chroma_sum (np.ndarray): Summed chroma features (12-element array).

        Returns:
            str: Detected key name.
        """
        # Pitch classes
        pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        # Krumhansl-Schmuckler key profiles
        major_profile = np.array(
            [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        )
        minor_profile = np.array(
            [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        )

        # Normalize chroma sum
        norm = np.linalg.norm(chroma_sum)
        chroma_norm = chroma_sum / norm if norm > 0 else chroma_sum

        max_corr = -1.0
        best_key = ""

        # Check all 12 major keys
        for i in range(12):
            # Rotate profile to match the key
            profile = np.roll(major_profile, i)
            profile_norm = profile / np.linalg.norm(profile)
            corr = np.dot(chroma_norm, profile_norm)

            if corr > max_corr:
                max_corr = corr
                best_key = f"{pitch_classes[i]} Major"

        # Check all 12 minor keys
        for i in range(12):
            profile = np.roll(minor_profile, i)
            profile_norm = profile / np.linalg.norm(profile)
            corr = np.dot(chroma_norm, profile_norm)

            if corr > max_corr:
                max_corr = corr
                best_key = f"{pitch_classes[i]} Minor"

        return best_key
