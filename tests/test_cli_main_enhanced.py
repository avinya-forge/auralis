from unittest.mock import MagicMock, patch
import unittest
import sys


class TestCLIEnhanced(unittest.TestCase):
    def setUp(self):
        # Create mocks for the modules we want to mock
        self.mock_playlist_service = MagicMock()
        self.mock_audio_analysis = MagicMock()
        self.mock_metadata_service = MagicMock()

        # Patch sys.modules to include our mocks
        # We use patch.dict so it's reversed after the test
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "src.services.playlist_service": self.mock_playlist_service,
                "src.services.audio_analysis_service": self.mock_audio_analysis,
                "src.services.metadata_service": self.mock_metadata_service,
            },
        )
        self.modules_patcher.start()

        # Import the module under test here, after patching
        # We need to reload it to ensure it uses the mocked modules if they are imported at top level
        # But src.cli.cli_main imports them locally inside functions, so just importing is enough if not already imported.
        # However, to be safe against persistent imports from other tests, we should perhaps reload.
        import src.cli.cli_main
        import importlib

        importlib.reload(src.cli.cli_main)
        self.cli_main = src.cli.cli_main

    def tearDown(self):
        self.modules_patcher.stop()

    @patch("src.cli.cli_main._load_files")
    def test_run_playlist_generate(self, mock_load):
        args = MagicMock()
        args.pl_command = "generate"
        args.type = "upbeat"
        args.source = "dir"
        args.output = "out.m3u8"
        args.bpm = None

        mock_load.return_value = [{"path": "1.mp3"}]

        # Configure the mocks
        mock_gen = self.mock_playlist_service.PlaylistGenerator
        mock_gen_instance = mock_gen.return_value
        mock_gen_instance.generate_upbeat_playlist.return_value = [{"path": "1.mp3"}]
        mock_gen_instance.export_playlist.return_value = True

        self.cli_main.run_playlist(args)

        mock_gen_instance.generate_upbeat_playlist.assert_called_once()
        mock_gen_instance.export_playlist.assert_called_once()
        self.mock_playlist_service.PlaylistHistory.return_value.add_entry.assert_called_once()

    @patch("src.cli.cli_main._load_files")
    @patch("src.cli.cli_main.ConsoleHandler")
    def test_run_analyze(self, mock_handler, mock_load):
        args = MagicMock()
        args.source = "dir"
        args.replay_gain = True
        args.save = False

        mock_load.return_value = [{"path": "1.mp3", "metadata": {}}]

        self.cli_main.run_analyze(args)

        self.mock_metadata_service.MetadataService.return_value.update_metadata.assert_called_once()
        self.mock_audio_analysis.AudioAnalyzer.return_value.calculate_replay_gain.assert_called()
