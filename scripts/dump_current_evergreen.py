import json
import os

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])
evergreen = [t for t in tracks if 'Evergreen Classics' in t.get('suggested_path', '') and not t.get('is_duplicate', False)]
print('Current count of non-duplicate evergreen:', len(evergreen))

with open('scripts/current_194_evergreen.txt', 'w', encoding='utf-8') as out:
    for i, item in enumerate(evergreen, 1):
        out.write(f"{i}. FN: {os.path.basename(item.get('source_path', ''))} || Title: {item.get('title', '')} || Artist: {item.get('artist', '')} || Dest: {item.get('suggested_path', '')}\n")

print('Wrote scripts/current_194_evergreen.txt')
