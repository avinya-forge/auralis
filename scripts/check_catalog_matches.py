import sqlite3
import json

conn = sqlite3.connect('master_cross_drive_catalog.db')
cursor = conn.cursor()

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Checking catalog matches for first 20 Evergreen tracks:")
for t in eg[:20]:
    fn = t['filename']
    ah = t.get('audio_hash')
    # search by filename
    cursor.execute("SELECT drive, original_relative_path, category, artist, album, title FROM catalog WHERE filename = ? LIMIT 3", (fn,))
    rows = cursor.fetchall()
    if rows:
        print(f"MATCH for {fn}:")
        for r in rows:
            print(f"  Drive {r[0]}: {r[1]} -> Cat: {r[2]}, Art: {r[3]}, Alb: {r[4]}")
    else:
        # try hash if available
        if ah:
            cursor.execute("SELECT drive, original_relative_path, category, artist, album, title FROM catalog WHERE audio_hash = ? LIMIT 3", (ah,))
            h_rows = cursor.fetchall()
            if h_rows:
                print(f"HASH MATCH for {fn}:")
                for r in h_rows:
                    print(f"  Drive {r[0]}: {r[1]} -> Cat: {r[2]}, Art: {r[3]}, Alb: {r[4]}")
            else:
                print(f"NO MATCH for {fn}")
        else:
            print(f"NO MATCH for {fn}")

conn.close()
