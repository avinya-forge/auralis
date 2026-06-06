import logging
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
except ImportError:
    librosa = None  # type: ignore


class DSPEngine:
    """
    Digital Signal Processing Engine for Audio Analysis.
    Extracts high-quality features from audio signals.
    """

    def __init__(self, sr: int = 22050):
        self.sr = sr
        if librosa is None:
            logger.warning("librosa is not installed. DSPEngine will not function fully.")

    def extract_chroma(self, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Extracts CQT-based chroma features (audio-002-1-chroma-features).
        Ensures numerical stability by catching warnings or errors
        and normalizing the signal.
        """
        if librosa is None:
            return None

        try:
            # Add a small epsilon to avoid log of zero or division by zero in CQT
            y_stable = y + 1e-6 * np.random.randn(*y.shape)

            # CQT-based chroma
            chroma_func = getattr(librosa.feature, "chroma_cqt")
            chroma = chroma_func(y=y_stable, sr=self.sr)
            return np.array(chroma) if chroma is not None else None
        except Exception as e:
            logger.error(f"Failed to extract chroma features: {e}")
            return None

    def extract_rhythm(self, y: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Extracts BPM and onset strength (audio-002-2-rhythm-extraction).
        """
        if librosa is None:
            return None

        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=self.sr)
            tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=self.sr)

            return {
                "bpm": float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo),
                "onset_strength": onset_env,
                "beats": beats,
            }
        except Exception as e:
            logger.error(f"Failed to extract rhythm features: {e}")
            return None
