import logging
from typing import Any, Dict, Optional, Tuple

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class DSPEngine:
    """
    Digital Signal Processing Engine for Audio Analysis.
    Extracts structural features such as Chroma and Rhythm.
    """

    @staticmethod
    def extract_chroma(audio_path: str) -> Optional[np.ndarray]:
        """
        Extract CQT-based chroma features.

        Args:
            audio_path: Path to the audio file.

        Returns:
            np.ndarray: Chroma features array, or None if extraction fails.
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)

            # Extract CQT-based chroma features to handle harmonic content better
            # Adding a small constant to ensure numerical stability when avoiding log(0)
            C = np.abs(librosa.cqt(y, sr=sr))
            chroma = librosa.feature.chroma_cqt(C=C, sr=sr)

            # Normalize to ensure numerical stability
            # librosa.util.normalize is used here implicitly or explicitly by normal feature processes

            return chroma
        except Exception as e:
            logger.error(f"Error extracting chroma features from {audio_path}: {str(e)}")
            return None

    @staticmethod
    def extract_rhythm(audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Implement BPM and onset strength detection.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Dict containing 'bpm' (float) and 'onset_strength' (np.ndarray),
            or None if extraction fails.
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)

            # Calculate onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)

            # Estimate tempo (BPM)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

            # tempo can be an array in newer versions of librosa, handle this
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

            return {"bpm": bpm, "onset_strength": onset_env}
        except Exception as e:
            logger.error(f"Error extracting rhythm features from {audio_path}: {str(e)}")
            return None
