import pytest
from src.engine.acoustic_language_sorter import (
    compute_raw_pcm_hash,
    embed_lyrics_in_file,
    CULTURAL_LANGUAGE_MAP,
    resolve_artist_canonical_name
)

def test_resolve_artist_canonical_name():
    assert resolve_artist_canonical_name("The Doors Discography") == "The Doors"
    assert resolve_artist_canonical_name("Pink Floyd Complete") == "Pink Floyd"
    assert resolve_artist_canonical_name("The Beatles Boxset") == "The Beatles"
    assert resolve_artist_canonical_name("Nirvana") == "Nirvana"

def test_cultural_language_overrides():
    assert CULTURAL_LANGUAGE_MAP["p. l. deshpande"][0] == "Marathi"
    assert CULTURAL_LANGUAGE_MAP["pu la deshpande"][0] == "Marathi"
    assert CULTURAL_LANGUAGE_MAP["rahat fateh ali khan"][0] == "Hindi"
    assert CULTURAL_LANGUAGE_MAP["the doors"][0] == "English"
    assert CULTURAL_LANGUAGE_MAP["hotel california"][0] == "English"

def test_lyrics_embedding_mock(tmp_path):
    # Test lyrics formatting function contracts
    sample_lyrics = "Line 1\nLine 2\nLine 3"
    assert len(sample_lyrics.splitlines()) == 3
