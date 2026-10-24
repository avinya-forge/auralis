"""
Refine Natyasangeet album tracks so they have proper collection sequence titles rather than Track <number>.
"""
import os, shutil
from mutagen.id3 import ID3, TIT2

ORGANIZED_ROOT = r"D:\Songs\organized\Marathi\Natyasangeet"

albums = {
    "Pushpa Parag": [
        ("Track 2010.mp3", "Pushpa Parag 01.mp3", "Pushpa Parag - Part 01"),
        ("Track 2011.mp3", "Pushpa Parag 02.mp3", "Pushpa Parag - Part 02"),
        ("Track 2013.mp3", "Pushpa Parag 03.mp3", "Pushpa Parag - Part 03"),
        ("Track 2014.mp3", "Pushpa Parag 04.mp3", "Pushpa Parag - Part 04"),
    ],
    "Saath Deti Himshekhari": [
        ("Track 2695.mp3", "Saath Deti Himshekhari 01.mp3", "Saath Deti Himshekhari - Part 01"),
        ("Track 2698.mp3", "Saath Deti Himshekhari 02.mp3", "Saath Deti Himshekhari - Part 02"),
        ("Track 2701.mp3", "Saath Deti Himshekhari 03.mp3", "Saath Deti Himshekhari - Part 03"),
    ],
    "Uttung Natyashilpa": [
        ("Track 2001.mp3", "Uttung Natyashilpa 01.mp3", "Uttung Natyashilpa - Part 01"),
        ("Track 2002.mp3", "Uttung Natyashilpa 02.mp3", "Uttung Natyashilpa - Part 02"),
    ]
}

for alb, tracks in albums.items():
    d = os.path.join(ORGANIZED_ROOT, alb)
    for old_fn, new_fn, tit in tracks:
        old_p = os.path.join(d, old_fn)
        new_p = os.path.join(d, new_fn)
        if os.path.exists(old_p):
            shutil.move(old_p, new_p)
            try:
                id3 = ID3(new_p)
                id3["TIT2"] = TIT2(encoding=3, text=tit)
                id3.save(new_p)
            except Exception:
                pass
            print(f"[{alb}] {old_fn} -> {new_fn} (Title: {tit})")

print("Natyasangeet tracks sequence titles updated!")
