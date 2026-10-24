import os
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

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
        id3 = ID3(fp)
        m = MP3(fp)
        sz = os.path.getsize(fp)
        tit = str(id3.get("TIT2", ""))
        art = str(id3.get("TPE1", ""))
        alb = str(id3.get("TALB", ""))
        print(f"=== {p} ===")
        print(f"  Size: {sz} | Dur: {round(m.info.length, 1)}s | Bitrate: {m.info.bitrate//1000}kbps")
        print(f"  TIT2: {tit} | TPE1: {art} | TALB: {alb}\n")
