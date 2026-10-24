import json

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

dutta_in_cache = [t for t in data['tracks'] if 'dutta' in t.get('source_path', '').lower() or 'dutta' in t.get('filename', '').lower() or 'kadkade' in t.get('source_path', '').lower() or 'kadkade' in t.get('artist', '').lower()]

print(f"Total dutta/kadkade tracks in cache: {len(dutta_in_cache)}")
for t in dutta_in_cache:
    print(f"SRC: {t.get('source_path')} | CAT: {t.get('category')} | PROP: {t.get('proposed_path')}")
