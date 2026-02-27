"""
Tests for AI Service Simulation Mode
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.services.ai.config import AIConfig
from src.services.ai_service import AIService


@pytest.fixture
def ai_service():
    return AIService()


def test_simulation_mode_returns_mock_data(ai_service):
    """Test that analyze_audio_classification returns mock data in simulation mode."""
    # Patch the property on the CLASS, not the instance
    with patch.object(AIConfig, "simulation_mode", new_callable=PropertyMock) as mock_sim:
        mock_sim.return_value = True

        # Path doesn't even need to exist
        result = ai_service.analyze_audio_classification("non_existent_file.mp3")

        assert len(result) == 1
        assert result[0]["label"] == "simulation_genre"
        assert result[0]["score"] == 1.0


def test_simulation_mode_no_model_load(ai_service):
    """Test that load_model is NOT called in simulation mode."""
    with patch.object(AIConfig, "simulation_mode", new_callable=PropertyMock) as mock_sim:
        mock_sim.return_value = True

        with patch.object(ai_service.loader, "load_model") as mock_load:
            ai_service.analyze_audio_classification("dummy.mp3")
            mock_load.assert_not_called()


def test_real_mode_calls_model_load(ai_service):
    """Test that real mode DOES call load_model."""
    with patch.object(AIConfig, "simulation_mode", new_callable=PropertyMock) as mock_sim:
        mock_sim.return_value = False

        with patch("os.path.exists", return_value=True):
            with patch.object(ai_service.loader, "load_model") as mock_load:
                mock_pipe = MagicMock()
                mock_pipe.return_value = [{"label": "rock", "score": 0.9}]
                mock_load.return_value = mock_pipe

                result = ai_service.analyze_audio_classification("real.mp3")

                mock_load.assert_called_once()
                assert result[0]["label"] == "rock"
