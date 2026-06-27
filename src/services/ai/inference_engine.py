"""
Auralis - Neural Inference Engine
Generic utility for model execution and resource management.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from src.services.ai.config import ai_config
from src.services.ai.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class NeuralInferenceEngine:
    """
    Handles generic neural inference tasks with standardized error handling and simulation support.
    """

    def __init__(self) -> None:
        self.loader = ModelLoader()

    def run_classification(
        self,
        file_path: str,
        model_name: str,
        task: str,
        candidate_labels: Optional[List[str]] = None,
        label_prefix: str = "",
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Executes a classification task (standard or zero-shot)."""
        if ai_config.simulation_mode:
            logger.info(f"Simulation Mode: Mocking inference for {model_name}")
            return [{"label": "simulation", "score": 0.99}]

        if not os.path.exists(file_path):
            logger.error(f"Inference failed: File not found {file_path}")
            return []

        try:
            pipe = self.loader.load_model(model_name, task)
            if pipe is None:
                return []

            # Determine results
            raw_result = (
                pipe(file_path, candidate_labels=candidate_labels)
                if candidate_labels
                else pipe(file_path)
            )
            return self._process_results(raw_result, label_prefix, top_k)

        except Exception as e:
            logger.error(f"Neural inference failed for {model_name} on {file_path}: {str(e)}")
            return []

    def _process_results(self, result: Any, label_prefix: str, top_k: int) -> List[Dict[str, Any]]:
        """Normalizes and filters inference results."""
        if not result:
            return []

        if not isinstance(result, list):
            result = [result]

        processed_results = []
        for item in result[:top_k]:
            label = item.get("label", "Unknown")
            if label_prefix and label.startswith(label_prefix):
                label = label.replace(label_prefix, "")

            processed_results.append({"label": label, "score": float(item.get("score", 0.0))})

        return processed_results

    def clear_resources(self) -> None:
        """Free memory/GPU resources."""
        self.loader.clear_cache()
