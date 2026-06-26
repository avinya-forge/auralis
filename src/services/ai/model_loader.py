import gc
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from transformers import pipeline
except ImportError:
    pipeline = None  # type: ignore


class ModelLoader:
    """
    Handles lazy loading and caching of Hugging Face models.
    Ensures heavy models are only kept in memory when active.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def get_model(self, model_name: str, task: str = "audio-classification") -> Optional[Any]:
        """
        Retrieves a model from cache or loads it via transformers pipeline.
        """
        if pipeline is None:
            logger.warning("transformers library not installed. Cannot load models.")
            return None

        cache_key = f"{task}:{model_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            logger.info(f"Loading AI model: {model_name} for task: {task}")
            # Use CPU by default for stability in shared environments,
            # unless CUDA is explicitly requested or available.
            model = pipeline(task, model=model_name)  # type: ignore
            self._cache[cache_key] = model
            return model
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return None

    def clear_cache(self) -> None:
        """Flushes the model cache to free up memory."""
        self._cache.clear()
        self._clear_gpu_cache()
        logger.info("AI model cache cleared.")

    @staticmethod
    def _clear_gpu_cache() -> None:
        """Helper to clear GPU memory."""
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Safely check for MPS (Apple Silicon) to avoid mypy attribute errors
            backends = getattr(torch, "backends", None)
            if backends:
                mps = getattr(backends, "mps", None)
                if mps and getattr(mps, "is_available", lambda: False)():
                    empty_cache_fn = getattr(mps, "empty_cache", None)
                    if empty_cache_fn:
                        empty_cache_fn()
        except (ImportError, AttributeError):
            pass
