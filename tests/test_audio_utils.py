import os
from unittest.mock import MagicMock, patch

import pytest

from src.utils.audio_utils import AudioUtils


class TestAudioUtils:

    def test_detect_leading_silence(self):
        # Create a mock sound object
        mock_sound = MagicMock()
        mock_sound.__len__.return_value = 100
        # Mock slice access: sound[start:end].dBFS
        # Return -60 for first 20ms, then -40
        def get_slice(s):
            start = s.start
            end = s.stop
            slice_mock = MagicMock()
            if start < 20:
                slice_mock.dBFS = -60.0
            else:
                slice_mock.dBFS = -40.0
            return slice_mock

        mock_sound.__getitem__.side_effect = get_slice

        silence_ms = AudioUtils.detect_leading_silence(mock_sound, silence_threshold=-50.0, chunk_size=10)
        assert silence_ms == 20

    @patch("src.utils.audio_utils.HAS_PYDUB", True)
    @patch("src.utils.audio_utils.AudioSegment")
    def test_trim_silence(self, MockAudioSegment):
        mock_audio = MagicMock()
        MockAudioSegment.from_file.return_value = mock_audio
        mock_audio.__len__.return_value = 1000  # 1 sec

        # We need mock_audio.reverse() to return mock_audio or another mock
        mock_audio.reverse.return_value = mock_audio

        # Mock detect_leading_silence by patching AudioUtils.detect_leading_silence
        with patch("src.utils.audio_utils.AudioUtils.detect_leading_silence", side_effect=[150, 150]):
            # Start: 150ms silence. End: 150ms silence.
            # Padding: 100ms.
            # Should trim 150-100 = 50ms from start and end.

            # Mock slicing and export
            mock_trimmed = MagicMock()
            mock_audio.__getitem__.return_value = mock_trimmed

            result = AudioUtils.trim_silence("test.mp3", padding=100)

            assert result is True
            mock_audio.__getitem__.assert_called()
            # Verify slice indices: start=50, end=1000-50=950
            # slice(50, 950)
            args, _ = mock_audio.__getitem__.call_args
            # slice object is passed
            s = args[0]
            assert s.start == 50
            assert s.stop == 950

            mock_trimmed.export.assert_called_with("test.mp3", format="mp3")

    @patch("src.utils.audio_utils.HAS_PYDUB", False)
    def test_trim_silence_no_pydub(self):
        assert not AudioUtils.trim_silence("test.mp3")

    @patch("src.utils.audio_utils.HAS_PYDUB", True)
    @patch("src.utils.audio_utils.AudioSegment")
    def test_trim_silence_no_silence(self, MockAudioSegment):
        mock_audio = MagicMock()
        MockAudioSegment.from_file.return_value = mock_audio
        mock_audio.__len__.return_value = 1000
        mock_audio.reverse.return_value = mock_audio

        with patch("src.utils.audio_utils.AudioUtils.detect_leading_silence", side_effect=[50, 50]):
            # Silence 50ms < Padding 100ms. No trim needed.
            result = AudioUtils.trim_silence("test.mp3", padding=100)
            assert result is False
            # Export not called on trimmed audio (which isn't created)
            # But mock_audio.export is not called either
            mock_audio.export.assert_not_called()
