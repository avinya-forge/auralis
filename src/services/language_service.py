"""
Auralis - Language Detection Service

This module provides functionality to detect the spoken language in audio files.
It uses speech recognition to extract text from audio, then performs language detection.
"""

import os
import tempfile
import logging
from pathlib import Path

# Import optional dependencies for language detection
try:
    import speech_recognition as sr
    import langdetect
    from pydub import AudioSegment
    HAS_LANGUAGE_DETECTION = True
except ImportError:
    HAS_LANGUAGE_DETECTION = False

# Set up logging
logger = logging.getLogger('auralis.language')

# Language name mapping for better display and folder names
LANGUAGE_NAMES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'ca': 'Catalan',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
    'et': 'Estonian',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'gu': 'Gujarati',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'hu': 'Hungarian',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'kn': 'Kannada',
    'ko': 'Korean',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'sq': 'Albanian',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tl': 'Tagalog',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'vi': 'Vietnamese',
    'zh-cn': 'Chinese_Simplified',
    'zh-tw': 'Chinese_Traditional'
}

class LanguageDetectionService:
    """Service for detecting spoken language in audio files"""
    
    def __init__(self):
        """Initialize the language detection service"""
        self.available = HAS_LANGUAGE_DETECTION
        if not self.available:
            logger.warning("Language detection dependencies not installed. "
                          "Please install: speech_recognition, langdetect, pydub")
    
    def detect_language(self, file_path, sample_duration=30):
        """
        Detect the spoken language in an audio file
        
        Args:
            file_path (str): Path to the audio file
            sample_duration (int): Duration in seconds to sample from the audio for detection
            
        Returns:
            tuple: (language_code, language_name) or ('unknown', 'Unknown')
        """
        if not self.available:
            logger.warning("Language detection not available")
            return 'unknown', 'Unknown'
        
        try:
            # Load audio file
            audio_path = Path(file_path)
            if not audio_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return 'unknown', 'Unknown'
            
            # Extract a segment for processing
            logger.info(f"Processing {file_path} for language detection")
            
            # Convert to WAV for speech recognition
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_path = temp_wav.name
            
            # Load audio and extract a sample for processing
            try:
                audio = AudioSegment.from_file(file_path)
                
                # Take a sample from the middle of the file (more likely to contain speech)
                middle = len(audio) // 2
                start_pos = max(0, middle - (sample_duration * 1000) // 2)
                end_pos = min(len(audio), start_pos + (sample_duration * 1000))
                
                audio_sample = audio[start_pos:end_pos]
                audio_sample.export(temp_path, format="wav")
                
                # Perform speech recognition
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_path) as source:
                    audio_data = recognizer.record(source)
                    try:
                        # Try Google's speech recognition (more languages)
                        text = recognizer.recognize_google(audio_data)
                    except sr.UnknownValueError:
                        logger.warning(f"Could not understand audio in {file_path}")
                        return 'unknown', 'Unknown'
                    except sr.RequestError:
                        logger.error("API unavailable for speech recognition")
                        return 'unknown', 'Unknown'
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                # Detect language from text
                if text and len(text.strip()) > 5:
                    lang_code = langdetect.detect(text)
                    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.capitalize())
                    logger.info(f"Detected language: {lang_name} ({lang_code}) in {file_path}")
                    return lang_code, lang_name
                else:
                    logger.warning(f"Not enough text extracted for language detection in {file_path}")
                    return 'unknown', 'Unknown'
                
            except Exception as e:
                logger.error(f"Error processing audio: {str(e)}")
                # Clean up temporary file if it exists
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return 'unknown', 'Unknown'
                
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return 'unknown', 'Unknown'

    def get_language_folder(self, file_path, default="Unknown"):
        """
        Get the appropriate language folder name for an audio file
        
        Args:
            file_path (str): Path to the audio file
            default (str): Default folder name if language detection fails
            
        Returns:
            str: Folder name based on detected language
        """
        lang_code, lang_name = self.detect_language(file_path)
        if lang_code == 'unknown':
            return default
        return lang_name

# Singleton instance
language_service = LanguageDetectionService()

def detect_language(file_path):
    """Detect the language of an audio file"""
    return language_service.detect_language(file_path)

def get_language_folder(file_path, default="Unknown"):
    """Get the appropriate language folder for an audio file"""
    return language_service.get_language_folder(file_path, default)

def is_available():
    """Check if language detection is available"""
    return language_service.available 