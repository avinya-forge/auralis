import sqlite3
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.catalog_resolver import normalize_title, lookup_catalog_track

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path NOT LIKE '%d:\\songs\\organized%'")
rows = c.fetchall()

test_titles = [
    'Aakashi Zep Ghe Re Pakhara.mp3',
    'Aala Aala Vara.mp3',
    'Aaji Soniyacha Dinu.mp3',
    'Aali Thumkat Naar Lachkat.mp3',
    'Aaj Purani Rahon Se.mp3',
    'Aane Wala Pal11!S.mp3',
    'Aaj Radhika Bano.mp3',
    'Aankhon Ki Masti.mp3'
]

for tt in test_titles:
    norm = normalize_title(tt)
    matches = [r[0] for r in rows if normalize_title(r[1]) == norm]
    lookup = lookup_catalog_track(tt)
    print(f"{tt} -> {len(matches)} matches | lookup: {lookup}")
    if matches:
        print("   Sample match path:", matches[0])
