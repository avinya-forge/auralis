import json
import re

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = data['tracks']
ev_tracks = [t for t in tracks if not t.get('is_duplicate') and t.get('category') == 'Evergreen Classics']

print(f"Remaining {len(ev_tracks)} Evergreen Classics:")
for t in ev_tracks[:40]:
    fn = t['filename']
    title = t.get('title')
    album = t.get('album')
    art = t.get('artist')
    print(f"  {fn} | Album: {album} | Artist: {art}")
