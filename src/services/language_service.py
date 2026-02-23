"""
Auralis - Language Detection Service

This module provides functionality to detect the spoken language in audio files.
It uses speech recognition to extract text from audio, then performs language detection.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, cast

# Optional dependencies will be imported lazily
pass

# Set up logging
logger = logging.getLogger("auralis.language")

# Language name mapping for better display and folder names
LANGUAGE_NAMES = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "gu": "Gujarati",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "kn": "Kannada",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pa": "Punjabi",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "so": "Somali",
    "sq": "Albanian",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Tagalog",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-cn": "Chinese_Simplified",
    "zh-tw": "Chinese_Traditional",
}


class LanguageDetectionService:
    """Service for detecting spoken language in audio files"""

    def __init__(self) -> None:
        """Initialize the language detection service"""
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        """Check if language detection dependencies are available"""
        if self._available is None:
            self._available = self._check_dependencies()
        return self._available

    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        try:
            import langdetect
            import speech_recognition
            import pydub

            return True
        except ImportError:
            logger.warning(
                "Language detection dependencies not installed. "
                "Please install: speech_recognition, langdetect, pydub"
            )
            return False

    def detect_language(self, file_path: str, sample_duration: int = 30) -> Tuple[str, str]:
        """
        Detect the spoken language in an audio file

        Args:
            file_path (str): Path to the audio file
            sample_duration (int): Duration in seconds to sample from the audio for detection

        Returns:
            tuple: (language_code, language_name) or ('unknown', 'Unknown')
        """
        if not self.available:
            return "unknown", "Unknown"

        try:
            # Load audio file
            audio_path = Path(file_path)
            if not audio_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return "unknown", "Unknown"

            # Extract a segment for processing
            logger.info(f"Processing {file_path} for language detection")
            return self._process_audio_detection(file_path, sample_duration)

        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return "unknown", "Unknown"

    def _process_audio_detection(self, file_path: str, sample_duration: int) -> Tuple[str, str]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_path = temp_wav.name

        try:
            self._extract_audio_sample(file_path, temp_path, sample_duration)
            text = self._recognize_speech(temp_path)

            # Clean up temporary file
            os.unlink(temp_path)

            return self._detect_from_text(text, file_path)

        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            # Clean up temporary file if it exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return "unknown", "Unknown"

    def _extract_audio_sample(self, file_path: str, temp_path: str, sample_duration: int) -> None:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(file_path)
        middle = len(audio) // 2
        start_pos = max(0, middle - (sample_duration * 1000) // 2)
        end_pos = min(len(audio), start_pos + (sample_duration * 1000))
        audio_sample = audio[start_pos:end_pos]
        audio_sample.export(temp_path, format="wav")

    def _recognize_speech(self, temp_path: str) -> Optional[str]:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            try:
                return cast(Optional[str], recognizer.recognize_google(audio_data))
            except (sr.UnknownValueError, sr.RequestError):
                return None

    def _detect_from_text(self, text: Optional[str], file_path: str) -> Tuple[str, str]:
        import langdetect

        if text and len(text.strip()) > 5:
            lang_code = langdetect.detect(text)
            lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.capitalize())
            logger.info(f"Detected language: {lang_name} ({lang_code}) in {file_path}")
            return lang_code, lang_name
        else:
            logger.warning(f"Not enough text extracted for language detection in {file_path}")
            return "unknown", "Unknown"

    def get_language_folder(self, file_path: str, default: str = "Unknown") -> str:
        """
        Get the appropriate language folder name for an audio file

        Args:
            file_path (str): Path to the audio file
            default (str): Default folder name if language detection fails

        Returns:
            str: Folder name based on detected language
        """
        lang_code, lang_name = self.detect_language(file_path)
        if lang_code == "unknown":
            return default
        return lang_name


# Singleton instance
language_service = LanguageDetectionService()


def detect_language(file_path: str) -> Tuple[str, str]:
    """Detect the language of an audio file"""
    return language_service.detect_language(file_path)


def get_language_folder(file_path: str, default: str = "Unknown") -> str:
    """Get the appropriate language folder for an audio file"""
    return language_service.get_language_folder(file_path, default)


def is_available() -> bool:
    """Check if language detection is available"""
    return language_service.available
