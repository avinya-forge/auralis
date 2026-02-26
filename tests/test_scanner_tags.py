from unittest.mock import MagicMock, Mock

import pytest
from PyQt6.QtCore import QCoreApplication

from src.core.scanner import MusicScanner


@pytest.fixture(scope="session")
def qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


class TestScannerTags:
    @pytest.fixture
    def scanner(self, qapp):
        return MusicScanner()

    def test_parse_mp3_tags_extended(self, scanner):
        # Mock MP3 audio object
        audio = MagicMock()
        data = {"TBPM": "128", "TKEY": "C Major", "TMOO": "Energetic"}
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        # Mock TXXX frames
        txxx_raga = Mock()
        txxx_raga.desc = "RAGA"
        txxx_raga.text = ["Bhairavi"]

        txxx_ai_mood = Mock()
        txxx_ai_mood.desc = "AI_MOOD"
        txxx_ai_mood.text = ["Meditative"]

        audio.tags = {"TXXX:RAGA": txxx_raga, "TXXX:AI_MOOD": txxx_ai_mood}
        # audio.tags is a dict, so keys() works by default, no need to mock it unless audio.tags was a Mock

        metadata = {}
        scanner._parse_mp3_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
        assert metadata["raga"] == "Bhairavi"
        assert metadata["ai_mood"] == "Meditative"

    def test_parse_flac_tags_extended(self, scanner):
        # Mock FLAC audio object (returns lists)
        audio = MagicMock()
        data = {
            "bpm": ["128"],
            "initialkey": ["C Major"],
            "mood": ["Energetic"],
            "raga": ["Bhairavi"],
            "ai_mood": ["Meditative"],
        }
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        metadata = {}
        scanner._parse_flac_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
        assert metadata["raga"] == "Bhairavi"
        assert metadata["ai_mood"] == "Meditative"

    def test_parse_generic_tags_extended(self, scanner):
        # Mock Generic audio object (returns lists)
        audio = MagicMock()
        data = {
            "bpm": ["128"],
            "initialkey": ["C Major"],
            "mood": ["Energetic"],
            "raga": ["Bhairavi"],
            "ai_mood": ["Meditative"],
        }
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        metadata = {}
        scanner._parse_generic_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
        assert metadata["raga"] == "Bhairavi"
        assert metadata["ai_mood"] == "Meditative"
