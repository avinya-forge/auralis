#!/usr/bin/env python3
"""
Auralis - Audio Similarity Detection Setup

This script installs the required dependencies for audio similarity detection.
"""

import os
import platform
import subprocess
import sys


def install_dependencies():
    """Install the required dependencies for audio similarity detection"""
    print("Installing audio similarity detection dependencies...")

    # Define the required packages
    packages = [
        "librosa>=0.9.0",
        "scikit-learn>=1.0.0",
        "soundfile>=0.10.0",
        "pydub>=0.25.1",
        "numpy>=1.20.0",
    ]

    # Install using pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("Dependencies installed successfully!")

        # Platform-specific installations
        if platform.system().lower() == "windows":
            try:
                # Some Windows machines need additional libraries
                print("Installing additional Windows dependencies...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-python"])
            except BaseException:
                print("Could not install ffmpeg-python. Audio conversion might be limited.")
        elif platform.system().lower() == "linux":
            print("Note: You may need to install the following system packages:")
            print("  - ffmpeg")
            print("  - libsndfile1")
            print("  - python3-dev")
            print("  - libasound2-dev")
            print("Using your distribution's package manager (apt, yum, etc.)")

        return True
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        return False


def check_module_installed(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} installed")
        return True
    except ImportError:
        print(f"✗ {module_name} not installed")
        return False


def test_audio_loading():
    """Test audio loading capabilities"""
    try:
        print("\nTesting audio loading capabilities...")
        import tempfile

        import librosa
        import numpy as np
        import soundfile as sf

        # Create a simple test audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            temp_path = temp.name

        # Generate a simple sine wave
        sample_rate = 22050
        duration = 1  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        x = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

        # Save as WAV
        sf.write(temp_path, x, sample_rate)

        # Test librosa loading
        y, sr = librosa.load(temp_path, sr=None)
        print(f"✓ librosa can load audio files (loaded {len(y)} samples at {sr} Hz)")

        # Clean up
        os.unlink(temp_path)

        print("Audio processing test passed!")
        return True
    except Exception as e:
        print(f"✗ Audio processing test failed: {str(e)}")
        print("Audio similarity detection may not work correctly.")
        return False


def test_dependencies():
    """Test if the dependencies are installed correctly"""
    print("Testing audio similarity detection dependencies...")

    modules_to_check = ["numpy", "librosa", "sklearn", "soundfile", "pydub"]

    all_installed = True
    for module in modules_to_check:
        if not check_module_installed(module):
            all_installed = False

    if not all_installed:
        return False

    print("All core dependencies are installed correctly!")

    return test_audio_loading()


if __name__ == "__main__":
    print("Auralis Audio Similarity Detection Setup")
    print("========================================")

    if install_dependencies():
        print("\nTesting installation:")
        if test_dependencies():
            print("\nSetup completed successfully!")
            print("You can now use audio-based similarity detection in Auralis.")
        else:
            print("\nSome dependencies could not be installed.")
            print("Please try installing them manually.")
    else:
        print("\nFailed to install dependencies.")
        print("Please try installing them manually:")
        print("pip install librosa scikit-learn soundfile pydub numpy")
