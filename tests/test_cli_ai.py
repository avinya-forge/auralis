import argparse
import io
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to path if needed (matches test_cli_main.py)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli.cli_main import run_ai_check, run_cli, setup_parser  # noqa: E402


class TestCLIAI(unittest.TestCase):
    def test_setup_parser_ai_check(self):
        """Test that parser correctly handles 'ai check'"""
        parser = setup_parser()

        args = parser.parse_args(["ai", "check"])
        self.assertEqual(args.command, "ai")
        self.assertEqual(args.ai_command, "check")

    @patch("src.cli.cli_main.DependencyChecker")
    def test_run_ai_check(self, MockChecker):
        """Test run_ai_check prints correct info"""
        mock_checker = MockChecker.return_value
        mock_checker.check_ai_dependencies.return_value = {
            "torch": {
                "installed": True,
                "version": "2.0.0",
                "cuda": True,
                "mps": False,
                "variant": "CUDA 11.8",
                "size": "2.1 GB",
            },
            "transformers": {"installed": True, "version": "4.30.0"},
            "torchaudio": {"installed": False},
            "scipy": {"installed": True, "version": "1.10.0"},
            "librosa": {"installed": False},
        }

        args = argparse.Namespace()

        # Capture stdout
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            run_ai_check(args)
            output = fake_out.getvalue()

        self.assertIn("Checking AI environment...", output)
        self.assertIn("PyTorch Status: ✓", output)
        self.assertIn("Version: 2.0.0", output)
        self.assertIn("Variant: CUDA 11.8", output)
        self.assertIn("CUDA Available: Yes", output)
        self.assertIn("MPS Available: No", output)
        self.assertIn("Est. Size: 2.1 GB", output)

        self.assertIn("✓ transformers (4.30.0)", output)
        self.assertIn("✗ torchaudio (N/A)", output)
        self.assertIn("✓ scipy (1.10.0)", output)
        self.assertIn("✗ librosa (N/A)", output)

    @patch("src.cli.cli_main.run_ai_check")
    @patch("src.cli.cli_main.setup_parser")
    def test_run_cli_dispatch_ai_check(self, mock_setup_parser, mock_run_ai_check):
        """Test that run_cli correctly dispatches to run_ai_check"""
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            command="ai", ai_command="check", log_level="INFO", debug=False
        )
        mock_setup_parser.return_value = mock_parser

        # We don't need HAS_PYQT to be true for ai check
        with patch("src.cli.cli_main.HAS_PYQT", False):
            # Mock QCoreApplication just in case, though it shouldn't be reached
            with patch("src.cli.cli_main.QCoreApplication"):
                run_cli()

        mock_run_ai_check.assert_called_once()


if __name__ == "__main__":
    unittest.main()
