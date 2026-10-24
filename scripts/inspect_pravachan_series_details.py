import json
from collections import defaultdict

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])

hash_map = defaultdict(list)
for t in tracks:
    h = t.get('audio_hash', '')
    hash_map[h].append(t)

def inspect_series(keyword, name):
    print(f"\n==================== {name} ====================")
    unique_items = []
    for h, file_list in hash_map.items():
        # Check if matches keyword
        if any(keyword in f"{t.get('source_path', '')} {t.get('filename', '')}".lower() for t in file_list):
            # Sort by bitrate/size descending to pick best copy
            sorted_files = sorted(file_list, key=lambda x: (x.get('bitrate', 0), x.get('size_bytes', 0)), reverse=True)
            unique_items.append((sorted_files[0], sorted_files[1:]))

    print(f"Total Unique: {len(unique_items)}")
    for best, dups in sorted(unique_items, key=lambda x: x[0].get('filename', ''))[:20]:
        print(f"  BEST: {best.get('filename')} (Size: {best.get('size_bytes')}) [Dups: {len(dups)}]")
        print(f"        Src: {best.get('source_path')}")

inspect_series("kavish", "Kavishwar Maharaj - Bhagwat Katha")
inspect_series("ghaisasi", "Ghaisasi Guruji - Bhagwat Katha")
inspect_series("aparna", "Aparna Abhyankar - Gita Pathan")
inspect_series("abhyankar", "Shankar Abhyankar")
