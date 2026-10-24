import json

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])
evergreen = [t for t in tracks if t.get('category') == 'Evergreen Classics' and not t.get('is_duplicate', False)]
print('Total tracks with category == Evergreen Classics:', len(evergreen))

with open('scripts/current_194_evergreen.txt', 'w', encoding='utf-8') as out:
    for i, t in enumerate(evergreen, 1):
        out.write(f"{i}. FN: {t.get('source_path', '')} || Cat: {t.get('category')} || Dest: {t.get('proposed_path', '')}\n")

# Show sample of first 10 destinations
for t in evergreen[:10]:
    print(t.get('proposed_path'))
