import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    import torchaudio.transforms as T
except ImportError:
    torch = None
    T = None


def generate_mel_spectrogram(
    y: np.ndarray,
    sr: int = 22050,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> Optional[np.ndarray]:
    """
    Generate normalized mel-spectrogram tensors from audio numpy arrays.
    Converts numpy array to torch tensor, processes with torchaudio,
    normalizes the output, and returns a numpy array.
    """
    if torch is None or T is None:
        logger.warning("torch/torchaudio not installed. Cannot generate mel-spectrogram.")
        return None

    try:
        # Convert to float32 tensor
        y_tensor = torch.from_numpy(y).float()

        # Ensure it's 2D: [channels, time]
        if y_tensor.dim() == 1:
            y_tensor = y_tensor.unsqueeze(0)

        mel_spectrogram_transform = T.MelSpectrogram(
            sample_rate=sr,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels,
            power=2.0,  # power spectrogram
            normalized=True,
        )

        mel_spec = mel_spectrogram_transform(y_tensor)

        # Convert to decibel scale for better perceptual representation
        amplitude_to_db = T.AmplitudeToDB()
        mel_db = amplitude_to_db(mel_spec)

        # Normalize to [0, 1] range based on typical DB ranges (-80 to 0)
        # We find max and min
        min_db = mel_db.min()
        max_db = mel_db.max()

        if max_db > min_db:
            normalized_mel = (mel_db - min_db) / (max_db - min_db)
        else:
            normalized_mel = torch.zeros_like(mel_db)

        return np.array(normalized_mel.numpy())

    except Exception as e:
        logger.error(f"Failed to generate mel-spectrogram: {e}")
        return None
