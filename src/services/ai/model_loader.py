"""
Auralis - Model Loader Module
"""

import gc
import logging
from typing import Any, Dict, Union

from src.services.ai.config import ai_config

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Handles lazy loading and lifecycle of AI models.
    """

    _instances: Dict[str, Any] = {}

    @classmethod
    def load_model(cls, model_name: str, task: str) -> Any:
        """
        Load a model by name and task.

        Args:
            model_name (str): Hugging Face model ID.
            task (str): Task type (e.g., "audio-classification").

        Returns:
            Any: The loaded model pipeline or object.
        """
        if model_name in cls._instances:
            return cls._instances[model_name]

        if ai_config.simulation_mode or not ai_config.enabled:
            logger.info(f"Simulating load of model {model_name}")
            return cls._create_mock_model(model_name)

        try:
            import torch
            from transformers import pipeline

            logger.info(f"Loading model {model_name} on {ai_config.device}")

            # Map device string to pipeline compatible format
            # device=-1 for CPU, device=0 for CUDA:0, device="mps" for MPS
            device: Union[int, str] = -1
            if ai_config.device == "cuda":
                device = 0  # Use first GPU
            elif ai_config.device == "mps":
                device = "mps"

            # For CPU, device remains -1

            # Use pipeline for simplicity
            pipe = pipeline(
                task=task,
                model=model_name,
                device=device,
                torch_dtype=(
                    torch.float16 if ai_config.use_fp16 and ai_config.device != "cpu" else None
                ),
            )

            cls._instances[model_name] = pipe
            return pipe

        except ImportError:
            logger.error("Transformers or Torch not installed.")
            return cls._create_mock_model(model_name)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            return cls._create_mock_model(model_name)

    @classmethod
    def unload_model(cls, model_name: str) -> None:
        """
        Unload a specific model from memory.

        Args:
            model_name (str): The name of the model to unload.
        """
        if model_name in cls._instances:
            logger.info(f"Unloading model {model_name}")
            del cls._instances[model_name]
            cls._clear_gpu_cache()

    @staticmethod
    def _create_mock_model(model_name: str) -> Any:
        """Create a mock model for simulation or error fallback."""

        class MockPipeline:
            def __call__(self, *args, **kwargs) -> Any:
                # Return generic structure matching common audio classification outputs
                return [{"label": "simulation", "score": 0.99}]

        return MockPipeline()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all loaded models from memory."""
        cls._instances.clear()
        cls._clear_gpu_cache()

    @staticmethod
    def _clear_gpu_cache() -> None:
        """Helper to clear GPU memory."""
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                torch.backends.mps.empty_cache()
        except ImportError:
            pass
