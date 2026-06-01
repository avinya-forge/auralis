"""
Auralis - Model Loader Module
"""

import gc
import logging
import os
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

            device: Union[int, str] = -1
            if ai_config.device == "cuda":
                device = 0
            elif ai_config.device == "mps":
                device = "mps"

            cache_dir = ai_config.model_cache_dir
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)

            pipe = pipeline(
                task=task,
                model=model_name,
                device=device,
                torch_dtype=(
                    torch.float16 if ai_config.use_fp16 and ai_config.device != "cpu" else None
                ),
                model_kwargs={"cache_dir": cache_dir},
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
        """
        if model_name in cls._instances:
            logger.info(f"Unloading model {model_name}")
            del cls._instances[model_name]
            cls._clear_gpu_cache()

    @staticmethod
    def _create_mock_model(model_name: str) -> Any:
        """Create a mock model for simulation or error fallback."""

        class MockPipeline:
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                # Support zero-shot return format if candidate_labels are present
                if "candidate_labels" in kwargs:
                    labels = kwargs["candidate_labels"]
                    return [{"label": label, "score": 1.0 / len(labels)} for label in labels]
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
