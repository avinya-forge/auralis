import sqlite3
import json
import re
from collections import Counter

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename, file_size FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
fj_rows = c.fetchall()

by_size = {}
for fp, fn, sz in fj_rows:
    by_size[sz] = fp

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen: {len(eg)}")
origins = Counter()
for t in eg:
    sz = t.get('size_bytes', 0)
    fp = by_size.get(sz)
    if fp:
        parts = fp.split('\\')
        top = '\\'.join(parts[1:3]) if len(parts) > 3 else parts[1]
        origins[top] += 1
    else:
        origins["NO SIZE MATCH"] += 1

print("\nOrigins of 1091 Evergreen tracks:")
for k, v in origins.most_common(30):
    print(f"  {k}: {v}")

conn.close()
