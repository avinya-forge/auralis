import sqlite3
import json

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
print(f"Total tracks in cache: {len(data)}")

# Check how many tracks have audio_hash matching master_audio_catalog
# Note: master_audio_catalog has file_size, filename. Does it have audio_hash?
print([d[1] for d in c.execute("PRAGMA table_info(master_audio_catalog)").fetchall()])

# Let's see if file_size and filename match
size_match = 0
for t in data[:100]:
    fn = t['filename']
    sz = t.get('size_bytes', 0)
    c.execute("SELECT file_path FROM master_audio_catalog WHERE file_size = ? AND drive_letter IN ('F', 'J') LIMIT 1", (sz,))
    r = c.fetchone()
    if r:
        size_match += 1

print(f"Exact size match on F/J for first 100 tracks: {size_match}/100")
conn.close()
