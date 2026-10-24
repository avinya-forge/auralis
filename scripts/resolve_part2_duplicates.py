"""
Auralis - Resolve Part 2 Collision Duplicates
Retains the highest quality copy (e.g. 320kbps over 128kbps), ensures it has the clean base filename,
and safely moves the inferior duplicate copy to D:\\Songs\\unorganized\\_duplicates_backup.
"""

import os
import sys
import re
import shutil
import mutagen

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.find_part2_dupes import pairs
from src.engine.master_acoustic_organizer import write_id3_metadata

DUPLICATES_BACKUP = r"D:\Songs\unorganized\_duplicates_backup"

def resolve_duplicates():
    resolved_count = 0
    os.makedirs(DUPLICATES_BACKUP, exist_ok=True)

    for rel, f_part2, f_base, d_part2, d_base, sz_part2, sz_base, fp_part2, fp_base in pairs:
        if not os.path.exists(fp_part2) or not os.path.exists(fp_base):
            continue

        # Get bitrates
        try:
            mf_p2 = mutagen.File(fp_part2)
            br_p2 = getattr(mf_p2.info, "bitrate", 0) if mf_p2 else 0
        except Exception:
            br_p2 = 0

        try:
            mf_base = mutagen.File(fp_base)
            br_base = getattr(mf_base.info, "bitrate", 0) if mf_base else 0
        except Exception:
            br_base = 0

        # Determine winner: highest bitrate, then largest file size
        p2_score = (br_p2, sz_part2)
        base_score = (br_base, sz_base)

        archive_sub = os.path.join(DUPLICATES_BACKUP, rel.replace(os.sep, "_"))
        os.makedirs(archive_sub, exist_ok=True)

        if p2_score > base_score:
            # Part 2 is superior quality!
            # Move base to archive
            shutil.move(fp_base, os.path.join(archive_sub, f_base))
            # Rename Part 2 to base filename
            shutil.move(fp_part2, fp_base)
            print(f"[{rel}] Upgraded to superior quality: {f_base} (kept {sz_part2}b, archived {sz_base}b)")
        else:
            # Base is superior or equal quality
            # Move Part 2 to archive
            shutil.move(fp_part2, os.path.join(archive_sub, f_part2))
            print(f"[{rel}] Kept higher quality base: {f_base} (archived {f_part2})")

        resolved_count += 1

    print(f"\nSuccessfully deduplicated and resolved {resolved_count} duplicate pairs!")

if __name__ == "__main__":
    resolve_duplicates()
