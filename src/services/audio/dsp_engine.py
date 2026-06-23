import logging
from typing import Any, Dict, Optional

import numpy as np

# Conditionally import librosa to avoid hard failure if missing
try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

logger = logging.getLogger(__name__)


class DSPEngine:
    """
    Digital Signal Processing Engine for Audio Analysis.
    Extracts high-quality features from audio signals.
    """

    def __init__(self, sr: int = 22050, sample_rate: int = 22050):
        # Support both kwargs
        self.sr = sr
        self.sample_rate = sample_rate

    def extract_chroma(self, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Extracts CQT-based chroma features (audio-002-1-chroma-features).
        Ensures numerical stability by catching warnings or errors
        and normalizing the signal.
        """
        if not LIBROSA_AVAILABLE:
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
        if not LIBROSA_AVAILABLE:
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

    def extract_features(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract DSP features (Chroma, BPM, Key) using librosa.
        """
        if not LIBROSA_AVAILABLE:
            logger.warning(
                "librosa is not available. DSP feature extraction will return mock data."
            )
            return self._mock_features()

        try:
            logger.info(f"Extracting DSP features for {file_path}")
            y, sr = librosa.load(file_path, sr=self.sample_rate)

            # 1. BPM / Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

            # 2. Chroma
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1).tolist()

            # 3. Key estimation (Simple rule-based off chroma mean)
            key = self._estimate_key(chroma_mean)

            features = {"bpm": round(bpm, 2), "key": key, "chroma_mean": chroma_mean}
            logger.debug(f"Extracted features: BPM={features['bpm']}, Key={features['key']}")
            return features
        except Exception as e:
            logger.error(f"Failed to extract DSP features from {file_path}: {e}")
            return None

    def _estimate_key(self, chroma_mean: list) -> str:
        """
        Very basic key estimation based on the dominant pitch class.
        In a real scenario, use Krumhansl-Schmuckler or similar.
        """
        pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        if not chroma_mean or len(chroma_mean) != 12:
            return "Unknown"

        dominant_index = np.argmax(chroma_mean)
        return pitch_classes[dominant_index]

    def _mock_features(self) -> Dict[str, Any]:
        """Return mock features if librosa is not available."""
        return {"bpm": 120.0, "key": "C", "chroma_mean": [0.1] * 12}
