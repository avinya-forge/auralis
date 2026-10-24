import json
from collections import defaultdict

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])

prav_tracks = [t for t in tracks if t.get('language') == 'Pravachan' or 'pravachan' in t.get('source_path', '').lower() or 'katha' in t.get('source_path', '').lower() or 'abhyankar' in t.get('source_path', '').lower() or 'kavishwar' in t.get('source_path', '').lower() or 'ghaisasi' in t.get('source_path', '').lower()]

print(f"Total pravachan files in cache: {len(prav_tracks)}")

# Check stream hashes to see unique audio vs duplicate copies
hash_map = defaultdict(list)
for t in prav_tracks:
    h = t.get('audio_hash', '')
    hash_map[h].append(t)

print(f"Unique audio streams: {len(hash_map)}")
print(f"Redundant copies: {len(prav_tracks) - len(hash_map)}")

# List the unique streams per group
series_streams = defaultdict(set)
for h, file_list in hash_map.items():
    t = file_list[0]
    p_low = f"{t.get('source_path', '')} {t.get('filename', '')}".lower()
    if "kavish" in p_low:
        s = "Kavishwar Maharaj - Bhagwat Katha"
    elif "ghaisasi" in p_low or "song " in p_low:
        s = "Ghaisasi Guruji - Bhagwat Katha"
    elif "aparna" in p_low:
        s = "Aparna Abhyankar - Gita Pathan"
    elif "yog" in p_low or "abhyankar" in p_low or "ramdas" in p_low or "gita" in p_low:
        s = "Shankar Abhyankar - Bhagavad Gita Nirupan"
    else:
        s = "Other"
    series_streams[s].add(h)

for s, h_set in sorted(series_streams.items()):
    print(f"\nSeries: {s} -> {len(h_set)} UNIQUE audio lectures")
