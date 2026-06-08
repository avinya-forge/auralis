import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore

try:
    import speechbrain  # type: ignore
    from speechbrain.inference.speaker import EncoderClassifier  # type: ignore
except ImportError:
    speechbrain = None  # type: ignore


class VocalistAnalyzer:
    """
    Analyzes vocal stems for characteristics and identity embeddings.
    """

    def __init__(self, model_source: str = "speechbrain/spkrec-ecapa-voxceleb"):
        self.model_source = model_source
        self.classifier = None
        self._load_model()

    def _load_model(self) -> None:
        if speechbrain is not None:
            try:
                self.classifier = EncoderClassifier.from_hparams(
                    source=self.model_source, savedir="resources/models/spkrec-ecapa-voxceleb"
                )
            except Exception as e:
                logger.error(f"Failed to load SpeechBrain model: {e}")
        else:
            logger.warning("SpeechBrain not installed. VocalistAnalyzer will run in mock mode.")

    def extract_vocal_stem(self, stems: Dict[str, str]) -> Optional[str]:
        """
        Extract the path to the vocal stem from demixer output.
        """
        vocal_path = stems.get("vocals")
        if not vocal_path:
            logger.error("Vocal stem not found in demixer output.")
            return None

        if not os.path.exists(vocal_path):
            logger.error(f"Vocal stem file does not exist: {vocal_path}")
            return None

        return vocal_path

    def generate_dvector(self, vocal_stem_path: str) -> Optional["np.ndarray"]:
        """
        Generate d-vector (speaker embedding) for a given vocal stem.
        Returns a numpy array representing the embedding (100% privacy preserving, no raw audio stored).
        """
        if not os.path.exists(vocal_stem_path):
            logger.error(f"Vocal stem not found: {vocal_stem_path}")
            return None

        if self.classifier is None:
            # Mock mode or failure to load
            logger.info("Mock generating d-vector.")
            if np is not None:
                return np.random.randn(192).astype(np.float32)
            return None

        try:
            # Load and encode
            signal = self.classifier.load_audio(vocal_stem_path)
            embeddings = self.classifier.encode_batch(signal)

            # Remove batch dimension
            embedding_np = embeddings.squeeze().cpu().numpy()
            return embedding_np
        except Exception as e:
            logger.error(f"Failed to generate d-vector: {e}")
            return None
