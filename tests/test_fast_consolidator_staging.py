"""
Unit tests for FastConsolidator and StagingManager
"""

import os
import sqlite3
import tempfile
import pytest
from src.engine.fast_consolidator import FastConsolidator, HardwareStrategy
from src.engine.staging_manager import StagingManager

@pytest.fixture
def temp_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_inventory.db")
        staging_root = os.path.join(tmpdir, "staging")
        dupes_root = os.path.join(tmpdir, "dupes")
        corrupt_root = os.path.join(tmpdir, "corrupt")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE audio_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            filename TEXT,
            extension TEXT,
            file_size INTEGER,
            duration REAL,
            bitrate INTEGER,
            file_hash TEXT,
            artist TEXT,
            title TEXT,
            album TEXT,
            genre TEXT,
            year TEXT,
            detected_language TEXT,
            suggested_target_path TEXT,
            status TEXT DEFAULT 'DISCOVERED'
        )
        """)
        
        # Create physical dummy audio files
        f1 = os.path.join(tmpdir, "song1.mp3")
        with open(f1, "wb") as f:
            f.write(b"AUDIO_DATA_X" * 200) # > 1024 bytes
            
        f2 = os.path.join(tmpdir, "song1_copy.mp3") # Exact duplicate size & name
        with open(f2, "wb") as f:
            f.write(b"AUDIO_DATA_X" * 200)
            
        f3_zero = os.path.join(tmpdir, "corrupt.mp3") # 0 bytes
        with open(f3_zero, "wb") as f:
            pass
            
        f4_unique = os.path.join(tmpdir, "unique.mp3")
        with open(f4_unique, "wb") as f:
            f.write(b"AUDIO_DATA_Y" * 300)
            
        # Insert records
        cur.execute("INSERT INTO audio_inventory VALUES (1, ?, 'song1.mp3', '.mp3', 2400, 120.0, 128000, 'hash1', 'Artist', 'Song 1', 'Album', 'Pop', '2020', 'Hindi', '', 'DISCOVERED')", (f1,))
        cur.execute("INSERT INTO audio_inventory VALUES (2, ?, 'song1.mp3', '.mp3', 2400, 120.0, 128000, 'hash1', 'Artist', 'Song 1', 'Album', 'Pop', '2020', 'Hindi', '', 'DISCOVERED')", (f2,))
        cur.execute("INSERT INTO audio_inventory VALUES (3, ?, 'corrupt.mp3', '.mp3', 0, 0.0, 0, 'hash0', '', '', '', '', '', 'Unknown', '', 'DISCOVERED')", (f3_zero,))
        cur.execute("INSERT INTO audio_inventory VALUES (4, ?, 'unique.mp3', '.mp3', 3600, 180.0, 192000, 'hash2', 'Artist 2', 'Unique', 'Album 2', 'Rock', '2021', 'English', '', 'DISCOVERED')", (f4_unique,))
        
        conn.commit()
        conn.close()
        
        yield {
            "tmpdir": tmpdir,
            "db_path": db_path,
            "staging_root": staging_root,
            "dupes_root": dupes_root,
            "corrupt_root": corrupt_root,
            "f1": f1,
            "f2": f2,
            "f3_zero": f3_zero,
            "f4_unique": f4_unique
        }

def test_hardware_strategy():
    rec = HardwareStrategy.get_recommended_drives()
    assert "fast_working_drive" in rec
    assert "cold_backup_drive" in rec
    assert "car_sync_drive" in rec

def test_fast_consolidator_audit_corrupt(temp_env):
    consolidator = FastConsolidator(db_path=temp_env["db_path"])
    corrupt_audit = consolidator.audit_zero_byte_and_corrupt()
    assert corrupt_audit["total_corrupted_or_zero_byte"] == 1
    assert corrupt_audit["files"][0]["filename"] == "corrupt.mp3"

def test_fast_consolidator_tier0_dupes(temp_env):
    consolidator = FastConsolidator(db_path=temp_env["db_path"])
    t0_data = consolidator.find_tier0_exact_duplicates()
    assert t0_data["tier0_duplicate_groups"] == 1
    assert t0_data["total_redundant_files_identified"] == 1
    assert t0_data["duplicate_groups"][0]["filename"] == "song1.mp3"

def test_staging_manager_execution_and_rollback(temp_env):
    mgr = StagingManager(
        db_path=temp_env["db_path"],
        staging_root=temp_env["staging_root"],
        duplicates_root=temp_env["dupes_root"],
        corrupt_root=temp_env["corrupt_root"]
    )
    
    plan = mgr.build_staging_plan()
    assert plan["total_files"] == 4
    assert plan["unique_tracks"] == 2 # song1 (primary keeper) + unique
    assert plan["duplicate_copies"] == 1 # song1 copy
    assert plan["corrupt_files"] == 1 # corrupt.mp3
    
    res = mgr.execute_staging()
    assert res["files_copied"] == 4
    
    # Verify rollback script generation
    assert os.path.exists(res["rollback_script"])
    
    # Check staging directory structure
    parent_ctx = os.path.basename(temp_env["tmpdir"])
    assert os.path.exists(os.path.join(temp_env["staging_root"], "Hindi", parent_ctx, "song1.mp3"))
    assert os.path.exists(os.path.join(temp_env["staging_root"], "English", "unique.mp3"))
    assert os.path.exists(os.path.join(temp_env["dupes_root"], "song1.mp3"))
    assert os.path.exists(os.path.join(temp_env["corrupt_root"], "corrupt.mp3"))
