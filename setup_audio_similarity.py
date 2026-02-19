#!/usr/bin/env python3
"""
Auralis - Audio Similarity Detection Setup

This script installs the required dependencies for audio similarity detection.
"""

import argparse
import os
import platform
import subprocess
import sys

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.utils.dependency_checker import DependencyChecker


def install_dependencies():
    """Install the required dependencies for audio similarity detection"""
    print("Installing audio similarity detection dependencies...")

    checker = DependencyChecker()

    # Define the required packages
    packages = [
        "librosa>=0.9.0",
        "scikit-learn>=1.0.0",
        "soundfile>=0.10.0",
        "pydub>=0.25.1",
        "numpy>=1.20.0",
    ]

    # Install using pip
    if checker.install_pip_packages(packages):
        print("Dependencies installed successfully!")

        # Platform-specific installations
        if platform.system().lower() == "windows":
            try:
                # Some Windows machines need additional libraries
                print("Installing additional Windows dependencies...")
                checker.install_pip_packages(["ffmpeg-python"])
            except subprocess.CalledProcessError:
                print("Could not install ffmpeg-python. Audio conversion might be limited.")
        elif platform.system().lower() == "linux":
            print("Note: You may need to install the following system packages:")
            print("  - ffmpeg")
            print("  - libsndfile1")
            print("  - python3-dev")
            print("  - libasound2-dev")
            print("Using your distribution's package manager (apt, yum, etc.)")

        return True
    else:
        print(f"Error installing dependencies.")
        return False


def check_system_dependencies():
    """Check for system-level dependencies"""
    print("\nChecking system dependencies...")
    checker = DependencyChecker()
    report = checker.check_all()

    tools = report["system_tools"]
    for tool, info in tools.items():
        if info["installed"]:
            print(f"✓ {tool} found at {info['path']}")
        else:
            print(f"✗ {tool} not found")
            if tool == "ffmpeg":
                 print("  Audio conversion and some analysis features require ffmpeg.")
                 # Print install instructions (generic)
            elif tool == "fpcalc":
                 print("  AcoustID fingerprinting requires fpcalc (Chromaprint).")

    if platform.system().lower() == "linux":
        lib = report["libraries"].get("sndfile", {})
        if lib.get("installed"):
             print(f"✓ libsndfile found: {lib['path']}")
        else:
             print("✗ libsndfile not found via ctypes")
             print("  Install libsndfile1 via your package manager.")


def test_dependencies():
    """Test if the dependencies are installed correctly"""
    print("\nTesting Python dependencies...")
    checker = DependencyChecker()
    report = checker.check_all()

    audio_sim = report["audio_similarity"]
    all_installed = True

    for mod, installed in audio_sim.items():
        if installed:
            print(f"✓ {mod} installed")
        else:
            print(f"✗ {mod} not installed")
            all_installed = False

    if not all_installed:
        return False

    print("All core dependencies are installed correctly!")

    print("\nTesting audio loading capabilities...")
    audio_report = checker.check_audio_capabilities()
    if audio_report["success"]:
        print(f"✓ {audio_report['message']}")
        return True
    else:
        print(f"✗ {audio_report['message']}")
        print("Audio similarity detection may not work correctly.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Auralis Audio Similarity Detection Setup")
    parser.add_argument(
        "--check-only", action="store_true", help="Only check dependencies without installing"
    )
    args = parser.parse_args()

    print("Auralis Audio Similarity Detection Setup")
    print("========================================")

    if args.check_only:
        check_system_dependencies()
        if test_dependencies():
            print("\nCheck completed successfully! Dependencies appear to be working.")
        else:
            print("\nCheck completed with issues.")
        return

    # Install mode
    if install_dependencies():
        check_system_dependencies()
        print("\nTesting installation:")
        if test_dependencies():
            print("\nSetup completed successfully!")
            print("You can now use audio-based similarity detection in Auralis.")
        else:
            print("\nSome dependencies could not be installed or verified.")
            print("Please try installing them manually.")
    else:
        print("\nFailed to install dependencies.")
        print("Please try installing them manually:")
        print("pip install librosa scikit-learn soundfile pydub numpy")


if __name__ == "__main__":
    main()
