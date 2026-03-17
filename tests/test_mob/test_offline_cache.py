import os
import sqlite3
import tempfile
import time
import pytest
from src.modules.mob.offline_cache import OfflineCache

@pytest.fixture
def temp_cache():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_cache.db")
        # 100 bytes max cache
        cache = OfflineCache(db_path=db_path, max_size_bytes=100)
        yield cache, temp_dir
        cache.close()

def test_cache_initialization(temp_cache):
    cache, temp_dir = temp_cache
    assert os.path.exists(cache.db_path)
    assert cache.get_total_size() == 0

def test_cache_track_inserts_and_gets(temp_cache):
    cache, temp_dir = temp_cache
    file_path = os.path.join(temp_dir, "track1.opus")
    with open(file_path, "wb") as f:
        f.write(b"a" * 30)

    cache.cache_track("t1", "Title 1", "Artist 1", file_path, 30)
    assert cache.get_total_size() == 30

    track = cache.get_track("t1")
    assert track is not None
    assert track[0] == "t1"
    assert track[1] == "Title 1"
    assert track[2] == "Artist 1"
    assert track[3] == file_path
    assert track[4] == 30

def test_lru_eviction(temp_cache):
    cache, temp_dir = temp_cache

    tracks = []
    # Fill cache to 90 bytes (3 tracks * 30 bytes)
    for i in range(3):
        file_path = os.path.join(temp_dir, f"track{i}.opus")
        with open(file_path, "wb") as f:
            f.write(b"a" * 30)
        cache.cache_track(f"t{i}", f"Title {i}", f"Artist {i}", file_path, 30)
        tracks.append(file_path)
        time.sleep(0.01) # ensure different timestamps

    assert cache.get_total_size() == 90
    assert os.path.exists(tracks[0])

    # Touch t0 so it is no longer the oldest
    cache.get_track("t0")
    time.sleep(0.01)

    # Adding t3 (40 bytes) will push total to 130 > 100
    # It should evict t1 (now oldest) -> 130 - 30 = 100 <= 100.
    file_path = os.path.join(temp_dir, "track3.opus")
    with open(file_path, "wb") as f:
        f.write(b"a" * 40)
    cache.cache_track("t3", "Title 3", "Artist 3", file_path, 40)

    assert cache.get_total_size() == 100
    assert not os.path.exists(tracks[1]) # t1 should be deleted
    assert cache.get_track("t1") is None

    # Check what happens if eviction is larger than 1 item
    # Adding t4 (70 bytes) will push total to 170 > 100
    # Current cache: t2 (30 bytes), t0 (30 bytes), t3 (40 bytes)
    # Order of timestamps: t2, t0, t3.
    # It should evict t2 -> 140 > 100
    # It should evict t0 -> 110 > 100
    # It should evict t3 -> 70 <= 100
    # Wait, 170 - 30 = 140. 140 - 30 = 110. 110 - 40 = 70.

    file_path4 = os.path.join(temp_dir, "track4.opus")
    with open(file_path4, "wb") as f:
        f.write(b"a" * 70)
    cache.cache_track("t4", "Title 4", "Artist 4", file_path4, 70)

    assert cache.get_total_size() == 70
    assert not os.path.exists(tracks[2]) # t2
    assert not os.path.exists(tracks[0]) # t0
    assert not os.path.exists(file_path) # t3

def test_lru_graceful_missing_file(temp_cache):
    cache, temp_dir = temp_cache
    file_path = os.path.join(temp_dir, "track_missing.opus")
    # File doesn't exist on disk, simulating a user deletion outside the app
    cache.cache_track("tm", "Missing", "Artist", file_path, 80)
    assert cache.get_total_size() == 80

    file_path2 = os.path.join(temp_dir, "track2.opus")
    with open(file_path2, "wb") as f:
        f.write(b"a" * 50)
    # Adding 50 bytes triggers eviction.
    cache.cache_track("t2", "Title 2", "Artist", file_path2, 50)

    assert cache.get_total_size() == 50
    assert cache.get_track("tm") is None

def test_clear_cache(temp_cache):
    cache, temp_dir = temp_cache
    file_path = os.path.join(temp_dir, "track1.opus")
    with open(file_path, "wb") as f:
        f.write(b"a" * 30)
    cache.cache_track("t1", "Title", "Artist", file_path, 30)

    assert os.path.exists(file_path)
    assert cache.get_total_size() == 30

    cache.clear_cache()

    assert not os.path.exists(file_path)
    assert cache.get_total_size() == 0

def test_cache_track_update(temp_cache):
    cache, temp_dir = temp_cache
    file_path = os.path.join(temp_dir, "track_update.opus")
    with open(file_path, "wb") as f:
        f.write(b"a" * 30)

    # Insert new track
    cache.cache_track("t1", "Title 1", "Artist 1", file_path, 30)
    assert cache.get_total_size() == 30

    # Update same track id with new data
    cache.cache_track("t1", "Title 1 Updated", "Artist 1", file_path, 30)
    assert cache.get_total_size() == 30 # Size should not double count
    track = cache.get_track("t1")
    assert track[1] == "Title 1 Updated"

    # Update same track with larger size
    with open(file_path, "wb") as f:
        f.write(b"a" * 50)
    cache.cache_track("t1", "Title 1 Larger", "Artist 1", file_path, 50)
    assert cache.get_total_size() == 50
