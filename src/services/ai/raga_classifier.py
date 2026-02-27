"""
Auralis - Raga Classifier Module
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from src.services.ai.config import ai_config
from src.services.ai.model_loader import ModelLoader
from src.services.ai.raga_constants import COMMON_RAGAS

logger = logging.getLogger(__name__)


class RagaClassifier:
    """
    Classifies audio into Ragas using Zero-Shot Audio Classification (CLAP).
    """

    MODEL_NAME = "laion/clap-htsat-unfused"

    def __init__(self) -> None:
        """Initialize the Raga Classifier."""
        self.loader = ModelLoader
        self.labels = COMMON_RAGAS

    def classify(self, file_path: str) -> Dict[str, Union[str, float]]:
        """
        Classify the audio file to identify the Raga.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Dict[str, Union[str, float]]: Dictionary containing 'label' and 'score'.
        """
        if ai_config.simulation_mode:
            logger.info("Simulation Mode: Returning mock Raga classification.")
            return {"label": "Yaman", "score": 0.85}

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"label": "Unknown", "score": 0.0}

        try:
            # We use the pipeline abstraction if possible, but CLAP might not have a direct
            # "audio-classification" pipeline that supports zero-shot with custom texts easily
            # via the standard pipeline API in all versions.
            # However, for simplicity and consistency with ModelLoader, let's try to use
            # the 'zero-shot-audio-classification' task if available, or fall back to manual loading.

            # Note: 'zero-shot-audio-classification' is supported by transformers >= 4.27
            pipe = self.loader.load_model(self.MODEL_NAME, "zero-shot-audio-classification")

            # pipe(audio, candidate_labels=["raga 1", "raga 2", ...])
            # We prefix labels to give context to the model
            candidate_labels = [f"Indian Classical Raga {raga}" for raga in self.labels]

            result = pipe(file_path, candidate_labels=candidate_labels)

            # Result is usually a list of dicts sorted by score
            # [{'score': 0.9, 'label': 'Indian Classical Raga Yaman'}, ...]
            if result and isinstance(result, list):
                top_result = result[0]
                label = top_result["label"].replace("Indian Classical Raga ", "")
                score = top_result["score"]
                return {"label": label, "score": score}

            return {"label": "Unknown", "score": 0.0}

        except Exception as e:
            logger.error(f"Raga classification failed for {file_path}: {str(e)}")
            # Fallback for simulation/testing if model load fails but we want to proceed
            if ai_config.simulation_mode:
                 return {"label": "Yaman", "score": 0.85}
            return {"label": "Unknown", "score": 0.0}
