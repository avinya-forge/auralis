"""
Auralis - AI Service Module
"""

import logging
import os
from typing import Any, Dict, List

from src.services.ai.config import ai_config
from src.services.ai.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class AIService:
    """
    Central service for AI-powered features.
    """

    def __init__(self) -> None:
        """Initialize the AI Service."""
        self.config = ai_config
        self.loader = ModelLoader

    def check_health(self) -> Dict[str, Any]:
        """
        Check if AI service is healthy and ready.

        Returns:
            Dict[str, Any]: Health status report.
        """
        health = {
            "enabled": self.config.enabled,
            "device": self.config.device,
            "simulation_mode": self.config.simulation_mode,
            "cache_dir": self.config.model_cache_dir,
            "use_fp16": self.config.use_fp16,
            "torch_available": False,
            "gpu_available": False,
        }

        try:
            import torch  # noqa: F401

            health["torch_available"] = True
            if self.config.device == "cuda":
                health["gpu_available"] = torch.cuda.is_available()
            elif self.config.device == "mps":
                health["gpu_available"] = (
                    hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
                )
        except ImportError:
            pass

        return health

    def analyze_audio_classification(
        self,
        file_path: str,
        model_name: str = "dima806/music_genres_classification",
        task: str = "audio-classification",
    ) -> List[Dict[str, Any]]:
        """
        Analyze audio using a classification model.

        Args:
            file_path (str): Path to audio file.
            model_name (str): Hugging Face model ID. Defaults to a music genre classifier.
            task (str): Task type. Defaults to 'audio-classification'.

        Returns:
            List[Dict[str, Any]]: List of classification results.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []

        try:
            pipe = self.loader.load_model(model_name, task)

            # Pipeline usually accepts path or bytes
            result = pipe(file_path)

            # Result format: [{'label': 'rock', 'score': 0.99}, ...]
            if isinstance(result, list):
                return result  # type: ignore
            return [result]  # type: ignore

        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {str(e)}")
            return []

    def clear_resources(self) -> None:
        """Free up GPU/RAM resources."""
        self.loader.clear_cache()
