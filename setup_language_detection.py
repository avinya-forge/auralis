#!/usr/bin/env python3
"""
Auralis - Language Detection Setup

This script installs the required dependencies for audio language detection.
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install the required dependencies for language detection"""
    print("Installing language detection dependencies...")
    
    # Define the required packages
    packages = [
        "SpeechRecognition>=3.8.0",
        "langdetect>=1.0.9",
        "pydub>=0.25.1"
    ]
    
    # Install using pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("Dependencies installed successfully!")
        
        # If on Windows, install pyaudio from wheel
        if platform.system().lower() == 'windows':
            try:
                print("Installing PyAudio for Windows...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            except:
                print("Could not install PyAudio automatically.")
                print("Please download and install PyAudio manually from:")
                print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        else:
            # For Linux/macOS, just try to install pyaudio normally
            # (may require additional system dependencies)
            try:
                print("Installing PyAudio...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            except:
                if platform.system().lower() == 'darwin':  # macOS
                    print("Could not install PyAudio automatically.")
                    print("Try running: brew install portaudio")
                    print("Then: pip install pyaudio")
                else:  # Linux
                    print("Could not install PyAudio automatically.")
                    print("Try running: sudo apt-get install python3-pyaudio")
                    print("Or: sudo apt-get install portaudio19-dev")
                    print("Then: pip install pyaudio")
        
        return True
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        return False

def test_dependencies():
    """Test if the dependencies are installed correctly"""
    print("Testing language detection dependencies...")
    
    try:
        import speech_recognition
        print("✓ SpeechRecognition installed")
    except ImportError:
        print("✗ SpeechRecognition not installed")
        return False
    
    try:
        import langdetect
        print("✓ langdetect installed")
    except ImportError:
        print("✗ langdetect not installed")
        return False
    
    try:
        import pydub
        print("✓ pydub installed")
    except ImportError:
        print("✗ pydub not installed")
        return False
    
    try:
        import pyaudio
        print("✓ pyaudio installed")
    except ImportError:
        print("✗ pyaudio not installed (required for microphone access)")
        # Not a fatal error, as we can still use audio files
    
    print("All core dependencies are installed correctly!")
    return True

if __name__ == "__main__":
    print("Auralis Language Detection Setup")
    print("================================")
    
    if install_dependencies():
        print("\nTesting installation:")
        if test_dependencies():
            print("\nSetup completed successfully!")
            print("You can now use audio-based language detection in Auralis.")
        else:
            print("\nSome dependencies could not be installed.")
            print("Please try installing them manually.")
    else:
        print("\nFailed to install dependencies.")
        print("Please try installing them manually:")
        print("pip install SpeechRecognition langdetect pydub pyaudio") 