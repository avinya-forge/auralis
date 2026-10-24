"""
Auralis - Clean Pink Floyd Master Directory
1. Renames Greatest Guitar Solos - Pink Floyd - Money.mp3 -> Money.mp3
2. Renames live album collision tracks (- Part 2.mp3) -> - Live.mp3 with updated ID3 tags
3. Archives redundant duplicate Pink Floyd.mp3 to _duplicates_backup
"""

import os
import sys
import re
import shutil
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PF_DIR = r"D:\Songs\organized\English\Pink Floyd"
DUPLICATES_BACKUP = r"D:\Songs\unorganized\_duplicates_backup"

def clean_pink_floyd():
    os.makedirs(DUPLICATES_BACKUP, exist_ok=True)

    # 1. Money
    money_old = os.path.join(PF_DIR, "Greatest Guitar Solos - Pink Floyd - Money.mp3")
    money_new = os.path.join(PF_DIR, "Money.mp3")
    if os.path.exists(money_old):
        shutil.move(money_old, money_new)
        audio = ID3(money_new)
        audio["TIT2"] = TIT2(encoding=3, text="Money")
        audio["TPE1"] = TPE1(encoding=3, text="Pink Floyd")
        audio["TALB"] = TALB(encoding=3, text="The Dark Side of the Moon")
        audio.save(money_new, v2_version=3)
        print("Cleaned Money.mp3")

    # 2. Pink Floyd.mp3
    pf_dup = os.path.join(PF_DIR, "Pink Floyd.mp3")
    if os.path.exists(pf_dup):
        shutil.move(pf_dup, os.path.join(DUPLICATES_BACKUP, "Pink Floyd - Another Brick Part 2 - Duplicate.mp3"))
        print("Archived redundant Pink Floyd.mp3")

    # 3. Live tracks
    for f in os.listdir(PF_DIR):
        if "- part 2.mp3" in f.lower():
            old_p = os.path.join(PF_DIR, f)
            base_name = re.sub(r"\s*-\s*part\s*2\.mp3$", "", f, flags=re.I)
            new_f = f"{base_name} - Live.mp3"
            new_p = os.path.join(PF_DIR, new_f)

            if os.path.exists(new_p):
                # Duplicate copy, move to archive
                shutil.move(old_p, os.path.join(DUPLICATES_BACKUP, f"Pink Floyd_{f}"))
                print(f"Archived duplicate: {f}")
            else:
                shutil.move(old_p, new_p)
                try:
                    audio = ID3(new_p)
                    audio["TIT2"] = TIT2(encoding=3, text=f"{base_name} Live")
                    audio["TPE1"] = TPE1(encoding=3, text="Pink Floyd")
                    audio["TALB"] = TALB(encoding=3, text="Pulse Live")
                    audio.save(new_p, v2_version=3)
                except Exception:
                    pass
                print(f"Renamed live track: {f} -> {new_f}")

if __name__ == "__main__":
    clean_pink_floyd()
