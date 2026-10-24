import os

with open('scripts/current_194_evergreen.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

non_inh_non_eng = []
inh_tracks = []
eng_tracks = []

eng_kws = ['wham', 'war', 'waiting vain', 'sexy eyes', 'ghost busters', 'dangerous', 'bloom', 'all one', 'ambush the night', 'left right left', 'nothing gonna change', 'nothings gonna change']

for line in lines:
    low = line.lower()
    if 'inh10' in low or 'inh9' in low:
        inh_tracks.append(line)
    elif any(k in low for k in eng_kws):
        eng_tracks.append(line)
    else:
        non_inh_non_eng.append(line)

print(f"Total: {len(lines)}")
print(f"INH: {len(inh_tracks)}")
print(f"English: {len(eng_tracks)}")
print(f"Remaining: {len(non_inh_non_eng)}")

with open('scripts/remaining_144.txt', 'w', encoding='utf-8') as out:
    for i, l in enumerate(non_inh_non_eng, 1):
        out.write(f"{i}. {l}\n")
