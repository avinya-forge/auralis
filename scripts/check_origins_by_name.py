import sqlite3
import json
import re
from collections import Counter

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
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

by_norm = {}
for fp, fn in fj_rows:
    n = norm(fn)
    if n and len(n) > 3:
        by_norm[n] = fp

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen: {len(eg)}")
origins = Counter()
for t in eg:
    fn = t['filename']
    n = norm(fn)
    fp = by_norm.get(n)
    if fp:
        parts = fp.split('\\')
        top = '\\'.join(parts[1:3]) if len(parts) > 3 else parts[1]
        origins[top] += 1
    else:
        origins["NO NAME MATCH"] += 1

print("\nOrigins by normalized name of 1091 Evergreen tracks:")
for k, v in origins.most_common(30):
    print(f"  {k}: {v}")

conn.close()
