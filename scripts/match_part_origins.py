import os
import sqlite3
import mutagen
from mutagen.mp3 import MP3

conn = sqlite3.connect("auralis_inventory.db")
c = conn.cursor()

parts = [
    r"English\Indian Rock Bands\Demonic Resurrection\Part 2.mp3",
    r"English\Indian Rock Bands\Zero\Part 2.mp3",
    r"English\U2\Part 2.mp3",
    r"English\U2\Part 3.mp3",
    r"English\Westlife\Part 2.mp3",
    r"Hindi\Albums\Atif Aslam - Doorie\Part 2.mp3",
    r"Hindi\Artists\Lata Mangeshkar\Part 2.mp3",
    r"Hindi\Soundtracks\Bodyguard\Part 2.mp3",
    r"Hindi\Soundtracks\Jodhaa Akbar\Part 2.mp3",
    r"Hindi\Soundtracks\Lakshya\Part 2.mp3",
    r"Hindi\Soundtracks\Love Story\Part.mp3",
    r"Hindi\Soundtracks\Oye Lucky Lucky Oye\Part 2.mp3",
    r"Hindi\Soundtracks\Soundtrack Singles\Part 2.mp3"
]

for p in parts:
    fp = os.path.join(r"D:\Songs\organized", p)
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        mp3 = MP3(fp)
        tag_sz = mp3.tags.size if mp3.tags else 0
        payload_sz = sz - tag_sz
        dur = mp3.info.length

        # Query inventory by payload_sz or exact sz or duration match
        c.execute("SELECT file_path, filename, title, artist, album FROM audio_inventory WHERE file_size IN (?, ?) OR (duration BETWEEN ? AND ? AND file_path LIKE ?)",
                  (sz, payload_sz, dur - 1.0, dur + 1.0, f"%{os.path.basename(os.path.dirname(fp))}%"))
        rows = c.fetchall()
        print(f"=== {p} ===")
        print(f"  Matches ({len(rows)}):")
        for r in rows[:5]:
            print(f"    Orig: {r[0]} | Filename: {r[1]} | Title: {r[2]} | Artist: {r[3]}")
        print()

conn.close()
