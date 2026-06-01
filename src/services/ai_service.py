"""
Auralis - AI Service Module
"""

import logging
from typing import Any, Dict, List

from src.services.ai.config import ai_config
from src.services.ai.inference_engine import NeuralInferenceEngine
from src.services.ai.raga_classifier import RagaClassifier

logger = logging.getLogger(__name__)


class AIService:
    """
    Central service for AI-powered features.
    """

    def __init__(self) -> None:
        """Initialize the AI Service."""
        self.config = ai_config
        self.engine = NeuralInferenceEngine()
        self.raga_classifier = RagaClassifier()

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

    def analyze_raga(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze audio to identify Raga.

        Args:
            file_path (str): Path to audio file.

        Returns:
            Dict[str, Any]: Raga classification result.
        """
        return self.raga_classifier.classify(file_path)

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
        return self.engine.run_classification(
            file_path=file_path,
            model_name=model_name,
            task=task
        )

    def clear_resources(self) -> None:
        """Free up GPU/RAM resources."""
        self.engine.clear_resources()
