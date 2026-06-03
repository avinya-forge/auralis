import logging
from typing import Any, Dict, Optional, cast

import librosa
import numpy as np


def extract_chroma(file_path: str) -> Optional[np.ndarray]:
    try:
        y, sr = librosa.load(file_path)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        return cast(np.ndarray, chroma)
    except Exception as e:
        logging.error(f"Failed to extract chroma: {e}")
        return None


def extract_rhythm(file_path: str) -> Optional[Dict[str, Any]]:
    try:
        y, sr = librosa.load(file_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        bpm = float(tempo[0]) if isinstance(tempo, (np.ndarray, list)) else float(tempo)
        return {"bpm": bpm, "onset_strength": onset_env}
    except Exception as e:
        logging.error(f"Failed to extract rhythm: {e}")
        return None
