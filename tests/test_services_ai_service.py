import os
import sys
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

# Ensure we can import src
sys.path.append(os.getcwd())

from src.services.ai.config import ai_config  # noqa: F401, E402
from src.services.ai.model_loader import ModelLoader  # noqa: E402
from src.services.ai_service import AIService  # noqa: E402


class TestAIService(unittest.TestCase):

    def setUp(self):
        self.service = AIService()

    @patch("src.services.ai.config.AIConfig.simulation_mode", new_callable=PropertyMock)
    def test_simulation_mode_analysis(self, mock_sim_mode):
        mock_sim_mode.return_value = True

        result = self.service.analyze_audio_classification("dummy.mp3")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "simulation")

    @patch("src.services.ai.config.AIConfig.simulation_mode", new_callable=PropertyMock)
    @patch("os.path.exists")
    @patch("src.services.ai.model_loader.ModelLoader.load_model")
    def test_real_analysis(self, mock_load, mock_exists, mock_sim_mode):
        mock_sim_mode.return_value = False
        mock_exists.return_value = True

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{"label": "rock", "score": 0.95}]
        mock_load.return_value = mock_pipeline

        result = self.service.analyze_audio_classification("test.mp3")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "rock")
        mock_load.assert_called_once()

    @patch("src.services.ai.config.AIConfig.enabled", new_callable=PropertyMock)
    @patch("src.services.ai.config.AIConfig.device", new_callable=PropertyMock)
    def test_check_health(self, mock_device, mock_enabled):
        mock_enabled.return_value = True
        mock_device.return_value = "cpu"

        # Patch torch in sys.modules
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.0.0"
        mock_torch.cuda.is_available.return_value = False

        with patch.dict(sys.modules, {"torch": mock_torch}):
            health = self.service.check_health()
            self.assertTrue(health["torch_available"])
            self.assertFalse(health["gpu_available"])


class TestModelLoader(unittest.TestCase):

    def tearDown(self):
        ModelLoader.clear_cache()

    @patch("src.services.ai.config.AIConfig.simulation_mode", new_callable=PropertyMock)
    def test_loader_simulation(self, mock_sim_mode):
        mock_sim_mode.return_value = True

        pipe = ModelLoader.load_model("test-model", "audio-classification")
        result = pipe("audio")
        self.assertEqual(result[0]["label"], "simulation")

    @patch("src.services.ai.config.AIConfig.simulation_mode", new_callable=PropertyMock)
    @patch("src.services.ai.config.AIConfig.enabled", new_callable=PropertyMock)
    @patch("src.services.ai.config.AIConfig.device", new_callable=PropertyMock)
    @patch("src.services.ai.config.AIConfig.model_cache_dir", new_callable=PropertyMock)
    def test_loader_real(self, mock_cache, mock_device, mock_enabled, mock_sim_mode):
        mock_sim_mode.return_value = False
        mock_enabled.return_value = True
        mock_device.return_value = "cpu"
        mock_cache.return_value = "/tmp/cache"

        mock_pipeline = MagicMock()

        # We need to mock transformers and torch
        mock_transformers = MagicMock()
        mock_transformers.pipeline = MagicMock(return_value=mock_pipeline)

        with patch.dict(sys.modules, {"torch": MagicMock(), "transformers": mock_transformers}):
            with patch("os.path.exists", return_value=True):
                pipe = ModelLoader.load_model("test-model", "audio-classification")

                self.assertEqual(pipe, mock_pipeline)
                mock_transformers.pipeline.assert_called_with(
                    task="audio-classification",
                    model="test-model",
                    device=-1,
                    torch_dtype=None,
                    model_kwargs={"cache_dir": "/tmp/cache"},
                )

    @patch("src.services.ai.model_loader.gc")
    def test_unload_model(self, mock_gc):
        # Setup mock cache
        mock_pipe = MagicMock()
        ModelLoader._instances["test-model"] = mock_pipe

        with patch.dict(sys.modules, {"torch": MagicMock()}):
            ModelLoader.unload_model("test-model")

        self.assertNotIn("test-model", ModelLoader._instances)
        mock_gc.collect.assert_called()
