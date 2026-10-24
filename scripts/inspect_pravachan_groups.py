import json
import os

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])

keywords = ["kavish", "ghaisasi", "abhyankar", "bhagwat", "katha", "pravachan", "dutta", "gita", "geeta", "ramdas", "day", "yog"]

prav_tracks = []
for t in tracks:
    src = t.get('source_path', '')
    fn = t.get('filename', '')
    prop = t.get('proposed_path', '')
    combined = f"{src} {fn} {prop} {t.get('artist', '')} {t.get('album', '')} {t.get('category', '')}".lower()
    if any(k in combined for k in ["kavish", "ghaisasi", "abhyankar", "bhagwat", "katha", "gita pravachan", "shankar abhyankar", "aparna abhyankar", "bhagavad-gita", "ramdas swami"]):
        prav_tracks.append(t)

print(f"Total pravachan tracks in cache: {len(prav_tracks)}")

# Categorize them
groups = {}
for t in prav_tracks:
    # Determine speaker / series
    combined = f"{t.get('source_path', '')} {t.get('filename', '')} {t.get('proposed_path', '')}".lower()
    if "kavish" in combined:
        grp = "Kavishwar Maharaj - Bhagwat Katha"
    elif "ghaisasi" in combined:
        grp = "Ghaisasi Guruji - Bhagwat Katha"
    elif "aparna" in combined:
        grp = "Aparna Abhyankar - Gita Pathan"
    elif "shankar" in combined or "abhyankar" in combined or "yog" in combined:
        grp = "Shankar Abhyankar - Bhagavad Gita Nirupan"
    else:
        grp = "Other Pravachan / Discourses"
    
    if grp not in groups:
        groups[grp] = []
    groups[grp].append(t)

for grp, tr_list in sorted(groups.items()):
    active = [t for t in tr_list if not t.get('is_duplicate', False)]
    dups = [t for t in tr_list if t.get('is_duplicate', False)]
    print(f"\n=== {grp} ===")
    print(f"Total: {len(tr_list)} | Active: {len(active)} | Duplicates: {len(dups)}")
    for t in active[:10]:
        print(f"   [ACTIVE] {t.get('filename')} -> {t.get('proposed_path')}")
    for t in dups[:5]:
        print(f"   [DUP]    {t.get('filename')} -> {t.get('proposed_path')}")
