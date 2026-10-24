import sqlite3

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_size, tier0_group_id, file_path FROM master_audio_catalog WHERE file_path LIKE '%10 DUTTA DIGAMBAR GURU%'")
rows = c.fetchall()

print(f"Dutta files in catalog: {len(rows)}")
for sz, grp, fp in rows[:8]:
    print(f"Size: {sz} | Group: {grp} | Path: {fp}")
    if grp:
        c.execute("SELECT file_path FROM master_audio_catalog WHERE tier0_group_id = ? AND file_path LIKE 'D:%'", (grp,))
        d_matches = c.fetchall()
        for dm in d_matches:
            print(f"   -> Found on D: {dm[0]}")
