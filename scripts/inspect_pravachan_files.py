import sqlite3
import os

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("""
    SELECT file_path, filename 
    FROM master_audio_catalog 
    WHERE file_path LIKE '%pravachan%' 
       OR file_path LIKE '%katha%' 
       OR file_path LIKE '%kavish%' 
       OR file_path LIKE '%ghaisasi%' 
       OR file_path LIKE '%abhyankar%'
       OR file_path LIKE '%dutta%'
""")
rows = c.fetchall()

print(f"Total matching master catalog rows: {len(rows)}")

# Group by parent directory
dir_map = {}
for path, fn in rows:
    p_dir = os.path.dirname(path)
    if p_dir not in dir_map:
        dir_map[p_dir] = []
    dir_map[p_dir].append(fn)

for d, fns in sorted(dir_map.items()):
    print(f"\nFOLDER: {d} ({len(fns)} files)")
    for f in fns[:5]:
        print(f"   - {f}")
    if len(fns) > 5:
        print(f"   ... and {len(fns)-5} more")
