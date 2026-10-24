import os
import re

d_songs = r"D:\Songs"
pravachan_matches = []

keywords = ["kavish", "ghaisasi", "abhyankar", "bhagwat", "katha", "pravachan", "dutta", "gita", "geeta", "ramdas"]

for root, dirs, files in os.walk(d_songs):
    for f in files:
        if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.ogg', '.flac')):
            continue
        p = os.path.join(root, f)
        p_low = p.lower()
        if any(k in p_low for k in keywords):
            pravachan_matches.append(p)

print(f"Total pravachan/katha matches found in D:\\Songs: {len(pravachan_matches)}")
folder_counts = {}
for p in pravachan_matches:
    d = os.path.dirname(p)
    folder_counts[d] = folder_counts.get(d, 0) + 1

for d, c in sorted(folder_counts.items()):
    print(f"{c:3d} files | {d}")
