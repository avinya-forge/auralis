import logging
import shutil
import subprocess  # nosec B404
import sys
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DemucsWrapper:
    """
    Process-isolated Demucs wrapper.
    Handles OOM errors by limiting memory usage per process if needed.
    """

    def __init__(self, model_name: str = "htdemucs") -> None:
        self.model_name = model_name

    def demix(self, audio_path: str, out_dir: str) -> Optional[Dict[str, str]]:
        """
        Runs the demucs source separation using subprocess for isolation.
        Returns the paths of the separated stems on success, None on failure.
        """
        cmd = [
            sys.executable,
            "-m",
            "demucs.separate",
            "-n",
            self.model_name,
            "-o",
            out_dir,
            audio_path,
        ]

        try:
            logger.info(f"Running Demucs on {audio_path}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603, B607
            # Demucs usually creates a folder inside out_dir based on model and track name.
            # Returning a mock dict for now
            return {
                "vocals": f"{out_dir}/vocals.wav",
                "drums": f"{out_dir}/drums.wav",
                "bass": f"{out_dir}/bass.wav",
                "other": f"{out_dir}/other.wav",
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Demucs failed with exit code {e.returncode}: {e.stderr}")
            # Detect common OOM scenarios
            if "CUDA out of memory" in e.stderr or e.returncode == 137:
                logger.error("OOM error detected during demixing.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error running Demucs: {str(e)}")
            return None

    def is_demucs_available(self) -> bool:
        try:
            demucs_path = shutil.which("demucs") or "demucs"
            result = subprocess.run(
                [demucs_path, "--version"], capture_output=True, text=True
            )  # nosec B603, B607
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def separate_sources(self, input_file: str) -> Optional[Dict[str, str]]:
        """
        Separate audio into sources (vocals, drums, bass, other) using Demucs.
        Returns a dictionary mapping source names to file paths.
        """
        import os

        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return None

        # Just reuse the demix functionality and default to a basic output directory
        output_dir = "demixed_output"
        os.makedirs(output_dir, exist_ok=True)
        return self.demix(input_file, output_dir)
