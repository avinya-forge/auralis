"""
Auralis - Multi-Drive Master Cataloger & Cross-Drive Deduplicator
Scans D:, F:, J:, and E: to calculate exact filename + size duplication,
isolates zero-byte files, and prepares the Centralized Shallow Base plan.
"""

import os
import sys
import sqlite3
import hashlib
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AUDIO_EXTS = {".mp3", ".flac", ".m4a", ".wav", ".wma", ".ogg", ".aac", ".aiff"}

def init_master_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_audio_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_letter TEXT,
        file_path TEXT UNIQUE,
        filename TEXT,
        extension TEXT,
        file_size INTEGER,
        is_corrupted_or_zero INTEGER DEFAULT 0,
        tier0_group_id TEXT,
        status TEXT DEFAULT 'DISCOVERED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_master_fn_size ON master_audio_catalog(filename, file_size)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_master_drive ON master_audio_catalog(drive_letter)")
    conn.commit()
    conn.close()

def scan_drive_files(root_dir: str, drive_name: str, db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    scanned = 0
    batch = []
    
    print(f"[*] Scanning Drive {drive_name}: {root_dir}...")
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in AUDIO_EXTS:
                full_path = os.path.join(dirpath, fname)
                try:
                    fsize = os.path.getsize(full_path)
                except Exception:
                    fsize = 0
                is_bad = 1 if fsize <= 1024 else 0
                
                batch.append((drive_name, full_path, fname, ext, fsize, is_bad))
                scanned += 1
                
                if len(batch) >= 1000:
                    cur.executemany("""
                    INSERT OR IGNORE INTO master_audio_catalog 
                    (drive_letter, file_path, filename, extension, file_size, is_corrupted_or_zero)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, batch)
                    conn.commit()
                    batch = []
                    print(f"    {drive_name}: Cataloged {scanned} tracks...")
                    
    if batch:
        cur.executemany("""
        INSERT OR IGNORE INTO master_audio_catalog 
        (drive_letter, file_path, filename, extension, file_size, is_corrupted_or_zero)
        VALUES (?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        
    conn.close()
    return scanned

def analyze_cross_drive_redundancy(db_path: str) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Total counts per drive
    cur.execute("SELECT drive_letter, COUNT(*), SUM(file_size) FROM master_audio_catalog GROUP BY drive_letter")
    drive_stats = {d: {"count": cnt, "size_gb": round(sz / (1024**3), 2) if sz else 0} for d, cnt, sz in cur.fetchall()}
    
    # 2. Zero-byte or corrupt count
    cur.execute("SELECT COUNT(*) FROM master_audio_catalog WHERE is_corrupted_or_zero = 1")
    zero_bytes = cur.fetchone()[0]
    
    # 3. Exact Filename + Exact File Size across the entire universe
    cur.execute("""
    SELECT COUNT(*), SUM(cnt) FROM (
        SELECT filename, file_size, COUNT(*) as cnt 
        FROM master_audio_catalog 
        WHERE is_corrupted_or_zero = 0
        GROUP BY filename, file_size
        HAVING COUNT(*) > 1
    )
    """)
    t0_groups, total_in_dupes = cur.fetchone()
    
    # 4. Total unique tracks if we collapse Tier-0 duplicates
    cur.execute("SELECT COUNT(DISTINCT filename || '___' || file_size) FROM master_audio_catalog WHERE is_corrupted_or_zero = 0")
    distinct_unique_tracks = cur.fetchone()[0]
    
    conn.close()
    
    return {
        "drive_stats": drive_stats,
        "zero_byte_or_corrupt_files": zero_bytes,
        "tier0_duplicate_groups": t0_groups,
        "total_files_in_duplicate_clusters": total_in_dupes,
        "redundant_copies_to_bypass": (total_in_dupes - t0_groups) if total_in_dupes and t0_groups else 0,
        "distinct_unique_audio_files": distinct_unique_tracks
    }

if __name__ == "__main__":
    db = r"D:\Code\avinya-forge\auralis\master_cross_drive_catalog.db"
    init_master_db(db)
    
    # Scan drives
    drives_to_scan = [
        ("D", r"D:\Songs\unorganized"),
        ("F", r"F:\Music"),
        ("J", r"J:\Music"),
    ]
    
    for d_letter, path in drives_to_scan:
        if os.path.exists(path):
            scan_drive_files(path, d_letter, db)
            
    print("\n--- Cross-Drive Redundancy Analysis ---")
    res = analyze_cross_drive_redundancy(db)
    import json
    print(json.dumps(res, indent=2))
