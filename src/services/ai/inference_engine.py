"""
Auralis - Neural Inference Engine
Generic utility for model execution and resource management.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from src.services.ai.config import ai_config
from src.services.ai.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class NeuralInferenceEngine:
    """
    Handles generic neural inference tasks with standardized error handling and simulation support.
    """

    def __init__(self) -> None:
        self.loader = ModelLoader

    def run_classification(
        self,
        file_path: str,
        model_name: str,
        task: str,
        candidate_labels: Optional[List[str]] = None,
        label_prefix: str = "",
        top_k: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Executes a classification task (standard or zero-shot).

        Args:
            file_path: Path to the audio file.
            model_name: Hugging Face model ID.
            task: Task type (e.g., 'audio-classification', 'zero-shot-audio-classification').
            candidate_labels: Labels for zero-shot classification.
            label_prefix: Prefix to remove from returned labels.
            top_k: Number of top results to return.

        Returns:
            List of results [{'label': str, 'score': float}].
        """
        if ai_config.simulation_mode:
            logger.info(f"Simulation Mode: Mocking inference for {model_name}")
            return [{"label": "simulation", "score": 0.99}]

        if not os.path.exists(file_path):
            logger.error(f"Inference failed: File not found {file_path}")
            return []

        try:
            pipe = self.loader.load_model(model_name, task)

            if candidate_labels:
                # Zero-shot path
                result = pipe(file_path, candidate_labels=candidate_labels)
            else:
                # Standard path
                result = pipe(file_path)

            if not result:
                return []

            if not isinstance(result, list):
                result = [result]

            # Process and clean labels
            processed_results = []
            for item in result[:top_k]:
                label = item.get("label", "Unknown")
                if label_prefix and label.startswith(label_prefix):
                    label = label.replace(label_prefix, "")

                processed_results.append({
                    "label": label,
                    "score": float(item.get("score", 0.0))
                })

            return processed_results

        except Exception as e:
            logger.error(f"Neural inference failed for {model_name} on {file_path}: {str(e)}")
            return []

    def clear_resources(self) -> None:
        """Free memory/GPU resources."""
        self.loader.clear_cache()
