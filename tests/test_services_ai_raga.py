"""
Tests for Raga Classifier
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from src.services.ai.raga_classifier import RagaClassifier


class TestRagaClassifier(unittest.TestCase):
    def setUp(self):
        # Patch transformers and torch locally
        self.modules_patcher = patch.dict(
            sys.modules, {"transformers": MagicMock(), "torch": MagicMock()}
        )
        self.modules_patcher.start()
        self.classifier = RagaClassifier()

    def tearDown(self):
        self.modules_patcher.stop()

    @patch("src.services.ai.inference_engine.ai_config")
    def test_classify_simulation_mode(self, mock_config):
        """Test classification in simulation mode."""
        mock_config.simulation_mode = True

        result = self.classifier.classify("dummy_path.mp3")

        self.assertEqual(result["label"], "simulation")
        self.assertEqual(result["score"], 0.99)

    @patch("src.services.ai.inference_engine.ai_config")
    @patch("src.services.ai.model_loader.ModelLoader.load_model")
    @patch("os.path.exists")
    def test_classify_real_mode(self, mock_exists, mock_load_model, mock_config):
        """Test classification in real mode (mocked model)."""
        mock_config.simulation_mode = False
        mock_config.enabled = True
        mock_exists.return_value = True

        # Mock pipeline
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "This is an audio snippet of the Indian Classical Raga Bhairav", "score": 0.95}]
        mock_load_model.return_value = mock_pipe

        result = self.classifier.classify("real_song.mp3")

        self.assertEqual(result["label"], "Bhairav")
        self.assertEqual(result["score"], 0.95)

        # Verify call arguments
        mock_pipe.assert_called_once()
        args, kwargs = mock_pipe.call_args
        self.assertEqual(args[0], "real_song.mp3")
        self.assertIn("candidate_labels", kwargs)

    @patch("src.services.ai.inference_engine.ai_config")
    @patch("os.path.exists")
    def test_classify_file_not_found(self, mock_exists, mock_config):
        """Test classification when file is missing."""
        mock_config.simulation_mode = False
        mock_exists.return_value = False

        result = self.classifier.classify("missing.mp3")

        self.assertEqual(result["label"], "Unknown")
        self.assertEqual(result["score"], 0.0)

    @patch("src.services.ai.inference_engine.ai_config")
    @patch("src.services.ai.model_loader.ModelLoader.load_model")
    @patch("os.path.exists")
    def test_classify_error_handling(self, mock_exists, mock_load_model, mock_config):
        """Test error handling during classification."""
        mock_config.simulation_mode = False
        mock_config.enabled = True
        mock_exists.return_value = True

        mock_load_model.side_effect = Exception("Model load failed")

        result = self.classifier.classify("broken.mp3")

        self.assertEqual(result["label"], "Unknown")
        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
