"""
Audio Fingerprint Service

This module provides functionality to generate audio fingerprints using AcoustID
and identify duplicate audio files.
"""

import logging
from typing import Dict, List, Optional, Tuple, cast

# Lazy imports
try:
    import acoustid  # type: ignore
    HAS_ACOUSTID = True
except ImportError:
    HAS_ACOUSTID = False

from src.utils.dependency_checker import DependencyChecker

logger = logging.getLogger(__name__)


class AudioFingerprinter:
    """
    Generates audio fingerprints using AcoustID.
    """

    def __init__(self) -> None:
        """Initialize the AudioFingerprinter."""
        self.has_dependencies = self._check_dependencies()

    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        if not HAS_ACOUSTID:
            logger.warning("acoustid module not found. Audio fingerprinting disabled.")
            return False

        # Check for fpcalc
        fpcalc_path = DependencyChecker.check_system_tool("fpcalc")
        if not fpcalc_path:
            logger.warning("fpcalc not found in PATH. Audio fingerprinting disabled.")
            return False

        return True

    def generate_fingerprint(self, file_path: str) -> Optional[Tuple[float, str]]:
        """
        Generate a fingerprint for an audio file.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Optional[Tuple[float, str]]: A tuple containing (duration, fingerprint),
                                         or None if generation failed.
        """
        if not self.has_dependencies:
            return None

        try:
            # acoustid.fingerprint_file returns (duration, fingerprint)
            return cast(Tuple[float, str], acoustid.fingerprint_file(file_path))
        except Exception as e:
            logger.error(f"Error generating fingerprint for {file_path}: {e}")
            return None


class DuplicateFinder:
    """
    Identifies duplicate audio files based on fingerprints.
    """

    def __init__(self) -> None:
        """Initialize the DuplicateFinder."""
        self.fingerprinter = AudioFingerprinter()

    def find_duplicates(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Find duplicate files in a list of file paths.

        Args:
            file_paths (List[str]): List of file paths to check.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are fingerprints (or hashes)
                                  and values are lists of file paths that share that fingerprint.
                                  Only fingerprints with > 1 file are returned.
        """
        if not self.fingerprinter.has_dependencies:
            logger.warning("Dependencies missing, cannot find duplicates.")
            return {}

        fingerprints: Dict[str, List[str]] = {}

        for file_path in file_paths:
            result = self.fingerprinter.generate_fingerprint(file_path)
            if result:
                duration, fingerprint = result
                # We use the fingerprint string itself as the key.
                if fingerprint in fingerprints:
                    fingerprints[fingerprint].append(file_path)
                else:
                    fingerprints[fingerprint] = [file_path]

        # Filter out unique files
        duplicates = {fp: paths for fp, paths in fingerprints.items() if len(paths) > 1}
        return duplicates
