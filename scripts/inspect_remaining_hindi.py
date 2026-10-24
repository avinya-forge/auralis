import sqlite3
import json
import re
from collections import Counter

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename, file_size FROM master_audio_catalog WHERE drive_letter IN ('F', 'J') AND file_path NOT LIKE '%organized%'")
fj_rows = c.fetchall()

def norm(s):
    if not s:
        return ""
    s = re.sub(r"\.[a-zA-Z0-9]+$", "", s)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps|ringtone|webrip)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return s

by_size = {}
by_norm = {}
for fp, fn, sz in fj_rows:
    by_size[sz] = fp
    n = norm(fn)
    if n and len(n) > 3:
        by_norm[n] = fp

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

unresolved = []
for t in eg:
    sz = t.get('size_bytes', 0)
    fn = t['filename']
    n = norm(fn)
    fp = by_size.get(sz) or by_norm.get(n)
    if not fp or not any(k in fp.lower() for k in ["ringtone", "marathi", "vidik", "sanskrit", "pravachan", "english", "old movies", "albums"]):
        unresolved.append(t)

print(f"Total remaining Hindi tracks: {len(unresolved)}")
print("\nSample 40 remaining Hindi tracks:")
for t in unresolved[:40]:
    print(f"FN: {t['filename']} | Title: {t['tag_title']} | Artist: {t['tag_artist']} | Album: {t['tag_album']}")
