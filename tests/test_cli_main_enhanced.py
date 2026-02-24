from unittest.mock import MagicMock, patch
import unittest
import sys

# Mock dependencies to avoid import errors if they rely on system tools
sys.modules["src.services.playlist_service"] = MagicMock()
sys.modules["src.services.audio_analysis_service"] = MagicMock()
sys.modules["src.services.metadata_service"] = MagicMock()

# We need to import the module under test AFTER mocking if it has top-level side effects
# But cli_main imports inside functions mostly.
from src.cli.cli_main import run_playlist, run_analyze  # noqa: E402


class TestCLIEnhanced(unittest.TestCase):
    @patch("src.cli.cli_main._load_files")
    def test_run_playlist_generate(self, mock_load):
        args = MagicMock()
        args.pl_command = "generate"
        args.type = "upbeat"
        args.source = "dir"
        args.output = "out.m3u8"
        args.bpm = None

        mock_load.return_value = [{"path": "1.mp3"}]

        # Configure the mocks in sys.modules
        pl_module = sys.modules["src.services.playlist_service"]
        mock_gen = pl_module.PlaylistGenerator
        mock_gen_instance = mock_gen.return_value
        mock_gen_instance.generate_upbeat_playlist.return_value = [{"path": "1.mp3"}]
        mock_gen_instance.export_playlist.return_value = True

        run_playlist(args)

        mock_gen_instance.generate_upbeat_playlist.assert_called_once()
        mock_gen_instance.export_playlist.assert_called_once()
        pl_module.PlaylistHistory.return_value.add_entry.assert_called_once()

    @patch("src.cli.cli_main._load_files")
    @patch("src.cli.cli_main.ConsoleHandler")
    def test_run_analyze(self, mock_handler, mock_load):
        args = MagicMock()
        args.source = "dir"
        args.replay_gain = True
        args.save = False

        mock_load.return_value = [{"path": "1.mp3", "metadata": {}}]

        # Configure mocks
        meta_module = sys.modules["src.services.metadata_service"]
        aa_module = sys.modules["src.services.audio_analysis_service"]

        run_analyze(args)

        meta_module.MetadataService.return_value.update_metadata.assert_called_once()
        aa_module.AudioAnalyzer.return_value.calculate_replay_gain.assert_called()
