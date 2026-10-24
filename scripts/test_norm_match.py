import sqlite3
import re
import json
import os

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute('SELECT file_path, filename FROM master_audio_catalog')
all_rows = c.fetchall()

def normalize_title(name):
    s = re.sub(r'\.[a-zA-Z0-9]+$', '', name)
    s = re.sub(r'^\s*\d+[\s\.\-_]*', '', s)
    s = re.sub(r'\[.*?\]|\(.*?\)', '', s)
    s = re.sub(r'(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

title_to_original_paths = {}
for path, fn in all_rows:
    p_lower = path.lower()
    if 'd:\\songs\\organized' not in p_lower:
        norm = normalize_title(fn)
        if len(norm) > 3:
            if norm not in title_to_original_paths:
                title_to_original_paths[norm] = []
            title_to_original_paths[norm].append(path)

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = data['tracks']
ev_tracks = [t for t in tracks if t['category'] == 'Evergreen Classics']

matched = 0
found_parent_dirs = []
for t in ev_tracks:
    norm = normalize_title(t['filename'])
    matches = title_to_original_paths.get(norm, [])
    if matches:
        matched += 1
        # Pick best match (prefer the path that has the deepest informative directory)
        found_parent_dirs.append(matches[0])

print(f'Total Evergreen Classics: {len(ev_tracks)}')
print(f'Directly matched to original catalog paths: {matched} ({matched/len(ev_tracks)*100:.1f}%)')
print('Sample 20 resolved original paths for Evergreen tracks:')
for p in found_parent_dirs[:20]:
    print('  ', p)
