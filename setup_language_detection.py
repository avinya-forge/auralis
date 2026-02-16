#!/usr/bin/env python3
"""
Auralis - Language Detection Setup

This script installs the required dependencies for audio language detection.
"""

import platform
import subprocess
import sys


def install_dependencies():
    """Install the required dependencies for language detection"""
    print("Installing language detection dependencies...")

    # Define the required packages
    packages = ["SpeechRecognition>=3.8.0", "langdetect>=1.0.9", "pydub>=0.25.1"]

    # Install using pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("Dependencies installed successfully!")

        # If on Windows, install pyaudio from wheel
        if platform.system().lower() == "windows":
            try:
                print("Installing PyAudio for Windows...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            except BaseException:
                print("Could not install PyAudio automatically.")
                print("Please download and install PyAudio manually from:")
                print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        else:
            # For Linux/macOS, just try to install pyaudio normally
            # (may require additional system dependencies)
            try:
                print("Installing PyAudio...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            except BaseException:
                if platform.system().lower() == "darwin":  # macOS
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


def check_module_installed(module_name, required=True):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} installed")
        return True
    except ImportError:
        print(f"✗ {module_name} not installed")
        if not required:
            print(f"  (Note: {module_name} is optional but recommended)")
        return False


def test_dependencies():
    """Test if the dependencies are installed correctly"""
    print("Testing language detection dependencies...")

    required_modules = ["speech_recognition", "langdetect", "pydub"]

    all_installed = True
    for module in required_modules:
        if not check_module_installed(module):
            all_installed = False

    # PyAudio is optional for some features but good to have
    check_module_installed("pyaudio", required=False)

    if all_installed:
        print("All core dependencies are installed correctly!")
        return True
    else:
        return False


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
