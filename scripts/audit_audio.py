#!/usr/bin/env python3
"""
Audit script to detect harmonic distortion in demixed stems.
(Task: audio-audit-distortion)
Calculates an estimated Signal-to-Noise Ratio (SNR) or harmonic distortion
metric based on spectral energy distribution using scipy/numpy.
"""

import argparse
import logging
import sys

try:
    import numpy as np
    import scipy.io.wavfile as wav
    from scipy.fft import rfft, rfftfreq
except ImportError:
    print("Error: numpy and scipy are required for this script.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def calculate_thd(signal: np.ndarray, sr: int) -> float:
    """
    Estimates Total Harmonic Distortion (THD).
    This is a simplified estimation by finding the peak frequency (fundamental)
    and summing the energy of its harmonics compared to the fundamental.
    """
    # Use real FFT for performance
    yf = np.abs(rfft(signal))
    xf = rfftfreq(len(signal), 1 / sr)

    # Find fundamental frequency (peak magnitude)
    peak_idx = np.argmax(yf)
    fundamental_freq = xf[peak_idx]
    fundamental_energy = yf[peak_idx] ** 2

    if fundamental_energy == 0:
        return 0.0

    # Calculate energy of harmonics
    harmonic_energy = 0.0
    for i in range(2, 10):  # Check up to 9th harmonic
        harmonic_freq = fundamental_freq * i
        # Find closest bin
        if harmonic_freq > xf[-1]:
            break
        closest_idx = np.argmin(np.abs(xf - harmonic_freq))
        harmonic_energy += yf[closest_idx] ** 2

    # THD formula: sqrt(sum(harmonics^2)) / fundamental
    # which is sqrt(harmonic_energy / fundamental_energy)
    thd = np.sqrt(harmonic_energy / fundamental_energy)
    return float(thd)


def calculate_snr(signal: np.ndarray, reference: np.ndarray) -> float:
    """Calculates Signal-to-Noise Ratio given a reference clean signal."""
    if len(signal) != len(reference):
        min_len = min(len(signal), len(reference))
        signal = signal[:min_len]
        reference = reference[:min_len]

    noise = signal - reference
    signal_power = np.mean(reference**2)
    noise_power = np.mean(noise**2)

    if noise_power == 0:
        return float("inf")

    snr = 10 * np.log10(signal_power / noise_power)
    return float(snr)


def main():
    parser = argparse.ArgumentParser(description="Detect harmonic distortion in stems.")
    parser.add_argument("stem_path", type=str, help="Path to the demixed stem wav file")
    parser.add_argument(
        "--reference", type=str, help="Optional clean reference for SNR", default=None
    )

    args = parser.parse_args()

    try:
        sr, signal = wav.read(args.stem_path)
    except Exception as e:
        logging.error(f"Failed to read {args.stem_path}: {e}")
        sys.exit(1)

    # Convert to float
    if signal.dtype != np.float32 and signal.dtype != np.float64:
        signal = signal.astype(np.float32) / np.iinfo(signal.dtype).max

    # Handle stereo
    if len(signal.shape) > 1:
        signal = np.mean(signal, axis=1)

    thd = calculate_thd(signal, sr)
    logging.info(f"File: {args.stem_path}")
    logging.info(f"Estimated THD: {thd * 100:.2f}%")

    if args.reference:
        try:
            _, ref_signal = wav.read(args.reference)
            if ref_signal.dtype != np.float32 and ref_signal.dtype != np.float64:
                ref_signal = ref_signal.astype(np.float32) / np.iinfo(ref_signal.dtype).max
            if len(ref_signal.shape) > 1:
                ref_signal = np.mean(ref_signal, axis=1)

            snr = calculate_snr(signal, ref_signal)
            logging.info(f"SNR vs Reference: {snr:.2f} dB")
        except Exception as e:
            logging.error(f"Failed to process reference file: {e}")


if __name__ == "__main__":
    main()
