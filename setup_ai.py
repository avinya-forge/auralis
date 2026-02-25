"""
Auralis - AI Setup Script

This script checks for and installs dependencies required for Neural Audio features,
handling platform-specific requirements (CUDA, MPS, CPU).
"""

import argparse
import logging
import platform
import subprocess
import sys
from typing import List, Optional

from src.utils.dependency_checker import DependencyChecker

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def install_packages(packages: List[str], index_url: Optional[str] = None) -> bool:
    """
    Install packages using pip, optionally with a specific index URL.

    Args:
        packages (List[str]): List of packages to install.
        index_url (str, optional): Custom PyPI index URL.

    Returns:
        bool: True if installation succeeded.
    """
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    if index_url:
        cmd.extend(["--index-url", index_url])

    logger.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def get_torch_index_url(args: argparse.Namespace) -> Optional[str]:
    """
    Determine the correct PyTorch index URL based on platform and arguments.
    """
    # CUDA 12.1 (Stable as of late 2023/2024)
    cuda_index = "https://download.pytorch.org/whl/cu121"
    # CPU only
    cpu_index = "https://download.pytorch.org/whl/cpu"

    system = platform.system()
    index_url: Optional[str] = None

    if args.cpu:
        # Force CPU
        if system == "Linux" or system == "Windows":
            index_url = cpu_index
        # Mac doesn't use index-url for CPU (it's same package)
    elif args.gpu:
        # Force GPU (CUDA)
        if system == "Linux" or system == "Windows":
            index_url = cuda_index
        elif system == "Darwin":
            logger.warning("CUDA is not available on macOS. Using standard install (MPS capable).")
    else:
        # Auto-detect: Default to CUDA on Linux/Windows as users running this script
        # likely want GPU support.
        if system == "Linux" or system == "Windows":
            index_url = cuda_index
        # Mac uses default PyPI

    return index_url


def report_status(report: dict) -> None:
    """Log the current installation status."""
    logger.info("All AI dependencies are installed!")
    torch_info = report.get("torch", {})
    if torch_info.get("cuda"):
        logger.info(f"CUDA is available (Torch {torch_info.get('version')})")
    elif torch_info.get("mps"):
        logger.info(f"MPS is available (Torch {torch_info.get('version')})")
    else:
        logger.info(f"Running on CPU (Torch {torch_info.get('version')})")


def get_confirmation(args: argparse.Namespace, missing_deps: List[str]) -> bool:
    """Ask user for confirmation unless --yes is specified."""
    if args.yes:
        return True

    print(f"\nThe following packages will be installed/updated: {', '.join(missing_deps)}")
    if args.cpu:
        print("Target: CPU (No GPU acceleration)")
    elif args.gpu:
        print("Target: CUDA (GPU acceleration)")
    else:
        print(f"Target: Auto-detect ({platform.system()})")

    response = input("\nDo you want to proceed? [y/N]: ").lower()
    return response == "y"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Auralis AI dependencies.")
    parser.add_argument("--cpu", action="store_true", help="Force CPU-only installation")
    parser.add_argument("--gpu", action="store_true", help="Attempt GPU installation (CUDA)")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force re-installation even if present"
    )
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    logger.info("Checking AI dependencies...")
    checker = DependencyChecker()
    report = checker.check_ai_dependencies()

    # Determine what needs to be done
    missing_deps = []
    # Core AI deps
    required = ["torch", "torchaudio", "transformers", "scipy", "librosa"]

    for req in required:
        if not report.get(req, {}).get("installed", False) or args.force:
            missing_deps.append(req)

    if not missing_deps and not args.force:
        report_status(report)
        return 0

    if not get_confirmation(args, missing_deps):
        logger.info("Installation cancelled.")
        return 1

    # Installation Logic
    logger.info("Installing dependencies...")
    success = True

    # Separate torch from others because it might need index-url
    torch_pkgs = [p for p in missing_deps if p in ["torch", "torchaudio"]]
    other_pkgs = [p for p in missing_deps if p not in ["torch", "torchaudio"]]

    if torch_pkgs:
        index_url = get_torch_index_url(args)
        logger.info(f"Installing PyTorch packages: {', '.join(torch_pkgs)}")
        if not install_packages(torch_pkgs, index_url):
            success = False

    if other_pkgs and success:
        logger.info(f"Installing other packages: {', '.join(other_pkgs)}")
        if not install_packages(other_pkgs):
            success = False

    if success:
        logger.info("Installation successful!")
        return 0
    else:
        logger.error("Installation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
