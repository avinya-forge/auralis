import gc
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Handles lazy loading and caching of Hugging Face models.
    Ensures heavy models are only kept in memory when active.
    """

    _instances: Dict[str, Any] = {}

    def __init__(self) -> None:
        pass

    @classmethod
    def load_model(cls, model_name: str, task: str = "audio-classification") -> Optional[Any]:
        """
        Retrieves a model from cache or loads it via transformers pipeline.
        Legacy name for backward compatibility with tests.
        """
        return cls.get_model(model_name, task)

    @classmethod
    def get_model(cls, model_name: str, task: str = "audio-classification") -> Optional[Any]:
        """
        Retrieves a model from cache or loads it via transformers pipeline.
        """
        from src.services.ai.config import ai_config

        if ai_config.simulation_mode:
            logger.info(f"Simulation Mode: Returning mock pipeline for {model_name}")
            return lambda x, **kwargs: [{"label": "simulation", "score": 0.99}]

        cache_key = f"{task}:{model_name}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        return cls._load_and_cache(model_name, task, cache_key)

    @classmethod
    def _load_and_cache(cls, model_name: str, task: str, cache_key: str) -> Optional[Any]:
        """Internal helper to load model and store in cache."""
        from src.services.ai.config import ai_config

        try:
            from transformers import pipeline
        except ImportError:
            logger.warning("transformers library not installed. Cannot load models.")
            return None

        try:
            logger.info(f"Loading AI model: {model_name} for task: {task}")
            device = cls._get_device()

            # Determine dtype
            torch_dtype = None
            try:
                import torch

                if ai_config.use_fp16 and ai_config.device != "cpu":
                    torch_dtype = torch.float16
            except ImportError:
                pass

            # Load pipeline
            # Use type: ignore for pipeline call to satisfy mypy overloads
            pipe = pipeline(
                task=task,
                model=model_name,
                device=device,
                torch_dtype=torch_dtype,
                model_kwargs=(
                    {"cache_dir": ai_config.model_cache_dir} if ai_config.model_cache_dir else {}
                ),
            )  # type: ignore
            cls._instances[cache_key] = pipe
            return pipe
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return None

    @staticmethod
    def _get_device() -> int:
        """Determines the best available device for inference."""
        from src.services.ai.config import ai_config

        device = -1  # Default to CPU
        try:
            import torch

            if ai_config.device == "cuda" and torch.cuda.is_available():
                device = 0
            elif (
                ai_config.device == "mps"
                and hasattr(torch.backends, "mps")
                and torch.backends.mps.is_available()
            ):
                device = 0
        except (ImportError, AttributeError):
            pass
        return device

    @classmethod
    def unload_model(cls, model_name: str, task: str = "audio-classification") -> None:
        """Removes a specific model from memory."""
        cache_key = f"{task}:{model_name}"
        if cache_key in cls._instances:
            del cls._instances[cache_key]
            cls._clear_gpu_cache()
            logger.info(f"Unloaded model: {model_name}")

    @classmethod
    def clear_cache(cls) -> None:
        """Flushes the model cache to free up memory."""
        cls._instances.clear()
        cls._clear_gpu_cache()
        logger.info("AI model cache cleared.")

    @staticmethod
    def _clear_gpu_cache() -> None:
        """Helper to clear GPU memory."""
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            backends = getattr(torch, "backends", None)
            if backends:
                mps = getattr(backends, "mps", None)
                if mps and getattr(mps, "is_available", lambda: False)():
                    empty_cache_fn = getattr(mps, "empty_cache", None)
                    if empty_cache_fn:
                        empty_cache_fn()
        except (ImportError, AttributeError):
            pass
