"""
Auralis - AI Configuration Module
"""

import logging
import os
from typing import Optional

from src.utils.config import config

logger = logging.getLogger(__name__)


class AIConfig:
    """
    Configuration manager for AI services.
    """

    @property
    def model_cache_dir(self) -> str:
        """Directory to store downloaded models."""
        default_path = os.path.join(os.path.expanduser("~"), ".cache", "auralis", "models")
        return config.get("AI_MODEL_CACHE_DIR", default_path)

    @property
    def device(self) -> str:
        """
        Get the device to run models on.
        Returns: 'cuda', 'mps', or 'cpu'.
        """
        configured_device = config.get("AI_DEVICE", "auto")
        if configured_device != "auto":
            return configured_device

        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
            # specific check for macos mps
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            logger.warning("Torch not installed, defaulting to cpu")

        return "cpu"

    @property
    def use_fp16(self) -> bool:
        """Whether to use half-precision for inference."""
        return config.get("AI_USE_FP16", True)

    @property
    def enabled(self) -> bool:
        """Whether AI features are enabled."""
        return config.get("AI_ENABLED", True)

    @property
    def simulation_mode(self) -> bool:
        """Whether to run in simulation mode (no actual inference)."""
        return config.get("AI_SIMULATION_MODE", False)


# Global instance
ai_config = AIConfig()
