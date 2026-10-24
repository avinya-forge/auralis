import json

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = [t for t in data['tracks'] if not t.get('is_duplicate')]
ev = [t for t in tracks if t.get('language') == 'Hindi' and t.get('category') == 'Evergreen Classics']
print('Total Evergreen Classics tracks:', len(ev))
for t in ev[:35]:
    print("FILE:", t['filename'])
    print("  Title :", t.get('title'))
    print("  Artist:", t.get('artist'))
    print("  Album :", t.get('album'))
    print("  Source:", t.get('source_path'))
    print("  RawTagAlbum:", t.get('tag_album'))
    print("  RawTagArtist:", t.get('tag_artist'))
    print("  RawTagTitle:", t.get('tag_title'))
    print("-" * 50)
