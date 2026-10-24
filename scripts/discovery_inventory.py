"""
Auralis - Global Discovery & Inventory Scanner
Scans music across specified directories, creates an inventory catalog (JSON + SQLite),
and identifies exact duplicate clusters non-destructively.
"""

import os
import sys
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AUDIO_EXTS = {".mp3", ".flac", ".m4a", ".wav", ".wma", ".ogg", ".aac", ".aiff"}

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audio_inventory (
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
        status TEXT DEFAULT 'DISCOVERED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hash ON audio_inventory(file_hash)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_size ON audio_inventory(file_size)")
    conn.commit()
    conn.close()

def compute_fast_hash(file_path: str, block_size: int = 131072) -> Optional[str]:
    """Compute fast hash of header + sample + trailer to identify identical files rapidly."""
    try:
        size = os.path.getsize(file_path)
        hasher = hashlib.md5(usedforsecurity=False)
        with open(file_path, "rb") as f:
            if size <= block_size * 3:
                hasher.update(f.read())
            else:
                hasher.update(f.read(block_size))
                f.seek(size // 2)
                hasher.update(f.read(block_size))
                f.seek(max(0, size - block_size))
                hasher.update(f.read(block_size))
        return f"{size}_{hasher.hexdigest()}"
    except Exception:
        return None

def extract_track_info(file_path: str) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "file_path": file_path,
        "filename": os.path.basename(file_path),
        "extension": os.path.splitext(file_path)[1].lower(),
        "file_size": os.path.getsize(file_path),
        "duration": 0.0,
        "bitrate": 0,
        "artist": "",
        "title": "",
        "album": "",
        "genre": "",
        "year": "",
    }
    
    try:
        audio = mutagen.File(file_path)
        if audio is not None:
            if hasattr(audio, "info") and audio.info:
                dur = getattr(audio.info, "length", 0.0)
                br = getattr(audio.info, "bitrate", 0)
                info["duration"] = float(round(dur, 2)) if isinstance(dur, (int, float)) else 0.0
                info["bitrate"] = int(br) if isinstance(br, (int, float)) else 0
                
            # If MP3 and length was 0, retry with MP3 parser
            if info["duration"] == 0 and info["extension"] == ".mp3":
                try:
                    mp3_audio = MP3(file_path)
                    info["duration"] = float(round(mp3_audio.info.length, 2)) if hasattr(mp3_audio.info, "length") and isinstance(mp3_audio.info.length, (int, float)) else 0.0
                    info["bitrate"] = int(mp3_audio.info.bitrate) if hasattr(mp3_audio.info, "bitrate") and isinstance(mp3_audio.info.bitrate, (int, float)) else 0
                except Exception:
                    info["duration"] = 0.0
                    info["bitrate"] = 0

            tags = audio.tags
            if tags:
                # Helper for ID3 / Vorbis
                def get_tag(*keys):
                    for k in keys:
                        if k in tags:
                            val = tags[k]
                            if isinstance(val, (list, tuple)) and val:
                                return str(val[0]).strip()
                            return str(val).strip()
                    return ""
                
                info["artist"] = get_tag("TPE1", "artist", "Author", "WM/AlbumArtist")
                info["title"] = get_tag("TIT2", "title", "Title", "WM/Title")
                info["album"] = get_tag("TALB", "album", "WM/AlbumTitle")
                info["genre"] = get_tag("TCON", "genre", "WM/Genre")
                info["year"] = get_tag("TDRC", "date", "year", "WM/Year")
    except Exception as e:
        info["error"] = str(e)
        
    return info

def detect_language_heuristic(file_path: str, title: str, artist: str, album: str) -> str:
    """Accurate language classifier combining path cues, unicode, and pattern classifier."""
    from src.engine.pattern_classifier import detect_language_and_category
    filename = os.path.basename(file_path)
    lang, _ = detect_language_and_category(file_path, filename, artist)
    return lang

def run_inventory_scan(roots: List[str], db_path: str, max_files_per_root: Optional[int] = None) -> Dict[str, Any]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    total_scanned = 0
    start_time = time.time()
    discovered_records = []
    
    print(f"[*] Starting Inventory Scan across {len(roots)} roots...")
    for root in roots:
        if not os.path.exists(root):
            print(f"[!] Warning: Path does not exist: {root}")
            continue
            
        print(f"[*] Scanning: {root}")
        count_in_root = 0
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in AUDIO_EXTS:
                    full_path = os.path.join(dirpath, fname)
                    total_scanned += 1
                    count_in_root += 1
                    
                    info = extract_track_info(full_path)
                    f_hash = compute_fast_hash(full_path)
                    lang = detect_language_heuristic(full_path, info["artist"], info["title"], info["album"])
                    
                    # Generate shallow target path (Max 3 levels: Root/Language/Artist_or_Category/Filename)
                    subcat = info["artist"] or "General"
                    if lang in ["Sanskrit", "Pravachan"]:
                        subcat = "Devotional" if lang == "Sanskrit" else "Discourses"
                    target_filename = info["filename"]
                    suggested_target = os.path.join(r"D:\Songs\organized", lang, subcat, target_filename)
                    
                    cur.execute("""
                    INSERT OR REPLACE INTO audio_inventory 
                    (file_path, filename, extension, file_size, duration, bitrate, file_hash, artist, title, album, genre, year, detected_language, suggested_target_path, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DISCOVERED')
                    """, (
                        full_path, fname, ext, info["file_size"], info["duration"], info["bitrate"],
                        f_hash, info["artist"], info["title"], info["album"], info["genre"], info["year"],
                        lang, suggested_target
                    ))
                    
                    discovered_records.append({
                        "file_path": full_path,
                        "filename": fname,
                        "size": info["file_size"],
                        "duration": info["duration"],
                        "bitrate": info["bitrate"],
                        "hash": f_hash,
                        "artist": info["artist"],
                        "title": info["title"],
                        "language": lang,
                        "suggested_target": suggested_target
                    })
                    
                    if total_scanned % 500 == 0:
                        conn.commit()
                        print(f"    Processed {total_scanned} files...")
                        
                    if max_files_per_root and count_in_root >= max_files_per_root:
                        break
            if max_files_per_root and count_in_root >= max_files_per_root:
                break
                
    conn.commit()
    elapsed = round(time.time() - start_time, 2)
    
    # Query duplicate clusters
    cur.execute("""
    SELECT file_hash, COUNT(*), GROUP_CONCAT(file_path, ' ||| ') 
    FROM audio_inventory 
    WHERE file_hash IS NOT NULL 
    GROUP BY file_hash 
    HAVING COUNT(*) > 1
    """)
    duplicate_rows = cur.fetchall()
    
    cur.execute("SELECT detected_language, COUNT(*) FROM audio_inventory GROUP BY detected_language")
    lang_dist = dict(cur.fetchall())
    
    conn.close()
    
    report = {
        "total_audio_files_cataloged": total_scanned,
        "elapsed_seconds": elapsed,
        "duplicate_hash_clusters_found": len(duplicate_rows),
        "language_distribution": lang_dist,
        "database_file": db_path
    }
    
    return report

if __name__ == "__main__":
    scan_roots = [
        r"D:\Songs\unorganized\BMW-Music",
        r"D:\Songs\unorganized\Incoming_Chunk_F",
    ]
    db_out = r"D:\Code\avinya-forge\auralis\auralis_inventory.db"
    json_out = r"D:\Code\avinya-forge\auralis\music_inventory_catalog.json"
    
    print(r"[*] Running inventory scan across active unorganized directories...")
    stats = run_inventory_scan(scan_roots, db_out)
    
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print("\n--- Scan Summary ---")
    print(json.dumps(stats, indent=2))
