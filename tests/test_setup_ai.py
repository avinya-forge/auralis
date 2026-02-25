"""
Tests for setup_ai.py script logic.
"""

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from setup_ai import main


@pytest.fixture
def mock_checker():
    with patch("setup_ai.DependencyChecker") as MockChecker:
        checker = MockChecker.return_value
        # Default report: nothing installed
        checker.check_ai_dependencies.return_value = {
            "torch": {"installed": False},
            "torchaudio": {"installed": False},
            "transformers": {"installed": False},
            "scipy": {"installed": False},
            "librosa": {"installed": False},
        }
        checker.install_pip_packages.return_value = True
        yield checker


def test_main_help():
    """Test help argument."""
    with patch.object(sys, "argv", ["setup_ai.py", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0


def test_main_install_defaults(mock_checker):
    """Test default installation path (auto)."""
    with patch.object(sys, "argv", ["setup_ai.py", "--yes"]):
        # Mock install_packages to intercept calls
        with patch("setup_ai.install_packages", return_value=True) as mock_install:
            with patch("platform.system", return_value="Linux"):
                exit_code = main()

                assert exit_code == 0
                # Check calls
                assert mock_install.call_count == 2

                # First call should be torch with CUDA index (Linux default)
                args1, kwargs1 = mock_install.call_args_list[0]
                assert set(args1[0]) == {"torch", "torchaudio"}
                # Check that index URL is CUDA
                assert "cu121" in args1[1]

                # Second call should be others
                args2, kwargs2 = mock_install.call_args_list[1]
                assert set(args2[0]) == {"transformers", "scipy", "librosa"}
                # Check optional arg
                if len(args2) > 1:
                     assert args2[1] is None
                else:
                     assert kwargs2.get("index_url") is None


def test_main_install_cpu(mock_checker):
    """Test CPU installation."""
    with patch.object(sys, "argv", ["setup_ai.py", "--cpu", "--yes"]):
        with patch("setup_ai.install_packages", return_value=True) as mock_install:
            with patch("platform.system", return_value="Linux"):
                exit_code = main()

                assert exit_code == 0

                # Torch call should be CPU index
                args1, kwargs1 = mock_install.call_args_list[0]
                assert "cpu" in args1[1]


def test_main_install_macos(mock_checker):
    """Test macOS installation (no index URL)."""
    with patch.object(sys, "argv", ["setup_ai.py", "--yes"]):
        with patch("setup_ai.install_packages", return_value=True) as mock_install:
            with patch("platform.system", return_value="Darwin"):
                exit_code = main()

                assert exit_code == 0

                # Torch call should have NO index URL (None)
                args1, kwargs1 = mock_install.call_args_list[0]
                if len(args1) > 1:
                     assert args1[1] is None
                else:
                     assert kwargs1.get("index_url") is None


def test_main_all_installed(mock_checker):
    """Test when everything is installed."""
    mock_checker.check_ai_dependencies.return_value = {
        "torch": {"installed": True, "cuda": True, "version": "2.0"},
        "torchaudio": {"installed": True},
        "transformers": {"installed": True},
        "scipy": {"installed": True},
        "librosa": {"installed": True},
    }

    with patch.object(sys, "argv", ["setup_ai.py"]):
        exit_code = main()
        assert exit_code == 0
