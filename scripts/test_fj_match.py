import sqlite3
import json
import re

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

def norm(s):
    s = re.sub(r"^\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return s

# Index all F and J entries by size and normalized filename
print("Building F/J catalog in-memory lookup...")
c.execute("SELECT drive_letter, file_path, filename, file_size FROM master_audio_catalog WHERE drive_letter IN ('F', 'J') AND file_path NOT LIKE '%organized%'")
fj_rows = c.fetchall()
print(f"Total F/J rows: {len(fj_rows)}")

by_size = {}
by_name = {}
for dl, fp, fn, sz in fj_rows:
    if sz not in by_size:
        by_size[sz] = []
    by_size[sz].append(fp)
    
    n = norm(fn)
    if n and len(n) > 3:
        if n not in by_name:
            by_name[n] = []
        by_name[n].append(fp)

matched = 0
unmatched = []
for t in eg:
    sz = t.get('size_bytes', 0)
    fn = t['filename']
    n = norm(fn)
    
    hits = by_size.get(sz, []) or by_name.get(n, [])
    if hits:
        matched += 1
    else:
        unmatched.append(t)

print(f"Total Evergreen tested: {len(eg)}")
print(f"Matched to original F/J paths: {matched} ({matched*100.0/len(eg):.1f}%)")
print(f"Unmatched: {len(unmatched)}")

print("\nSample 15 matched paths:")
for t in eg[:25]:
    sz = t.get('size_bytes', 0)
    fn = t['filename']
    n = norm(fn)
    hits = by_size.get(sz, []) or by_name.get(n, [])
    if hits:
        # pick the cleanest hit
        print(f"  Current: {fn} -> Orig: {hits[0]}")
    else:
        print(f"  NO HIT: {fn}")

conn.close()
