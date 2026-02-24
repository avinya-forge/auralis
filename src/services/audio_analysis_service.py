"""
Audio Analysis Service

This module provides functionality to analyze audio files for musical properties
such as BPM (Beats Per Minute) and Key (Tonality).
It uses the `librosa` library for audio signal processing.
"""

import logging
from typing import Any, Optional

# Lazy imports for optional dependencies
try:
    import mutagen
    import mutagen.flac
    import mutagen.id3
    import mutagen.ogg

    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Analyzes audio files for musical properties.
    """

    def __init__(self) -> None:
        """Initialize the AudioAnalyzer."""
        self._check_dependencies()

    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        try:
            import librosa  # noqa: F401
            import numpy  # noqa: F401

            return True
        except ImportError:
            logger.warning("Librosa or numpy not installed. Audio analysis will not work.")
            return False

    def get_bpm(self, file_path: str) -> Optional[float]:
        """
        Detect BPM (Beats Per Minute) of an audio file.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[float]: The detected BPM, or None if detection failed.
        """
        try:
            import librosa
            import numpy as np
        except ImportError:
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
        try:
            import librosa
            import numpy as np
        except ImportError:
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
        import numpy as np

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

    def get_mood(self, bpm: float, key: str) -> str:
        """
        Determine mood based on BPM and Key (Heuristic).

        Args:
            bpm (float): Beats per minute.
            key (str): Key (e.g., 'C Major', 'A Minor').

        Returns:
            str: Detected mood (e.g., 'Energetic', 'Calm', 'Melancholic', 'Happy').
        """
        if not bpm or not key:
            return "Unknown"

        is_major = "Major" in key

        if bpm >= 120:
            return "Energetic" if is_major else "Intense"
        elif bpm >= 90:
            return "Happy" if is_major else "Melancholic"
        else:
            return "Calm" if is_major else "Sad"

    def save_analysis_tags(
        self,
        file_path: str,
        bpm: Optional[float] = None,
        key: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> bool:
        """
        Save analysis results to audio file tags.

        Args:
            file_path (str): Path to the audio file.
            bpm (Optional[float]): BPM value.
            key (Optional[str]): Key value.
            mood (Optional[str]): Mood value.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not HAS_MUTAGEN:
            logger.warning("Mutagen not installed. Cannot save analysis tags.")
            return False

        try:
            audio = mutagen.File(file_path)
            if not audio:
                return False

            # Round BPM
            bpm_str = str(int(round(bpm))) if bpm else ""

            if isinstance(audio, mutagen.mp3.MP3):
                self._save_mp3_tags(audio, bpm_str, key, mood)
            elif isinstance(audio, mutagen.flac.FLAC) or isinstance(audio, mutagen.ogg.OggVorbis):
                self._save_vorbis_tags(audio, bpm_str, key, mood)

            # Save changes
            audio.save()
            return True

        except Exception as e:
            logger.error(f"Error saving analysis tags for {file_path}: {e}")
            return False

    def _save_mp3_tags(
        self, audio: Any, bpm_str: str, key: Optional[str], mood: Optional[str]
    ) -> None:
        """Save analysis tags to MP3 file."""
        if bpm_str:
            audio["TBPM"] = mutagen.id3.TBPM(encoding=3, text=bpm_str)
        if key:
            audio["TKEY"] = mutagen.id3.TKEY(encoding=3, text=key)
        if mood:
            audio["TMOO"] = mutagen.id3.TMOO(encoding=3, text=mood)

    def _save_vorbis_tags(
        self, audio: Any, bpm_str: str, key: Optional[str], mood: Optional[str]
    ) -> None:
        """Save analysis tags to Vorbis/FLAC file."""
        if bpm_str:
            audio["bpm"] = bpm_str
        if key:
            audio["initialkey"] = key
        if mood:
            audio["mood"] = mood

    def calculate_replay_gain(
        self, file_path: str, target_dbfs: float = -14.0
    ) -> Optional[float]:
        """
        Calculate ReplayGain (Track Gain) to reach target dBFS.

        Args:
            file_path (str): Path to audio file.
            target_dbfs (float): Target loudness in dBFS.

        Returns:
            Optional[float]: Gain in dB.
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            logger.warning("pydub not installed. Cannot calculate ReplayGain.")
            return None

        try:
            # Load audio
            audio = AudioSegment.from_file(file_path)
            current_dbfs = audio.dBFS
            gain = target_dbfs - current_dbfs
            return float(gain)
        except Exception as e:
            logger.error(f"Error calculating ReplayGain for {file_path}: {e}")
            return None

    def save_replay_gain_tags(self, file_path: str, gain: float) -> bool:
        """
        Save ReplayGain tags to audio file.

        Args:
            file_path (str): Path to audio file.
            gain (float): Gain value in dB.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not HAS_MUTAGEN:
            logger.warning("Mutagen not installed. Cannot save ReplayGain tags.")
            return False

        try:
            audio = mutagen.File(file_path)
            if not audio:
                return False

            gain_str = f"{gain:.2f} dB"

            if isinstance(audio, mutagen.mp3.MP3):
                # ID3v2.4 RVA2 or TXXX:REPLAYGAIN_TRACK_GAIN
                # Using TXXX for broader compatibility
                audio.tags.add(
                    mutagen.id3.TXXX(encoding=3, desc="REPLAYGAIN_TRACK_GAIN", text=gain_str)
                )
            elif isinstance(audio, mutagen.flac.FLAC) or isinstance(audio, mutagen.ogg.OggVorbis):
                audio["REPLAYGAIN_TRACK_GAIN"] = gain_str

            audio.save()
            return True

        except Exception as e:
            logger.error(f"Error saving ReplayGain tags for {file_path}: {e}")
            return False
