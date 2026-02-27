from unittest.mock import MagicMock

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
        data = {
            "TBPM": "128",
            "TKEY": "C Major",
            "TMOO": "Energetic",
            "TXXX:RAGA": "Yaman",
            "TXXX:AI_MOOD": "Meditative",
        }
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        metadata = {}
        scanner._parse_mp3_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
        assert metadata["raga"] == "Yaman"
        assert metadata["ai_mood"] == "Meditative"

    def test_parse_flac_tags_extended(self, scanner):
        # Mock FLAC audio object (returns lists)
        audio = MagicMock()
        data = {
            "bpm": ["128"],
            "initialkey": ["C Major"],
            "mood": ["Energetic"],
            "raga": ["Bhairav"],
            "ai_mood": ["Devotional"],
        }
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        metadata = {}
        scanner._parse_flac_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
        assert metadata["raga"] == "Bhairav"
        assert metadata["ai_mood"] == "Devotional"

    def test_parse_generic_tags_extended(self, scanner):
        # Mock Generic audio object (returns lists)
        audio = MagicMock()
        data = {"bpm": ["128"], "initialkey": ["C Major"], "mood": ["Energetic"]}
        audio.__contains__.side_effect = data.__contains__
        audio.__getitem__.side_effect = data.__getitem__

        metadata = {}
        scanner._parse_generic_tags(audio, metadata)

        assert metadata["bpm"] == "128"
        assert metadata["key"] == "C Major"
        assert metadata["mood"] == "Energetic"
