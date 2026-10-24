"""
Clean remaining redundant parent prefixes in Marathi folders.
"""
import os, shutil
from mutagen.id3 import ID3, TIT2

ORGANIZED_ROOT = r"D:\Songs\organized\Marathi"

prefixes_to_clean = [
    (r"Geet Ramayan", r"Geet Ramayan - Part 3.mp3", r"Part 03.mp3", "Part 03"),
    (r"Geet Ramayan", r"Geet Ramayan - Part 4.mp3", r"Part 04.mp3", "Part 04"),
    (r"Geet Ramayan", r"Geet Ramayan - Part 5.mp3", r"Part 05.mp3", "Part 05"),
    (r"Natyasangeet\Pushpa Parag", r"Pushpa Parag - Track 2010.mp3", r"Track 2010.mp3", "Track 2010"),
    (r"Natyasangeet\Pushpa Parag", r"Pushpa Parag - Track 2011.mp3", r"Track 2011.mp3", "Track 2011"),
    (r"Natyasangeet\Pushpa Parag", r"Pushpa Parag - Track 2013.mp3", r"Track 2013.mp3", "Track 2013"),
    (r"Natyasangeet\Pushpa Parag", r"Pushpa Parag - Track 2014.mp3", r"Track 2014.mp3", "Track 2014"),
    (r"Natyasangeet\Saath Deti Himshekhari", r"Saath Deti Himshekhari - Track 2695.mp3", r"Track 2695.mp3", "Track 2695"),
    (r"Natyasangeet\Saath Deti Himshekhari", r"Saath Deti Himshekhari - Track 2698.mp3", r"Track 2698.mp3", "Track 2698"),
    (r"Natyasangeet\Saath Deti Himshekhari", r"Saath Deti Himshekhari - Track 2701.mp3", r"Track 2701.mp3", "Track 2701"),
    (r"Natyasangeet\Uttung Natyashilpa", r"Uttung Natyashilpa - Track 2001.mp3", r"Track 2001.mp3", "Track 2001"),
    (r"Natyasangeet\Uttung Natyashilpa", r"Uttung Natyashilpa - Track 2002.mp3", r"Track 2002.mp3", "Track 2002"),
]

for sub, old_fn, new_fn, clean_tit in prefixes_to_clean:
    old_p = os.path.join(ORGANIZED_ROOT, sub, old_fn)
    new_p = os.path.join(ORGANIZED_ROOT, sub, new_fn)
    if os.path.exists(old_p) and not os.path.exists(new_p):
        shutil.move(old_p, new_p)
        try:
            id3 = ID3(new_p)
            id3["TIT2"] = TIT2(encoding=3, text=clean_tit)
            id3.save(new_p)
        except Exception:
            pass
        print(f"Renamed: {old_fn} -> {new_fn}")

print("Done cleaning remaining parent prefixes!")
