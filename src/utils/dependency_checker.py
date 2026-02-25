"""
Auralis - Dependency Checker Module

This module provides utilities for checking and managing system and Python dependencies.
"""

import ctypes.util
import importlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional


class DependencyChecker:
    """
    Handles checking and validation of system and Python dependencies.
    """

    @staticmethod
    def check_module(module_name: str) -> bool:
        """
        Check if a Python module is installed and importable.

        Args:
            module_name (str): The name of the module to check (import name).

        Returns:
            bool: True if the module can be imported, False otherwise.
        """
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False

    @staticmethod
    def check_system_tool(tool_name: str) -> Optional[str]:
        """
        Check if a system tool is available in the PATH.

        Args:
            tool_name (str): The name of the tool (e.g., 'ffmpeg').

        Returns:
            Optional[str]: The path to the tool if found, None otherwise.
        """
        return shutil.which(tool_name)

    @staticmethod
    def check_library(library_name: str) -> Optional[str]:
        """
        Check if a shared library is available via ctypes.

        Args:
            library_name (str): The name of the library (e.g., 'sndfile').

        Returns:
            Optional[str]: The path/name of the library if found, None otherwise.
        """
        return ctypes.util.find_library(library_name)

    def check_audio_capabilities(self) -> Dict[str, Any]:
        """
        Test audio loading capabilities by generating and loading a sample file.

        Returns:
            Dict[str, Any]: A report of the test results.
        """
        report = {"success": False, "message": "", "details": {}}

        # Check required modules for this test
        required_modules = ["numpy", "soundfile", "librosa"]
        missing = [m for m in required_modules if not self.check_module(m)]

        if missing:
            report["message"] = f"Missing required modules for audio test: {', '.join(missing)}"
            return report

        try:
            import librosa
            import numpy as np
            import soundfile as sf

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
                temp_path = temp.name

            try:
                # Generate a simple sine wave
                sample_rate = 22050
                duration = 1.0  # seconds
                t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
                x = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

                # Save as WAV
                sf.write(temp_path, x, sample_rate)

                # Test librosa loading
                y, sr = librosa.load(temp_path, sr=None)

                report["success"] = True
                report["message"] = "Audio processing test passed"
                report["details"] = {
                    "samples_loaded": len(y),
                    "sample_rate": sr,
                    "duration": duration,
                }

            finally:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

        except Exception as e:
            report["success"] = False
            report["message"] = f"Audio processing test failed: {str(e)}"

        return report

    def check_ai_dependencies(self) -> Dict[str, Any]:
        """
        Check for AI-specific dependencies with detailed version/device info.

        Returns:
            Dict[str, Any]: AI dependency status report.
        """
        report: Dict[str, Any] = {
            "torch": {"installed": False, "version": None, "cuda": False, "mps": False},
            "torchaudio": {"installed": False, "version": None},
            "transformers": {"installed": False, "version": None},
            "scipy": {"installed": False, "version": None},
            "librosa": {"installed": False, "version": None},
        }

        # Check PyTorch specifically
        try:
            import torch

            report["torch"]["installed"] = True
            report["torch"]["version"] = torch.__version__
            report["torch"]["cuda"] = torch.cuda.is_available()
            report["torch"]["mps"] = (
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
            )
        except ImportError:
            pass

        # Check other AI dependencies
        for module in ["torchaudio", "transformers", "scipy", "librosa"]:
            try:
                mod = importlib.import_module(module)
                report[module]["installed"] = True
                report[module]["version"] = getattr(mod, "__version__", "unknown")
            except ImportError:
                pass

        return report

    def check_all(self) -> Dict[str, Any]:
        """
        Run a comprehensive check of all known dependencies.

        Returns:
            Dict[str, Any]: A complete status report.
        """
        report: Dict[str, Any] = {
            "platform": platform.system(),
            "python_version": sys.version,
            "core": {},
            "audio_similarity": {},
            "language_detection": {},
            "ai": {},
            "system_tools": {},
            "libraries": {},
        }

        # Core dependencies (import names)
        core_modules = ["PyQt6", "mutagen", "requests", "tqdm", "psutil"]
        for mod in core_modules:
            report["core"][mod] = self.check_module(mod)

        # Audio Similarity dependencies (import names)
        # Note: scikit-learn is imported as sklearn
        audio_sim_modules = ["librosa", "sklearn", "soundfile", "pydub", "numpy", "acoustid"]
        for mod in audio_sim_modules:
            report["audio_similarity"][mod] = self.check_module(mod)

        if platform.system() == "Windows":
            # ffmpeg-python is usually not imported directly in check logic but needed
            # However, it might be imported as ffmpeg. Let's check package name equivalent?
            # No, check_module checks import. ffmpeg-python imports as ffmpeg.
            report["audio_similarity"]["ffmpeg"] = self.check_module("ffmpeg")

        # Language Detection dependencies (import names)
        lang_det_modules = ["speech_recognition", "langdetect", "pydub", "pyaudio"]
        for mod in lang_det_modules:
            report["language_detection"][mod] = self.check_module(mod)

        # AI dependencies (detailed check)
        ai_report = self.check_ai_dependencies()
        for mod, data in ai_report.items():
            report["ai"][mod] = data["installed"]

        # System Tools
        tools = ["ffmpeg", "ffprobe", "fpcalc"]
        for tool in tools:
            path = self.check_system_tool(tool)
            report["system_tools"][tool] = {"installed": path is not None, "path": path}

        # Libraries (Linux)
        if platform.system() == "Linux":
            lib = self.check_library("sndfile")
            report["libraries"]["sndfile"] = {"installed": lib is not None, "path": lib}

        return report

    def get_install_instructions(self, missing_modules: List[str], missing_tools: List[str]) -> str:
        """
        Get instructions for installing missing items.

        Args:
            missing_modules (List[str]): List of missing Python modules.
            missing_tools (List[str]): List of missing system tools.

        Returns:
            str: Installation instructions.
        """
        instructions = []
        pip_packages = []

        # Map common missing items to packages
        pip_map = {
            "speech_recognition": "SpeechRecognition",
            "sklearn": "scikit-learn",
            "pyaudio": "pyaudio",
            "ffmpeg": "ffmpeg-python",  # usually for windows python
        }

        for item in missing_modules:
            pip_packages.append(pip_map.get(item, item))

        if pip_packages:
            instructions.append("To install missing Python packages:")
            instructions.append(f"  pip install {' '.join(pip_packages)}")

            if "pyaudio" in pip_packages and platform.system() == "Windows":
                instructions.append(
                    "  (Note: PyAudio on Windows may require manual installation from wheel)"
                )
            if "pyaudio" in pip_packages and platform.system() == "Linux":
                instructions.append(
                    "  (Note: PyAudio on Linux requires portaudio19-dev: sudo apt-get install portaudio19-dev)"
                )

        if missing_tools:
            instructions.append("\nTo install missing system tools:")
            if platform.system() == "Darwin":
                instructions.append(f"  brew install {' '.join(missing_tools)}")
            elif platform.system() == "Linux":
                instructions.append(f"  sudo apt-get install {' '.join(missing_tools)}")
            elif platform.system() == "Windows":
                instructions.append(f"  Download {'/'.join(missing_tools)} and add to PATH.")

        return "\n".join(instructions)

    def install_pip_packages(self, packages: List[str]) -> bool:
        """
        Attempt to install pip packages.

        Args:
            packages (List[str]): List of package names to install.

        Returns:
            bool: True if installation was successful.
        """
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
            return True
        except subprocess.CalledProcessError:
            return False
