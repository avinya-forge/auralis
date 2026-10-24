"""
Auralis - Demo File Journey & Dry-Run Pipeline
Demonstrates the complete, auditable lifecycle of music tracks from unorganized source
to verified, deduplicated, and tag-corrected organized destination.
"""

import os
import sys
import re
import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Tuple
from pathlib import Path
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.discovery_inventory import compute_fast_hash, extract_track_info, detect_language_heuristic

def clean_title_and_artist(raw_name: str, existing_artist: str = "", existing_title: str = "") -> Tuple[str, str, str]:
    """
    Cleans junk web watermarks, track numbers, and parses (Artist, Title, Album/Movie).
    Handles patterns like:
      - '04 - Murder 2 (2011) - Phir Mohabbat [www.DJLUV.in].mp3'
      - '001 AAH = YE SHAAM KI TANHAIYAN.mp3'
      - 'Till Kingdom Come - Coldplay.mp3'
      - '05bhavanyashtakam-shri aadi shankaracharya.mp3'
    """
    stem = os.path.splitext(raw_name)[0]
    
    # 1. Strip common web watermarks & bitrate badges
    junk_patterns = [
        r"\[.*?djluv.*?\]", r"\[.*?songs\.pk.*?\]", r"\[.*?bindassbuzz.*?\]",
        r"\[.*?mp3.*?\]", r"\[.*?128kbps.*?\]", r"\[.*?320kbps.*?\]",
        r"www\.[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,4}", r"\(.*?mp3.*?\)",
        r"_www\.[a-zA-Z0-9_\-\.]+",
    ]
    cleaned = stem
    for pat in junk_patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    
    cleaned = cleaned.replace("_", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    
    artist = existing_artist.strip() if existing_artist else ""
    title = existing_title.strip() if existing_title else ""
    album = ""
    
    # Pattern A: '001 AAH = YE SHAAM KI TANHAIYAN' (Movie = Song)
    if "=" in cleaned:
        parts = cleaned.split("=", 1)
        # Strip leading numbers
        movie_part = re.sub(r"^\d+[\s\.\-_]*", "", parts[0]).strip()
        song_part = parts[1].strip()
        album = movie_part.title()
        title = song_part.title()
        if not artist:
            artist = "Bollywood Classics"
        return artist, title, album

    # Pattern B: '04 - Murder 2 (2011) - Phir Mohabbat' (Track - Movie (Year) - Song)
    dash_parts = [p.strip() for p in cleaned.split(" - ") if p.strip()]
    if len(dash_parts) == 3 and re.match(r"^\d+$", dash_parts[0]):
        album = dash_parts[1].title()
        title = dash_parts[2].title()
        if not artist:
            artist = "Bollywood"
        return artist, title, album
        
    # Pattern C: 'Till Kingdom Come - Coldplay' or 'Coldplay - Till Kingdom Come'
    if len(dash_parts) == 2:
        part1 = re.sub(r"^\d+[\s\.\-_]*", "", dash_parts[0]).strip().title()
        part2 = dash_parts[1].strip().title()
        if not artist:
            artist = part2
            title = part1
        elif not title:
            title = part1
        return artist, title, album

    # Pattern D: Devotional with hyphen: '05bhavanyashtakam-shri aadi shankaracharya'
    if "-" in cleaned and not dash_parts:
        subparts = cleaned.split("-", 1)
        title = re.sub(r"^\d+[\s\.\-_]*", "", subparts[0]).strip().title()
        artist = subparts[1].strip().title()
        return artist, title, album

    # Fallback: clean track number from stem
    clean_stem = re.sub(r"^\d+[\s\.\-_]*", "", cleaned).strip().title()
    if not title:
        title = clean_stem
    if not artist:
        artist = "Unknown Artist"
        
    return artist, title, album

def simulate_file_journey(sample_files: List[str], target_base: str = r"D:\Songs\organized") -> Dict[str, Any]:
    """Simulates the 7-stage journey for a batch of sample files."""
    journey_log = []
    seen_hashes: Dict[str, Dict[str, Any]] = {}
    
    unique_count = 0
    duplicate_count = 0
    
    for idx, path in enumerate(sample_files, start=1):
        filename = os.path.basename(path)
        raw_info = extract_track_info(path)
        f_hash = compute_fast_hash(path)
        
        # Stage 1 & 2: Clean and extract tags
        artist, title, album = clean_title_and_artist(filename, raw_info["artist"], raw_info["title"])
        album = album or raw_info["album"]
        
        # Stage 3: Deduplication Evaluation
        is_duplicate = False
        keeper_path = path
        dedupe_action = "KEEP_PRIMARY"
        
        if f_hash in seen_hashes:
            is_duplicate = True
            duplicate_count += 1
            existing = seen_hashes[f_hash]
            dedupe_action = f"DUPLICATE_OF: {existing['filename']}"
            target_dest = os.path.join(target_base, "_duplicates_quarantine", filename)
        else:
            unique_count += 1
            seen_hashes[f_hash] = {
                "path": path,
                "filename": filename,
                "bitrate": raw_info["bitrate"],
                "size": raw_info["file_size"]
            }
            # Stage 4: Language Classification
            lang = detect_language_heuristic(path, artist, title, album)
            
            # Stage 5: Shallow 3-Level Path
            subfolder = artist if artist and artist != "Unknown Artist" else "General"
            if lang in ["Sanskrit", "Pravachan"]:
                subfolder = "Devotional" if lang == "Sanskrit" else "Discourses"
                
            clean_filename = f"{title}.mp3" if title else filename
            target_dest = os.path.join(target_base, lang, subfolder, clean_filename)

        journey_step = {
            "step_id": idx,
            "source_file": filename,
            "source_path": path,
            "source_duration_s": raw_info["duration"],
            "source_bitrate_kbps": round(raw_info["bitrate"] / 1000) if raw_info["bitrate"] else "Unknown",
            "detected_language": detect_language_heuristic(path, artist, title, album),
            "parsed_metadata": {
                "title": title,
                "artist": artist,
                "album": album or "N/A"
            },
            "dedupe_verdict": dedupe_action,
            "target_destination": target_dest,
            "max_folder_depth": len(Path(target_dest).relative_to(target_base).parts)
        }
        journey_log.append(journey_step)
        
    return {
        "batch_size": len(sample_files),
        "unique_tracks": unique_count,
        "duplicates_identified": duplicate_count,
        "journey_records": journey_log
    }

if __name__ == "__main__":
    conn = sqlite3.connect(r"D:\Code\avinya-forge\auralis\auralis_inventory.db")
    cur = conn.cursor()
    
    # Select sample files representing Hindi, Marathi, Sanskrit, English, and duplicates
    sample_paths = []
    
    # 1. Get known duplicate pairs
    cur.execute("""
    SELECT GROUP_CONCAT(file_path, '|||') 
    FROM audio_inventory 
    GROUP BY file_hash 
    HAVING COUNT(*) > 1 
    LIMIT 4
    """)
    for (group_paths,) in cur.fetchall():
        sample_paths.extend(group_paths.split("|||"))
        
    # 2. Add Hindi, Marathi, English, Sanskrit samples
    for lang in ["Hindi", "Marathi", "English", "Sanskrit"]:
        cur.execute("SELECT file_path FROM audio_inventory WHERE detected_language = ? LIMIT 5", (lang,))
        sample_paths.extend([r[0] for r in cur.fetchall()])
        
    conn.close()
    
    # Limit sample batch to 30 files for clean demonstration
    sample_paths = sample_paths[:30]
    result = simulate_file_journey(sample_paths)
    
    out_file = r"D:\Code\avinya-forge\auralis\demo_journey_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"[*] Demo Journey simulation completed for {len(sample_paths)} files.")
    print(f"[*] Report saved to {out_file}")
    print(f"[*] Summary: {result['unique_tracks']} Unique tracks, {result['duplicates_identified']} Duplicates quarantined.")
    print(f"[*] Sample Journey Output:")
    for rec in result["journey_records"][:6]:
        print(f"\n[{rec['step_id']}] File: {rec['source_file']}")
        print(f"    Tags: Title='{rec['parsed_metadata']['title']}', Artist='{rec['parsed_metadata']['artist']}'")
        print(f"    Lang: {rec['detected_language']} | Dedupe: {rec['dedupe_verdict']}")
        print(f"    Target (Depth {rec['max_folder_depth']}): {rec['target_destination']}")
