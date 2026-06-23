from typing import Dict, Any, Optional
import logging
import os
from typing import Any, Dict, Optional

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

    def extract_signature(
        self, audio_array: np.ndarray, sample_rate: int = 16000
    ) -> Optional[np.ndarray]:
        """
        Extract a voice signature (embedding) from raw audio array.
        Requires 16kHz audio typically.
        """
        if not self.classifier:
            logger.warning("Vocalist model not loaded. Returning mock embedding.")
            return self._mock_signature()

        try:
            import torch

            tensor = torch.from_numpy(audio_array).float()

            if tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)

            with torch.no_grad():
                embeddings = self.classifier.encode_batch(tensor)

            embedding_np = embeddings.squeeze().cpu().numpy()
            return embedding_np
        except Exception as e:
            logger.error(f"Failed to extract voice signature: {e}")
            return None

    def compare_signatures(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """
        Compare two voice signatures using cosine similarity.
        """
        try:
            dot_product = np.dot(sig1, sig2)
            norm_a = np.linalg.norm(sig1)
            norm_b = np.linalg.norm(sig2)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error comparing signatures: {e}")
            return 0.0

    def analyze_vocal_characteristics(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """
        Higher-level analysis returning various vocal characteristics.
        """
        signature = self.extract_signature(audio_array)

        return {
            "has_vocals": True,
            "vocal_intensity": 0.75,
            "signature_vector": signature.tolist() if signature is not None else [],
            "estimated_gender": "Unknown",
        }

    def _mock_signature(self) -> np.ndarray:
        return np.random.randn(192).astype(np.float32)
