import json

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])

prav_tracks = [t for t in tracks if t.get('language') == 'Pravachan' or 'pravachan' in t.get('source_path', '').lower() or 'katha' in t.get('source_path', '').lower() or 'abhyankar' in t.get('source_path', '').lower() or 'kavishwar' in t.get('source_path', '').lower() or 'ghaisasi' in t.get('source_path', '').lower() or 'dutta' in t.get('source_path', '').lower()]

print(f"Total matching tracks in current cache: {len(prav_tracks)}")

for t in prav_tracks[:30]:
    print(f"SRC: {t.get('source_path')} | CAT: {t.get('category')} | PROP: {t.get('proposed_path')}")
