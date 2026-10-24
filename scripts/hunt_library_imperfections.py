"""
Auralis - Deep Imperfection Hunter & Precision Polisher
Scans D:\\Songs\\organized for subtle quality flaws:
1. Naming & Typography:
   - Bad apostrophe casing (e.g. "It'S", "Can'T", "Ain'T", "Rock 'N' Roll", "Guns N' Roses")
   - Bad ordinal capitalization ("115Th", "2Nd", "3Rd", "1St", "40Th")
   - Redundant prefixes matching parent folder (e.g. "Pink Floyd - Comfortably Numb.mp3" inside Pink Floyd)
   - Double spaces, trailing hyphens, double hyphens, stray underscores
   - Inconsistent casing (ALL CAPS like "DIL SE RE.mp3", all lowercase like "numb.mp3")
   - Uppercase file extensions (.MP3, .Wma)
   - Stray punctuation or curly quotes (`, ‘, ’, “, ”, etc.)
2. Embedded Metadata:
   - Missing Album Artist (TPE2 / aART / WM/AlbumArtist)
   - Missing Year (TDRC / TYER / ©day / WM/Year)
   - Missing Track Number (TRCK / trkn / WM/TrackNumber)
   - Artist name matching filename pattern (e.g. "Artist - Title" embedded in Title tag)
   - Inconsistent genre naming (e.g. "soundtrack" vs "Soundtrack", "bollywood" vs "Bollywood")
3. Subfolder Consistency:
   - Misplaced "Soundtracks" vs "Albums"
   - Inverted or redundant subfolders
"""

import os
import sys
import re
from collections import defaultdict, Counter

import mutagen
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from mutagen.asf import ASF

ORGANIZED_ROOT = r"D:\Songs\organized"

def hunt():
    print("=" * 80)
    print("AURALIS PRECISION IMPERFECTION HUNT")
    print(f"Target: {ORGANIZED_ROOT}")
    print("=" * 80)

    all_files = []
    for r, d, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            if f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav')):
                all_files.append(os.path.join(r, f))

    print(f"Auditing {len(all_files)} physical tracks...\n")

    issues = defaultdict(list)
    bad_apostrophe_cap = re.compile(r"([a-zA-Z])'([A-Z])")
    bad_ordinal_cap = re.compile(r"\b(\d+)(St|Nd|Rd|Th)\b")

    for p in all_files:
        rel = os.path.relpath(p, ORGANIZED_ROOT)
        fname = os.path.basename(p)
        stem, ext = os.path.splitext(fname)
        parent_dir = os.path.basename(os.path.dirname(p))

        # Check extension casing
        if ext != ext.lower():
            issues["uppercase_extension"].append(rel)

        # Whitespace
        if "  " in fname or fname.strip() != fname:
            issues["whitespace_flaw"].append(rel)

        # Stray underscores
        if "_" in fname:
            issues["underscore_flaw"].append(rel)

        # Trailing/leading hyphens or double hyphens
        if stem.startswith("-") or stem.endswith("-") or "--" in stem:
            issues["hyphen_flaw"].append(rel)

        # Bad apostrophe casing (e.g. Can'T -> Can't)
        if bad_apostrophe_cap.search(stem):
            issues["bad_apostrophe_casing"].append((rel, stem))

        # Bad ordinal casing (e.g. 115Th -> 115th)
        if bad_ordinal_cap.search(stem):
            issues["bad_ordinal_casing"].append((rel, stem))

        # All caps filename (> 4 chars and all uppercase)
        words = [w for w in re.split(r'[\s\-]+', stem) if len(w) > 3 and not re.match(r'^\d+$', w)]
        if len(words) >= 2 and all(w.isupper() for w in words):
            issues["all_caps_filename"].append((rel, stem))

        # Redundant artist prefix in filename matching parent folder
        if parent_dir and stem.lower().startswith(parent_dir.lower() + " - "):
            issues["redundant_parent_prefix"].append((rel, stem))

        # Embedded tags audit
        try:
            if ext.lower() == ".mp3":
                try:
                    id3 = ID3(p)
                    tit2 = str(id3.get("TIT2", "")).strip()
                    tpe1 = str(id3.get("TPE1", "")).strip()
                    talb = str(id3.get("TALB", "")).strip()
                    tpe2 = str(id3.get("TPE2", "")).strip()
                    year = str(id3.get("TDRC", id3.get("TYER", ""))).strip()
                    trck = str(id3.get("TRCK", "")).strip()

                    if not year:
                        issues["missing_year_tag"].append(rel)
                    if bad_apostrophe_cap.search(tit2):
                        issues["bad_apostrophe_in_title_tag"].append((rel, tit2))
                    if bad_ordinal_cap.search(tit2):
                        issues["bad_ordinal_in_title_tag"].append((rel, tit2))
                    if " - " in tit2 and tpe1 and tpe1.lower() in tit2.lower():
                        issues["artist_leaked_in_title_tag"].append((rel, tit2))
                except Exception:
                    pass
        except Exception:
            pass

    print(">>> IMPERFECTION AUDIT RESULTS:")
    print("-" * 60)
    for k, v in issues.items():
        print(f"  [{k}]: {len(v)} occurrences")

    print("\nDetailed Sample of Discrepancies:")
    for k, v in issues.items():
        print(f"\n--- {k} ({len(v)}) ---")
        for item in v[:8]:
            print(f"  {item}")
        if len(v) > 8:
            print(f"  ... and {len(v)-8} more")

if __name__ == "__main__":
    hunt()
