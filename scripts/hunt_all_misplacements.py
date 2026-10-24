"""
Auralis - Comprehensive Cross-Language and Misplacement Hunter
Checks every track in D:\\Songs\\organized against ALL candidates in auralis_inventory.db
by matching file size or ID3-stripped audio payload size.
"""

import os
import sys
import json
import sqlite3
import mutagen
from mutagen.mp3 import MP3
from collections import defaultdict

ORGANIZED_ROOT = r"D:\Songs\organized"
DB_PATH = "auralis_inventory.db"

def comprehensive_audit():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_path, file_size, filename, title, artist, album FROM audio_inventory")
    inventory = c.fetchall()
    conn.close()

    # Index by exact file_size
    by_size = defaultdict(list)
    for row in inventory:
        by_size[row[1]].append(row)

    print(f"Loaded {len(inventory)} inventory records across {len(by_size)} distinct sizes.")

    all_mismatches = []
    total_audited = 0

    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav')):
                continue
            total_audited += 1
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            rel_target = os.path.relpath(p, ORGANIZED_ROOT)
            parts = rel_target.split(os.sep)
            target_lang = parts[0]

            # Try exact size match or size - tag_size match
            candidates = by_size.get(sz, [])
            if not candidates and f.lower().endswith('.mp3'):
                try:
                    mp3 = MP3(p)
                    tag_sz = mp3.tags.size if mp3.tags else 0
                    payload_sz = sz - tag_sz
                    candidates = by_size.get(payload_sz, [])
                except Exception:
                    candidates = []

            if candidates:
                # Check the candidate origins
                # Does ANY candidate match target_lang?
                matched_langs = []
                for cand in candidates:
                    orig_p = cand[0].replace("/", "\\")
                    for part in orig_p.split("\\"):
                        if part.lower() in ["marathi", "hindi", "english", "sanskrit", "pravachan", "ringtones"]:
                            l = part.capitalize()
                            if l == "Ringtones":
                                l = "Ringtones & Alerts"
                            matched_langs.append((l, cand))
                            break

                # If all candidate languages conflict with target_lang
                if matched_langs and all(l != target_lang for l, cand in matched_langs):
                    # Deliberate transfers: e.g. Sanskrit chants originating in Morning folder
                    # But Marathi in English or Hindi in English or Marathi in Hindi are real bugs!
                    top_orig_lang = matched_langs[0][0]
                    orig_sample = matched_langs[0][1]
                    all_mismatches.append({
                        "organized_path": rel_target,
                        "orig_path": orig_sample[0],
                        "orig_filename": orig_sample[2],
                        "orig_title": orig_sample[3],
                        "orig_lang": top_orig_lang,
                        "target_lang": target_lang,
                        "size": sz
                    })

    print(f"\nAudited {total_audited} organized tracks.")
    print(f"Found {len(all_mismatches)} total cross-language misplacements:\n")
    
    with open("misplacements_audit.json", "w", encoding="utf-8") as fp:
        json.dump(all_mismatches, fp, indent=2)
    print("Saved all misplacements to misplacements_audit.json")
    for m in all_mismatches:
        print(f"  [{m['orig_lang']} -> {m['target_lang']}] {m['organized_path']}")
        print(f"    Orig: {m['orig_path']} (Filename: {m['orig_filename']}, Title: {m['orig_title']})\n")

if __name__ == "__main__":
    comprehensive_audit()
