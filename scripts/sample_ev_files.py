import json
import sqlite3
import re

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path NOT LIKE '%d:\\songs\\organized%'")
catalog_rows = c.fetchall()

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = [t for t in data['tracks'] if not t.get('is_duplicate')]
ev = [t for t in tracks if t.get('language') == 'Hindi' and t.get('category') == 'Evergreen Classics']

print(f"Total Evergreen: {len(ev)}")
print(f"Catalog rows: {len(catalog_rows)}")

# Print 30 random sample filenames from Evergreen
for t in ev[50:80]:
    print("EV File:", t['filename'], "| source:", t['source_path'])
