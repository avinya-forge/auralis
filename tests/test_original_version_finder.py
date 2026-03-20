from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.modules.neu.embedding_database import EmbeddingDatabase
from src.modules.neu.original_version_finder import OriginalVersionFinder


@pytest.fixture
def mock_embedding_db():
    return MagicMock(spec=EmbeddingDatabase)


@pytest.fixture
def finder(mock_embedding_db):
    with patch("musicbrainzngs.set_useragent"):
        return OriginalVersionFinder(embedding_db=mock_embedding_db)


def test_find_original_perfect_match(finder, mock_embedding_db):
    """Test finding the original version when similarities are high."""
    # Setup mock similarities
    target_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    mock_embedding_db.search_similar.return_value = [
        ("track_1", 0.95),
        ("track_2", 0.98),
        ("track_3", 0.85),  # Should be filtered out
    ]

    # Mock _get_oldest_release_date to return specific dates
    def mock_get_date(track_id):
        if track_id == "track_1":
            return datetime(1990, 1, 1)
        elif track_id == "track_2":
            return datetime(1995, 1, 1)
        return None

    with patch.object(finder, "_get_oldest_release_date", side_effect=mock_get_date):
        result = finder.find_original(target_embedding)

    assert result == "track_1"  # track_1 is oldest


def test_find_original_no_matches(finder, mock_embedding_db):
    """Test when no tracks have > 0.9 similarity."""
    target_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    mock_embedding_db.search_similar.return_value = [("track_1", 0.89), ("track_2", 0.85)]

    result = finder.find_original(target_embedding)
    assert result is None


def test_find_original_no_dates_found(finder, mock_embedding_db):
    """Test when none of the similar tracks have release dates in MusicBrainz."""
    target_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    mock_embedding_db.search_similar.return_value = [("track_1", 0.95)]

    with patch.object(finder, "_get_oldest_release_date", return_value=None):
        result = finder.find_original(target_embedding)

    # As per implementation, if no dates found, it returns None. Wait, looking at the code,
    # oldest_date remains None, so if we don't have fallback, it returns None.
    # Ah, the code says `return oldest_track_id` which starts as None and only gets set if `release_date` is truthy.
    assert result is None


@patch("musicbrainzngs.search_recordings")
def test_get_oldest_release_date_success(mock_search, finder):
    """Test fetching release dates from MusicBrainz API."""
    mock_search.return_value = {
        "recording-list": [
            {
                "release-list": [
                    {"date": "1999-12-31"},
                    {"date": "1995"},  # This should be parsed as oldest
                ]
            },
            {"release-list": [{"date": "1998-05"}]},
        ]
    }

    result = finder._get_oldest_release_date("track_1")
    assert result == datetime(1995, 1, 1)


@patch("musicbrainzngs.search_recordings")
def test_get_oldest_release_date_invalid_date(mock_search, finder):
    """Test with invalid date formats from MusicBrainz."""
    mock_search.return_value = {"recording-list": [{"release-list": [{"date": "invalid-date"}]}]}

    result = finder._get_oldest_release_date("track_1")
    assert result is None


@patch("musicbrainzngs.search_recordings")
def test_get_oldest_release_date_no_recordings(mock_search, finder):
    """Test with no recordings returned from MusicBrainz."""
    mock_search.return_value = {"recording-list": []}
    result = finder._get_oldest_release_date("track_1")
    assert result is None

    mock_search.return_value = {}
    result = finder._get_oldest_release_date("track_1")
    assert result is None


@patch("musicbrainzngs.search_recordings")
def test_get_oldest_release_date_error(mock_search, finder):
    """Test when MusicBrainz API raises an exception."""
    mock_search.side_effect = Exception("API error")

    result = finder._get_oldest_release_date("track_1")
    assert result is None


def test_init_exception_handling():
    with patch("musicbrainzngs.set_useragent", side_effect=Exception("Error")):
        finder = OriginalVersionFinder(embedding_db=MagicMock(spec=EmbeddingDatabase))
        assert finder is not None
