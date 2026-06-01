"""
Auralis - Raga Classifier Module
"""

import logging
from typing import Dict, Union

from src.services.ai.inference_engine import NeuralInferenceEngine
from src.services.ai.raga_constants import COMMON_RAGAS

logger = logging.getLogger(__name__)


class RagaClassifier:
    """
    Classifies audio into Ragas using Zero-Shot Audio Classification (CLAP).
    """

    MODEL_NAME = "laion/clap-htsat-unfused"
    LABEL_PREFIX = "Indian Classical Raga "

    def __init__(self) -> None:
        """Initialize the Raga Classifier."""
        self.engine = NeuralInferenceEngine()
        self.labels = COMMON_RAGAS

    def classify(self, file_path: str) -> Dict[str, Union[str, float]]:
        """
        Classify the audio file to identify the Raga.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            Dict[str, Union[str, float]]: Dictionary containing 'label' and 'score'.
        """
        candidate_labels = [f"{self.LABEL_PREFIX}{raga}" for raga in self.labels]

        results = self.engine.run_classification(
            file_path=file_path,
            model_name=self.MODEL_NAME,
            task="zero-shot-audio-classification",
            candidate_labels=candidate_labels,
            label_prefix=self.LABEL_PREFIX,
            top_k=1,
        )

        if results:
            return results[0]

        return {"label": "Unknown", "score": 0.0}
