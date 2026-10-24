import re

with open('scripts/current_194_evergreen.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Let's inspect tracks that have Inh
inh_tracks = [l.strip() for l in lines if 'inh10' in l.lower()]
print(f"Tracks with INH: {len(inh_tracks)}")
for t in inh_tracks[:10]:
    print("  ", t)

# Let's inspect tracks with English titles
eng_keywords = ['wham', 'war', 'waiting vain', 'sexy eyes', 'ghost busters', 'dangerous', 'bloom', 'all one', 'ambush the night', 'left right left', 'nothings gonna change', 'nothing gonna change']
eng_tracks = [l.strip() for l in lines if any(k in l.lower() for k in eng_keywords)]
print(f"Tracks with English keywords: {len(eng_tracks)}")
for t in eng_tracks:
    print("  ", t)
