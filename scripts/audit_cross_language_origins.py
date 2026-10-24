"""
Auralis - Origin vs Target Cross-Language & Cross-Genre Auditor
Compares the raw origin path of each file in D:\\Songs\\organized (from auralis_inventory.db)
with its current location in D:\\Songs\\organized to find any mismatched tracks
(e.g. Marathi files placed in Hindi or English, English files in Hindi, etc.)
"""

import os
import sys
import sqlite3
from collections import defaultdict

ORGANIZED_ROOT = r"D:\Songs\organized"
DB_PATH = "auralis_inventory.db"

def audit_origins():
    print("Connecting to auralis_inventory.db...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_path, file_size, filename, title, artist, album FROM audio_inventory")
    inventory = c.fetchall()
    conn.close()

    # Index by file size
    size_to_orig = defaultdict(list)
    for row in inventory:
        size_to_orig[row[1]].append(row)

    print(f"Indexed {len(inventory)} inventory records across {len(size_to_orig)} distinct sizes.")

    mismatches = []
    total_checked = 0

    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav')):
                continue
            total_checked += 1
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            rel_target = os.path.relpath(p, ORGANIZED_ROOT)
            target_lang = rel_target.split(os.sep)[0]

            # Check if we have exact file_size matches in inventory
            orig_candidates = size_to_orig.get(sz, [])
            if len(orig_candidates) == 1:
                orig = orig_candidates[0]
                orig_path = orig[0]
                orig_parts = orig_path.replace("/", "\\").split("\\")

                # Detect language in original path
                orig_lang = None
                for part in orig_parts:
                    if part.lower() in ["marathi", "hindi", "english", "sanskrit", "pravachan", "ringtones"]:
                        orig_lang = part.capitalize()
                        if orig_lang == "Ringtones":
                            orig_lang = "Ringtones & Alerts"
                        break

                if orig_lang and orig_lang != target_lang:
                    # Ignore if deliberate reassignment (e.g. Sanskrit from Morning)
                    mismatches.append({
                        "organized_path": rel_target,
                        "orig_path": orig_path,
                        "orig_lang": orig_lang,
                        "target_lang": target_lang,
                        "size": sz,
                        "orig_filename": orig[2],
                        "orig_title": orig[3]
                    })

    print(f"\nAudited {total_checked} organized tracks.")
    print(f"Found {len(mismatches)} potential origin language mismatches:\n")

    for m in mismatches:
        print(f"  [ORIG: {m['orig_lang']} -> TARGET: {m['target_lang']}]")
        print(f"    Orig:   {m['orig_path']}")
        print(f"    Target: {m['organized_path']}\n")

if __name__ == "__main__":
    audit_origins()
