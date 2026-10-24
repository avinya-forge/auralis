import json
from collections import Counter

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = [t for t in data['tracks'] if not t.get('is_duplicate')]

generic_cats = [
    ('Hindi', 'Evergreen Classics'),
    ('Marathi', 'Bhavgeet & Classics'),
    ('English', 'Rock & Pop'),
    ('Hindi', 'General'),
    ('English', 'General')
]

for lang, cat in generic_cats:
    matched = [t for t in tracks if t.get('language') == lang and t.get('category') == cat]
    print(f"\n==========================================")
    print(f"Generic Category: {lang} -> {cat} ({len(matched)} tracks)")
    print(f"==========================================")
    for t in matched[:15]:
        print(f"  File: {t['filename']} | Title: {t.get('title')} | Album: {t.get('album')} | Artist: {t.get('artist')}")
