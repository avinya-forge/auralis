"""
Unit tests for ReliableMetadataClient in src/engine/reliable_metadata_client.py.
Tests online querying, caching, artwork fetching, Deezer, and fallback behaviors.
"""

import os
import json
import sqlite3
import pytest
from unittest.mock import patch, MagicMock

from src.engine.reliable_metadata_client import ReliableMetadataClient

def test_reliable_metadata_client_cache_lifecycle(tmp_path):
    db_file = str(tmp_path / "test_cache.db")
    client = ReliableMetadataClient(cache_db=db_file)
    
    # Verify cache miss
    cached = client.get_cached("Comfortably Numb", "Pink Floyd")
    assert cached is None
    
    # Save mock metadata
    test_data = {
        "title": "Comfortably Numb",
        "artist": "Pink Floyd",
        "album": "The Wall",
        "year": "1979",
        "genre": "Rock",
        "composer": "Gilmour / Waters",
        "artwork_url": "https://example.com/art.jpg"
    }
    client.save_cache("Comfortably Numb", "Pink Floyd", test_data, source="test")
    
    # Verify cache hit
    hit = client.get_cached("Comfortably Numb", "Pink Floyd")
    assert hit is not None
    assert hit["title"] == "Comfortably Numb"
    assert hit["album"] == "The Wall"
    assert hit["year"] == "1979"

def test_reliable_metadata_client_query_itunes_success():
    client = ReliableMetadataClient()
    mock_response = {
        "resultCount": 1,
        "results": [{
            "trackName": "Hotel California",
            "artistName": "Eagles",
            "collectionName": "Hotel California",
            "releaseDate": "1976-12-08T08:00:00Z",
            "primaryGenreName": "Rock",
            "artworkUrl100": "https://example.com/100x100bb.jpg",
            "trackNumber": 1
        }]
    }
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response).encode("utf-8")
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm
        
        res = client.query_itunes("Eagles Hotel California")
        assert res is not None
        assert res["title"] == "Hotel California"
        assert res["artist"] == "Eagles"
        assert res["year"] == "1976"
        assert "600x600bb" in res["artwork_url"]

def test_reliable_metadata_client_query_itunes_album():
    client = ReliableMetadataClient()
    mock_response = {
        "resultCount": 1,
        "results": [{
            "collectionName": "Rockstar (Original Motion Picture Soundtrack)",
            "artistName": "A.R. Rahman",
            "releaseDate": "2011-09-30T07:00:00Z",
            "primaryGenreName": "Bollywood",
            "artworkUrl100": "https://example.com/100x100bb.jpg",
        }]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response).encode("utf-8")
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        res = client.query_itunes_album("Rockstar", "A.R. Rahman")
        assert res is not None
        assert res["album"] == "Rockstar (Original Motion Picture Soundtrack)"
        assert res["album_artist"] == "A.R. Rahman"
        assert res["year"] == "2011"
        assert "600x600bb" in res["artwork_url"]

def test_reliable_metadata_client_query_deezer():
    client = ReliableMetadataClient()
    mock_deezer = {
        "data": [{
            "title": "Enter Sandman",
            "artist": {"name": "Metallica"},
            "album": {
                "title": "Metallica (Remastered 2021)",
                "cover_xl": "https://example.com/1000x1000.jpg"
            }
        }]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_deezer).encode("utf-8")
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        res = client.query_deezer("Enter Sandman Metallica")
        assert res is not None
        assert res["title"] == "Enter Sandman"
        assert res["artist"] == "Metallica"
        assert res["artwork_url"] == "https://example.com/1000x1000.jpg"

def test_reliable_metadata_client_query_deezer_album():
    client = ReliableMetadataClient()
    mock_deezer_album = {
        "data": [{
            "title": "Gangster",
            "artist": {"name": "Pritam"},
            "cover_xl": "https://example.com/gangster_1000x1000.jpg"
        }]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_deezer_album).encode("utf-8")
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        res = client.query_deezer_album("Gangster", "Pritam")
        assert res is not None
        assert res["album"] == "Gangster"
        assert res["album_artist"] == "Pritam"
        assert res["artwork_url"] == "https://example.com/gangster_1000x1000.jpg"

def test_reliable_metadata_client_query_musicbrainz_success():
    client = ReliableMetadataClient()
    mock_mb_response = {
        "recordings": [{
            "title": "Imagine",
            "artist-credit": [{"name": "John Lennon"}],
            "first-release-date": "1971-10-11",
            "releases": [{"title": "Imagine"}]
        }]
    }
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_mb_response).encode("utf-8")
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm
        
        res = client.query_musicbrainz("Imagine", "John Lennon")
        assert res is not None
        assert res["title"] == "Imagine"
        assert res["artist"] == "John Lennon"
        assert res["year"] == "1971"

def test_reliable_metadata_client_fetch_artwork_bytes():
    client = ReliableMetadataClient()
    fake_bytes = b"\xff\xd8\xff\xe0fake_jpeg"
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_cm = MagicMock()
        mock_cm.read.return_value = fake_bytes
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm
        
        art = client.fetch_artwork_bytes("https://example.com/art.jpg")
        assert art == fake_bytes

def test_reliable_metadata_client_resolve_track_fallback(tmp_path):
    db_file = str(tmp_path / "test_cache2.db")
    client = ReliableMetadataClient(cache_db=db_file)
    
    with patch("urllib.request.urlopen", side_effect=Exception("Network down")):
        res = client.resolve_track_metadata(
            filename="01 Purusha Suktam.mp3",
            artist="Vedic Rishis",
            album="Rigveda"
        )
        assert res is not None
        assert res["title"] == "Purusha Suktam"
        assert res["artist"] == "Vedic Rishis"
        assert res["album"] == "Rigveda"
