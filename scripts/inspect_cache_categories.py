import json
from collections import Counter

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])
print(f'Total tracks in cache: {len(tracks)}')
active = [t for t in tracks if not t.get('is_duplicate', False)]
print(f'Active unique tracks: {len(active)}')
dups = [t for t in tracks if t.get('is_duplicate', False)]
print(f'Duplicate tracks: {len(dups)}')

categories = Counter()
languages = Counter()

for t in active:
    languages[t.get('language', 'Unknown')] += 1
    categories[f"{t.get('language', 'Unknown')} / {t.get('category', 'Unknown')}"] += 1

print('\n--- Language Distribution ---')
for lang, count in languages.most_common():
    print(f"{lang:15s}: {count:5d}")

print('\n--- Top 30 Categories ---')
for cat, count in categories.most_common(30):
    print(f"{cat:40s}: {count:5d}")

print('\n--- Bottom 10 Categories ---')
for cat, count in categories.most_common()[-10:]:
    print(f"{cat:40s}: {count:5d}")
