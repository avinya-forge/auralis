import sqlite3

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path LIKE '%dutta%' OR filename LIKE '%dutta%'")
rows = c.fetchall()

print(f"Total rows for dutta: {len(rows)}")
for p, fn in rows:
    print(f"{p}")
