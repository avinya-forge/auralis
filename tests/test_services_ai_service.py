"""
Tests for AI Service and related components.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from src.services.ai.config import AIConfig
from src.services.ai.model_loader import ModelLoader
from src.services.ai_service import AIService


class TestAIConfig(unittest.TestCase):
    def setUp(self):
        self.config_patcher = patch("src.services.ai.config.config")
        self.mock_config = self.config_patcher.start()

    def tearDown(self):
        self.config_patcher.stop()

    def test_defaults(self):
        self.mock_config.get.side_effect = lambda k, d=None: d
        ai_config = AIConfig()
        self.assertTrue(ai_config.enabled)
        self.assertTrue(ai_config.use_fp16)
        self.assertIn("models", ai_config.model_cache_dir)

    def test_device_detection_cuda(self):
        self.mock_config.get.return_value = "auto"

        # Create a mock torch module
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.backends.mps.is_available.return_value = False

        with patch.dict(sys.modules, {"torch": mock_torch}):
            ai_config = AIConfig()
            self.assertEqual(ai_config.device, "cuda")

    def test_device_detection_cpu(self):
        self.mock_config.get.return_value = "auto"

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        # Delete mps from backends to simulate non-Mac or older torch
        del mock_torch.backends.mps

        with patch.dict(sys.modules, {"torch": mock_torch}):
            ai_config = AIConfig()
            self.assertEqual(ai_config.device, "cpu")


class TestModelLoader(unittest.TestCase):
    def setUp(self):
        ModelLoader._instances = {}

    @patch("src.services.ai.model_loader.ai_config")
    def test_load_model_simulation(self, mock_config):
        mock_config.simulation_mode = True
        mock_config.enabled = True

        loader = ModelLoader()
        model = loader.load_model("test-model", "test-task")

        # Check if it returns a mock object (callable)
        result = model("input")
        self.assertEqual(result[0]["label"], "simulation")

    @patch("src.services.ai.model_loader.ai_config")
    def test_load_model_real_mocked(self, mock_config):
        mock_config.simulation_mode = False
        mock_config.enabled = True
        mock_config.device = "cpu"
        mock_config.use_fp16 = False

        mock_torch = MagicMock()
        mock_transformers = MagicMock()
        mock_pipeline = MagicMock()
        mock_transformers.pipeline = mock_pipeline

        mock_pipe_instance = MagicMock()
        mock_pipeline.return_value = mock_pipe_instance

        with patch.dict(sys.modules, {"transformers": mock_transformers, "torch": mock_torch}):
            loader = ModelLoader()
            model = loader.load_model("test-model", "test-task")

            mock_pipeline.assert_called_with(
                task="test-task",
                model="test-model",
                device=-1,
                torch_dtype=None,
            )
            self.assertEqual(model, mock_pipe_instance)

    @patch("src.services.ai.model_loader.gc")
    def test_unload_model(self, mock_gc):
        ModelLoader._instances["test-model"] = "some-object"

        mock_torch = MagicMock()

        with patch.dict(sys.modules, {"torch": mock_torch}):
            ModelLoader.unload_model("test-model")

            self.assertNotIn("test-model", ModelLoader._instances)
            mock_gc.collect.assert_called()


class TestAIService(unittest.TestCase):
    def setUp(self):
        self.service = AIService()

    @patch("src.services.ai.model_loader.ModelLoader.load_model")
    def test_analyze_audio_classification(self, mock_load):
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "rock", "score": 0.9}]
        mock_load.return_value = mock_pipe

        with patch("os.path.exists", return_value=True):
            result = self.service.analyze_audio_classification("path/to/audio.mp3")

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["label"], "rock")
            mock_pipe.assert_called_with("path/to/audio.mp3")
            mock_load.assert_called()

    def test_analyze_audio_file_not_found(self):
        with patch("os.path.exists", return_value=False):
            result = self.service.analyze_audio_classification("nonexistent.mp3")
            self.assertEqual(result, [])

    @patch("src.services.ai_service.ai_config")
    def test_check_health(self, mock_config):
        mock_config.enabled = True
        mock_config.device = "cuda"
        mock_config.simulation_mode = False
        mock_config.model_cache_dir = "/tmp"
        mock_config.use_fp16 = True

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        with patch.dict(sys.modules, {"torch": mock_torch}):
            # Re-instantiate service to ensure it picks up patched config if needed,
            # though here we patched the imported module object used by the instance
            service = AIService()
            health = service.check_health()

            self.assertTrue(health["enabled"])
            self.assertEqual(health["device"], "cuda")
            self.assertTrue(health["torch_available"])
            self.assertTrue(health["gpu_available"])
