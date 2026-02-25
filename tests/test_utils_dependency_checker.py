"""
Tests for Dependency Checker (AI Features)
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from src.utils.dependency_checker import DependencyChecker


@pytest.fixture
def checker():
    return DependencyChecker()


def test_check_ai_dependencies_missing(checker):
    """Test check_ai_dependencies when modules are missing."""
    with patch.dict(sys.modules, {"torch": None, "transformers": None, "torchaudio": None, "scipy": None, "librosa": None}):
        report = checker.check_ai_dependencies()

        assert report["torch"]["installed"] is False
        assert report["transformers"]["installed"] is False
        assert report["torchaudio"]["installed"] is False


def test_check_ai_dependencies_torch_cpu(checker):
    """Test check_ai_dependencies with CPU torch."""
    mock_torch = MagicMock()
    mock_torch.__version__ = "2.1.0+cpu"
    mock_torch.cuda.is_available.return_value = False
    mock_torch.backends.mps.is_available.return_value = False

    with patch.dict(sys.modules, {"torch": mock_torch}):
        report = checker.check_ai_dependencies()

        assert report["torch"]["installed"] is True
        assert report["torch"]["version"] == "2.1.0+cpu"
        assert report["torch"]["cuda"] is False
        assert report["torch"]["mps"] is False


def test_check_ai_dependencies_torch_cuda(checker):
    """Test check_ai_dependencies with CUDA torch."""
    mock_torch = MagicMock()
    mock_torch.__version__ = "2.1.0+cu118"
    mock_torch.cuda.is_available.return_value = True

    with patch.dict(sys.modules, {"torch": mock_torch}):
        report = checker.check_ai_dependencies()

        assert report["torch"]["installed"] is True
        assert report["torch"]["version"] == "2.1.0+cu118"
        assert report["torch"]["cuda"] is True


def test_check_ai_dependencies_other_libs(checker):
    """Test checking other libraries like transformers."""
    mock_transformers = MagicMock()
    mock_transformers.__version__ = "4.30.0"

    with patch.dict(sys.modules, {"transformers": mock_transformers}):
        report = checker.check_ai_dependencies()

        assert report["transformers"]["installed"] is True
        assert report["transformers"]["version"] == "4.30.0"
