import os
from typing import Any, Dict, List, Optional

from src.services.ai.config import ai_config
from src.services.ai.model_loader import ModelLoader


class NeuralInferenceEngine:
    """Handles generic neural inference tasks."""

    def __init__(self) -> None:
        self.loader = ModelLoader

    def _process_result(self, result: Any, label_prefix: str, top_k: int) -> List[Dict[str, Any]]:
        """Clean and process inference results."""
        if not result:
            return []
        if not isinstance(result, list):
            result = [result]

        processed = []
        for item in result[:top_k]:
            label = item.get("label", "Unknown")
            if label_prefix and label.startswith(label_prefix):
                label = label.replace(label_prefix, "")
            processed.append({"label": label, "score": float(item.get("score", 0.0))})
        return processed

    def run_classification(
        self,
        file_path: str,
        model_name: str,
        task: str,
        candidate_labels: Optional[List[str]] = None,
        label_prefix: str = "",
        top_k: int = 1,
    ) -> List[Dict[str, Any]]:
        """Run classification."""
        if ai_config.simulation_mode:
            return [{"label": "simulation", "score": 0.99}]
        if not os.path.exists(file_path):
            return []
        try:
            pipe = self.loader.load_model(model_name, task)
            if not pipe:
                return []
            res = (
                pipe(file_path, candidate_labels=candidate_labels)
                if candidate_labels
                else pipe(file_path)
            )
            return self._process_result(res, label_prefix, top_k)
        except Exception:
            return []

    def clear_resources(self) -> None:
        """Clear."""
        self.loader.clear_cache()
