import json
from collections import Counter

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']
print(f"Total Evergreen Classics: {len(eg)}")
for t in eg[:40]:
    print(f"FN: {t['filename']} | Title: {t['tag_title']} | Artist: {t['tag_artist']} | Album: {t['tag_album']}")
