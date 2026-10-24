import sqlite3

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("""
    SELECT DISTINCT file_path 
    FROM master_audio_catalog 
    WHERE file_path LIKE '%pravachan%' 
       OR file_path LIKE '%katha%' 
       OR file_path LIKE '%kavish%' 
       OR file_path LIKE '%ghaisasi%' 
       OR file_path LIKE '%dutta%' 
       OR file_path LIKE '%abhyankar%'
""")
rows = c.fetchall()
dirs = set()
for r in rows:
    dirs.add(r[0].rsplit('\\', 1)[0])

print(f"Total directories found: {len(dirs)}")
for d in sorted(dirs):
    print("DIR:", d)
