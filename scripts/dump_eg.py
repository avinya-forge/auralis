import json
import re

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen: {len(eg)}")
# Write all 1091 filenames to a text file for complete inspection
with open('scripts/all_eg_filenames.txt', 'w', encoding='utf-8') as f:
    for t in eg:
        f.write(f"{t['filename']} || {t['tag_title']} || {t['tag_artist']} || {t['tag_album']}\n")

print("Saved all 1091 tracks to scripts/all_eg_filenames.txt")
