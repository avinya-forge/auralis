"""
Audit Entire Organized Library for:
1. Redundant Artist Prefixes in artist/movie directories
2. Cryptic filenames (<= 3 chars, single digits, 'Unknown', 'Piste')
3. Intra-folder duplicates (via NLP title canonicalization + duration match)
"""

import os
import sys
import re
from collections import defaultdict
import mutagen

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ORGANIZED = r"D:\Songs\organized"

def canonical_nlp_title(name: str) -> str:
    s = os.path.splitext(name)[0].lower()
    # Normalize common spelling/phonetic variants
    s = s.replace("whisky", "whiskey")
    s = s.replace("colour", "color")
    s = s.replace("the wall part ii", "the wall part 2")
    # Strip rip/quality tags
    s = re.sub(r"\b(mp3|320kbps|128kbps|remastered|version|original|live)\b", "", s)
    # Strip part suffixes for matching
    s = re.sub(r"\s*-\s*part\s*\d+", "", s)
    s = re.sub(r"\s+no\.?\s*\d*", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def scan_library():
    redundant_prefixes = []
    cryptic_files = []
    intra_folder_duplicates = defaultdict(list)
    total_files = 0

    for root, dirs, files in os.walk(ORGANIZED):
        rel = os.path.relpath(root, ORGANIZED)
        parts = rel.split(os.sep)
        curr_folder = parts[-1] if parts else ""

        folder_groups = defaultdict(list)
        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac')):
                continue
            total_files += 1
            fp = os.path.join(root, f)
            stem, ext = os.path.splitext(f)

            # 1. Check Redundant Artist Prefix
            clean_folder_lower = re.sub(r"[^a-z0-9]", "", curr_folder.lower())
            clean_stem_lower = re.sub(r"[^a-z0-9]", "", stem.lower())
            if len(clean_folder_lower) > 3:
                # Check if file begins with folder name
                if stem.lower().startswith(curr_folder.lower() + " -") or stem.lower().startswith(curr_folder.lower() + "-") or stem.lower().startswith("artist - " + curr_folder.lower()):
                    redundant_prefixes.append((fp, curr_folder, f))

            # 2. Check Cryptic Filenames
            if len(stem) <= 3 or stem.isdigit() or any(w in stem.lower() for w in ['unknown', 'piste', 'audiotrack', 'track0', 'track1', 'track2']):
                cryptic_files.append((fp, curr_folder, f))

            # 3. Check Intra-folder Duplicates
            try:
                mf = mutagen.File(fp)
                dur = round(getattr(mf.info, "length", 0)) if mf else 0
            except Exception:
                dur = 0
            canon = canonical_nlp_title(stem)
            # Group by canonical title and 4-second duration bucket
            dur_bucket = round(dur / 4) * 4
            folder_groups[(canon, dur_bucket)].append((f, dur, os.path.getsize(fp), fp))

        for (canon, dur_bucket), members in folder_groups.items():
            if len(members) > 1 and len(canon) > 3:
                intra_folder_duplicates[rel].append((canon, dur_bucket, members))

    print("=== LIBRARY AUDIT SUMMARY ===")
    print(f"Total audio files scanned: {total_files}")
    print(f"Redundant Artist/Folder Prefixes: {len(redundant_prefixes)}")
    print(f"Cryptic Filenames found: {len(cryptic_files)}")
    total_dups = sum(sum(len(m[2]) - 1 for m in group) for group in intra_folder_duplicates.values())
    print(f"Intra-Folder Duplicate Tracks: {total_dups} across {len(intra_folder_duplicates)} folders")

    print("\nSample Redundant Prefixes (First 10):")
    for fp, folder, f in redundant_prefixes[:10]:
        print(f"  [{folder}] -> {f}")

    print("\nSample Cryptic Files (First 10):")
    for fp, folder, f in cryptic_files[:10]:
        print(f"  [{folder}] -> {f}")

    print("\nSample Intra-Folder Duplicate Groups (First 5 folders):")
    for folder, groups in list(intra_folder_duplicates.items())[:5]:
        print(f"  FOLDER: {folder}")
        for canon, dur_b, members in groups[:2]:
            print(f"    Match \"{canon}\" (~{dur_b}s):")
            for m in members:
                print(f"      {m[0]} (dur: {m[1]}s, size: {m[2]})")

if __name__ == "__main__":
    scan_library()
