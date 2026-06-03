import gc
import logging
from typing import Any, Optional

import torch

from src.services.ai.config import ai_config


class ModelLoader:
    _instances: dict[str, Any] = {}

    @classmethod
    def load_model(cls, model_name: str, task: Optional[str] = None) -> Any:
        if ai_config.simulation_mode:
            return lambda *a, **k: [{"label": "simulation", "score": 0.99}]
        if model_name in cls._instances:
            return cls._instances[model_name]
        try:
            import transformers

            pipe = transformers.pipeline(
                task=task,
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                model_kwargs={"cache_dir": ai_config.model_cache_dir},
            )
            cls._instances[model_name] = pipe
            return pipe
        except ImportError:
            logging.error("Transformers not installed. Cannot load real model.")
            raise

    @classmethod
    def unload_model(cls, model_name: str) -> None:
        if model_name in cls._instances:
            del cls._instances[model_name]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    @classmethod
    def clear_cache(cls) -> None:
        cls._instances.clear()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


loader_instance = ModelLoader()
