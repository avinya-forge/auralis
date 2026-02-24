"""
Auralis - AI Setup Script

This script checks for and installs dependencies required for Neural Audio features.
"""

import logging
import sys

from src.utils.dependency_checker import DependencyChecker

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Checking AI dependencies...")
    checker = DependencyChecker()
    report = checker.check_all()

    ai_deps = report.get("ai", {})
    missing_deps = [pkg for pkg, installed in ai_deps.items() if not installed]

    if not missing_deps:
        logger.info("All AI dependencies are installed!")

        # Check torch device availability
        try:
            import torch

            if torch.cuda.is_available():
                logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                logger.info("MPS (Metal Performance Shaders) is available")
            else:
                logger.info("Running on CPU (No GPU acceleration detected)")
        except ImportError:
            pass

        return 0

    logger.warning(f"Missing AI dependencies: {', '.join(missing_deps)}")

    # Check for user confirmation
    if "--yes" not in sys.argv and "-y" not in sys.argv:
        print("\nThe following packages will be installed:")
        print(checker.get_install_instructions(missing_deps, []))
        response = input("\nDo you want to proceed? [y/N]: ").lower()
        if response != "y":
            logger.info("Installation cancelled.")
            return 1

    logger.info("Installing dependencies...")
    # Map for pip install
    pip_packages = []
    pip_map = {
        "sklearn": "scikit-learn",
    }

    for dep in missing_deps:
        pip_packages.append(pip_map.get(dep, dep))

    if checker.install_pip_packages(pip_packages):
        logger.info("Installation successful!")
        return 0
    else:
        logger.error("Installation failed. Please try installing manually.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
