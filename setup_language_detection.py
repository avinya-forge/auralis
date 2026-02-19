#!/usr/bin/env python3
"""
Auralis - Language Detection Setup

This script installs the required dependencies for audio language detection.
"""

import platform
import subprocess
import sys

# Ensure we can import from src
import os
sys.path.append(os.getcwd())

from src.utils.dependency_checker import DependencyChecker


def install_dependencies():
    """Install the required dependencies for language detection"""
    print("Installing language detection dependencies...")

    # Define the required packages
    packages = ["SpeechRecognition>=3.8.0", "langdetect>=1.0.9", "pydub>=0.25.1"]

    checker = DependencyChecker()
    if checker.install_pip_packages(packages):
        print("Dependencies installed successfully!")

        # If on Windows, install pyaudio from wheel
        if platform.system().lower() == "windows":
            print("Installing PyAudio for Windows...")
            if not checker.install_pip_packages(["pyaudio"]):
                print("Could not install PyAudio automatically.")
                print("Please download and install PyAudio manually from:")
                print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        else:
            # For Linux/macOS, just try to install pyaudio normally
            print("Installing PyAudio...")
            if not checker.install_pip_packages(["pyaudio"]):
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
    else:
        return False


def test_dependencies():
    """Test if the dependencies are installed correctly"""
    print("Testing language detection dependencies...")

    checker = DependencyChecker()
    report = checker.check_all()

    lang_report = report["language_detection"]

    all_installed = True
    for mod, installed in lang_report.items():
        if installed:
            print(f"✓ {mod} installed")
        else:
            # Pyaudio is optional? Original script says "optional but good to have"
            if mod == "pyaudio":
                print(f"✗ {mod} not installed (Optional)")
            else:
                print(f"✗ {mod} not installed")
                all_installed = False

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
