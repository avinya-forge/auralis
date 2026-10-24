import sqlite3

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, file_size FROM master_audio_catalog WHERE file_size IN (3984091, 5428297, 3723337, 4970789, 4387840, 4850469, 5499611, 3952274) AND file_path LIKE 'D:%'")
rows = c.fetchall()
print(f"Matches on D by exact byte size: {len(rows)}")
for r in rows:
    print("  ", r)
