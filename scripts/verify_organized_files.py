"""
Auralis - Complete Multi-Loop Verification Engine for D:\\Songs\\organized
Executes 5 deterministic verification loops across all physical files in D:\\Songs\\organized:
- Loop 1: Physical Stream & Header Integrity (zero-byte, corruption, unreadable headers, 0-duration)
- Loop 2: Filesystem Path & Hierarchy Sanitization (brackets, illegal symbols, repeated prefixes)
- Loop 3: Embedded Metadata & Tag Quality (missing tags, generic titles, spam watermarks/URLs)
- Loop 4: Linguistic & Categorical Placement (misplaced genres/languages, catch-all buckets)
- Loop 5: Quality-Aware Stream Duplication (identical audio streams sitting in organized)
"""

import os
import sys
import re
import json
import hashlib
from collections import defaultdict, Counter
from typing import Dict, Any, List, Tuple

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.pattern_classifier import (
    clean_watermarks, clean_name, detect_language_and_category,
    extract_bollywood_movie_and_song, SUKTA_PATTERNS, STOTRA_PATTERNS
)
from src.engine.pravachan_resolver import resolve_pravachan_track
from src.engine.catalog_resolver import lookup_catalog_track

ORGANIZED_ROOT = r"D:\Songs\organized"

def compute_audio_stream_hash(file_path: str) -> str:
    """Computes MD5 hash of raw audio stream payload ignoring ID3 / container header variance."""
    try:
        sz = os.path.getsize(file_path)
        if sz == 0:
            return ""
        ext = os.path.splitext(file_path)[1].lower()
        tag_size = 0
        if ext == ".mp3":
            try:
                audio = MP3(file_path)
                tag_size = audio.tags.size if audio.tags else 0
            except Exception:
                tag_size = 0
        
        hasher = hashlib.md5()
        with open(file_path, "rb") as fp:
            fp.seek(tag_size)
            while chunk := fp.read(131072):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def run_verification_pipeline() -> Dict[str, Any]:
    print("=" * 80)
    print(f"STARTING COMPREHENSIVE MULTI-LOOP VERIFICATION ON: {ORGANIZED_ROOT}")
    print("=" * 80)

    all_files = []
    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            if f.lower().endswith(('.mp3', '.wma', '.wav', '.m4a', '.ogg', '.flac')):
                all_files.append(os.path.join(root, f))

    total_files = len(all_files)
    print(f"\nFound {total_files} audio files to verify.\n")

    # =========================================================================
    # LOOP 1: Physical Stream & Header Integrity
    # =========================================================================
    print(">>> RUNNING LOOP 1: Physical Stream & Audio Integrity Check...")
    zero_byte_files = []
    unreadable_files = []
    zero_duration_files = []
    low_bitrate_files = []
    format_counts = Counter()
    file_metadata = {}

    for p in all_files:
        ext = os.path.splitext(p)[1].lower()
        format_counts[ext] += 1
        sz = os.path.getsize(p)
        if sz == 0:
            zero_byte_files.append(p)
            continue

        try:
            mf = mutagen.File(p)
            if mf is None or mf.info is None:
                unreadable_files.append((p, "mutagen.File returned None"))
                continue
            dur = getattr(mf.info, "length", 0.0)
            br = getattr(mf.info, "bitrate", 0) // 1000 if getattr(mf.info, "bitrate", 0) else 128
            sr = getattr(mf.info, "sample_rate", 0)

            if dur <= 0:
                zero_duration_files.append((p, dur))

            if br > 0 and br < 64:
                low_bitrate_files.append((p, br))

            # Read embedded tags
            tag_title = ""
            tag_artist = ""
            tag_album = ""
            tag_genre = ""
            if ext == ".mp3":
                try:
                    id3 = ID3(p)
                    tag_title = str(id3.get("TIT2", ""))
                    tag_artist = str(id3.get("TPE1", ""))
                    tag_album = str(id3.get("TALB", ""))
                    tag_genre = str(id3.get("TCON", ""))
                except Exception:
                    pass
            elif ext == ".wma":
                try:
                    asf = mutagen.File(p)
                    if asf and asf.tags:
                        tag_title = str(asf.tags.get("Title", [""])[0])
                        tag_artist = str(asf.tags.get("Author", [""])[0])
                        tag_album = str(asf.tags.get("WM/AlbumTitle", [""])[0])
                        tag_genre = str(asf.tags.get("WM/Genre", [""])[0])
                except Exception:
                    pass
            elif ext == ".m4a":
                try:
                    mp4 = mutagen.File(p)
                    if mp4 and mp4.tags:
                        tag_title = str(mp4.tags.get("\xa9nam", [""])[0]) if mp4.tags.get("\xa9nam") else ""
                        tag_artist = str(mp4.tags.get("\xa9ART", [""])[0]) if mp4.tags.get("\xa9ART") else ""
                        tag_album = str(mp4.tags.get("\xa9alb", [""])[0]) if mp4.tags.get("\xa9alb") else ""
                        tag_genre = str(mp4.tags.get("\xa9gen", [""])[0]) if mp4.tags.get("\xa9gen") else ""
                except Exception:
                    pass
            elif ext == ".wav":
                try:
                    wav = mutagen.File(p)
                    if wav and wav.tags:
                        tag_title = str(wav.tags.get("TIT2", ""))
                        tag_artist = str(wav.tags.get("TPE1", ""))
                        tag_album = str(wav.tags.get("TALB", ""))
                        tag_genre = str(wav.tags.get("TCON", ""))
                except Exception:
                    pass

            file_metadata[p] = {
                "size_bytes": sz,
                "duration": dur,
                "bitrate": br,
                "sample_rate": sr,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
                "tag_genre": tag_genre,
            }
        except Exception as e:
            unreadable_files.append((p, str(e)))

    loop1_report = {
        "total_files": total_files,
        "format_distribution": dict(format_counts),
        "zero_byte_count": len(zero_byte_files),
        "unreadable_count": len(unreadable_files),
        "zero_duration_count": len(zero_duration_files),
        "low_bitrate_count": len(low_bitrate_files),
        "integrity_pass_rate": f"{(1 - (len(zero_byte_files) + len(unreadable_files) + len(zero_duration_files)) / total_files) * 100:.2f}%"
    }
    print(f"  [Loop 1 Complete] Zero-Byte: {len(zero_byte_files)} | Corrupted: {len(unreadable_files)} | Zero-Duration: {len(zero_duration_files)}")
    print(f"  [Loop 1 Complete] Physical Integrity Pass Rate: {loop1_report['integrity_pass_rate']}")

    # =========================================================================
    # LOOP 2: Filesystem Path & Hierarchy Sanitization Check
    # =========================================================================
    print("\n>>> RUNNING LOOP 2: Filesystem Path & Naming Sanitization Check...")
    bracket_path_files = []
    symbol_path_files = []
    repeated_prefix_files = []
    long_path_files = []

    symbol_regex = re.compile(r'[\$\%\!\@\~\+\^\=\;\`\#]')

    for p in all_files:
        rel_path = os.path.relpath(p, ORGANIZED_ROOT)
        filename = os.path.basename(p)

        # Check brackets
        if any(c in rel_path for c in ['(', ')', '[', ']', '{', '}']):
            bracket_path_files.append(rel_path)

        # Check dirty symbols
        if symbol_regex.search(rel_path):
            symbol_path_files.append(rel_path)

        # Check repeated prefixes
        stem = os.path.splitext(filename)[0]
        if re.search(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*-\s*", stem, flags=re.I) or re.search(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*$", stem, flags=re.I):
            repeated_prefix_files.append(rel_path)

        # Check Windows MAX_PATH (260 chars)
        if len(p) >= 260:
            long_path_files.append((rel_path, len(p)))

    loop2_report = {
        "bracket_path_violations": len(bracket_path_files),
        "symbol_violations": len(symbol_path_files),
        "repeated_prefix_violations": len(repeated_prefix_files),
        "long_path_violations": len(long_path_files)
    }
    print(f"  [Loop 2 Complete] Bracket Violations: {len(bracket_path_files)}")
    print(f"  [Loop 2 Complete] Dirty Symbol Violations: {len(symbol_path_files)}")
    print(f"  [Loop 2 Complete] Repeated Prefix Violations: {len(repeated_prefix_files)}")
    print(f"  [Loop 2 Complete] Windows Long Path (>=260): {len(long_path_files)}")

    # =========================================================================
    # LOOP 3: Embedded Metadata & Tag Quality Check
    # =========================================================================
    print("\n>>> RUNNING LOOP 3: Embedded Metadata & Tag Quality Check...")
    missing_title_tags = []
    generic_title_tags = []
    watermarked_tags = []
    watermark_re = re.compile(r'\b(www\.[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-\.]+\.(com|pk|in|net|org)|songs\.pk|djluv|papuyaar|apniisp|downloadming)\b', re.I)

    for p in all_files:
        meta = file_metadata.get(p, {})
        tag_t = meta.get("tag_title", "").strip()
        tag_a = meta.get("tag_artist", "").strip()
        tag_alb = meta.get("tag_album", "").strip()
        rel_p = os.path.relpath(p, ORGANIZED_ROOT)

        if not tag_t:
            missing_title_tags.append(rel_p)
        elif re.match(r"^(track|audio|title|song)?[\s_-]*\d+(\s*\(\d+\))?(_\d+)?$", tag_t.lower()):
            # Exempt Blur's iconic track titled "Song 2"
            if tag_t.lower() == "song 2" and "Blur" in (tag_a or rel_p):
                pass
            elif tag_t.lower() == "song 2" and "Assorted Pop & Rock" in rel_p:
                pass
            else:
                generic_title_tags.append((rel_p, tag_t))

        # Check watermarks in tags
        comb_tags = f"{tag_t} {tag_a} {tag_alb}"
        if watermark_re.search(comb_tags):
            watermarked_tags.append((rel_p, watermark_re.search(comb_tags).group(0)))

    loop3_report = {
        "missing_title_tags": len(missing_title_tags),
        "generic_title_tags": len(generic_title_tags),
        "watermarked_tags": len(watermarked_tags)
    }
    print(f"  [Loop 3 Complete] Missing Embedded Titles: {len(missing_title_tags)}")
    print(f"  [Loop 3 Complete] Generic Embedded Titles: {len(generic_title_tags)}")
    print(f"  [Loop 3 Complete] Watermarked / Spam Tags: {len(watermarked_tags)}")

    # =========================================================================
    # LOOP 4: Linguistic & Categorical Placement Check (Cross-Verification)
    # =========================================================================
    print("\n>>> RUNNING LOOP 4: Linguistic & Categorical Placement Check...")
    misplaced_tracks = []
    catch_all_tracks = []
    top_level_distribution = Counter()

    for p in all_files:
        rel_p = os.path.relpath(p, ORGANIZED_ROOT)
        parts = rel_p.split(os.sep)
        top_lang = parts[0]
        top_level_distribution[top_lang] += 1
        fn = os.path.basename(p)
        meta = file_metadata.get(p, {})

        # Catch-all bucket audit
        if "Evergreen Classics" in parts:
            catch_all_tracks.append((rel_p, "Evergreen Classics"))
        elif "Modern Soundtracks" in parts:
            catch_all_tracks.append((rel_p, "Modern Soundtracks"))

        # Misplaced language detection
        # 1. English band inside Hindi folder
        if top_lang == "Hindi":
            if any(b in rel_p.lower() for b in ["disturbed", "beatles", "pink floyd", "nirvana", "coldplay", "u2", "metallica", "green day"]):
                misplaced_tracks.append((rel_p, "English Rock Band inside Hindi folder"))
            elif any(g in rel_p.lower() for g in ["geet ramayan", "marathi", "bhavgeet", "natyasangeet"]):
                misplaced_tracks.append((rel_p, "Marathi Song inside Hindi folder"))
            elif any(pr in rel_p.lower() for pr in ["bhagavad", "ghaisasi", "kavishwar", "abhyankar", "gita00-intro"]):
                misplaced_tracks.append((rel_p, "Pravachan / Katha inside Hindi folder"))
            elif any(rt in rel_p.lower() for rt in ["sony ericsson", "ringtone"]):
                misplaced_tracks.append((rel_p, "Ringtone / Alert tone inside Hindi folder"))

        # 2. Marathi song inside Pravachan folder (e.g. Raghavachi Katha, Swar Gangechya Kathavarti)
        if top_lang == "Pravachan":
            if "raghavachi katha" in fn.lower():
                misplaced_tracks.append((rel_p, "Geet Ramayan song inside Pravachan folder"))
            elif "gangechya katha" in fn.lower():
                misplaced_tracks.append((rel_p, "Marathi Bhavgeet inside Pravachan folder"))

    loop4_report = {
        "top_level_distribution": dict(top_level_distribution),
        "catch_all_bucket_count": len(catch_all_tracks),
        "misplaced_track_count": len(misplaced_tracks),
    }
    print(f"  [Loop 4 Complete] Top-Level Distribution: {dict(top_level_distribution)}")
    print(f"  [Loop 4 Complete] Catch-All Bucket Tracks (Evergreen/Modern): {len(catch_all_tracks)}")
    print(f"  [Loop 4 Complete] Misplaced Cross-Language Tracks: {len(misplaced_tracks)}")

    # =========================================================================
    # LOOP 5: Quality-Aware Stream Duplication Check
    # =========================================================================
    print("\n>>> RUNNING LOOP 5: Quality-Aware Stream Duplication Check...")
    stream_hashes = defaultdict(list)
    for p in all_files:
        h = compute_audio_stream_hash(p)
        if h:
            meta = file_metadata.get(p, {})
            stream_hashes[h].append({
                "path": os.path.relpath(p, ORGANIZED_ROOT),
                "full_path": p,
                "bitrate": meta.get("bitrate", 0),
                "duration": meta.get("duration", 0.0),
                "size_bytes": meta.get("size_bytes", 0)
            })

    duplicate_groups = {h: lst for h, lst in stream_hashes.items() if len(lst) > 1}
    redundant_duplicate_count = sum(len(lst) - 1 for lst in duplicate_groups.values())

    loop5_report = {
        "unique_audio_streams": len(stream_hashes),
        "duplicate_groups": len(duplicate_groups),
        "redundant_files_in_organized": redundant_duplicate_count
    }
    print(f"  [Loop 5 Complete] Unique Audio Streams: {len(stream_hashes)}")
    print(f"  [Loop 5 Complete] Redundant Duplicates Sitting in Organized: {redundant_duplicate_count}")

    # Compile Full Summary
    summary = {
        "loop1_physical_integrity": loop1_report,
        "loop2_path_sanitization": loop2_report,
        "loop3_metadata_quality": loop3_report,
        "loop4_categorical_placement": loop4_report,
        "loop5_stream_duplication": loop5_report,
        "sample_discrepancies": {
            "bracket_paths": bracket_path_files[:10],
            "misplaced_tracks": misplaced_tracks[:15],
            "watermarked_tags": watermarked_tags[:10],
            "catch_all_samples": catch_all_tracks[:10],
            "duplicate_samples": [
                [item["path"] for item in lst] for lst in list(duplicate_groups.values())[:5]
            ]
        }
    }

    report_path = os.path.join(PROJECT_ROOT, "organized_verification_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"MULTI-LOOP VERIFICATION COMPLETE! Full report saved to: {report_path}")
    print("=" * 80)
    return summary

if __name__ == "__main__":
    run_verification_pipeline()
