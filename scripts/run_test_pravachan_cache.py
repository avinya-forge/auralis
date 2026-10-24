import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engine.pravachan_resolver import resolve_pravachan_track

with open('cached_dry_run_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tracks = data.get('tracks', [])

test_tracks = [
    t for t in tracks 
    if t.get('language') == 'Pravachan' 
       or 'pravachan' in t.get('source_path', '').lower() 
       or 'katha' in t.get('source_path', '').lower() 
       or 'abhyankar' in t.get('source_path', '').lower() 
       or 'kavishwar' in t.get('source_path', '').lower() 
       or 'ghaisasi' in t.get('source_path', '').lower()
       or 'day' in t.get('filename', '').lower()
       or 'yog' in t.get('filename', '').lower()
]

print(f"Testing on {len(test_tracks)} candidate tracks...")

by_cat = {}
none_count = 0
for t in test_tracks:
    res = resolve_pravachan_track(
        t.get('filename', ''), 
        t.get('source_path', ''), 
        t.get('tag_title', ''), 
        t.get('tag_artist', ''),
        t.get('tag_album', '')
    )
    if res is None:
        none_count += 1
        continue
    cat = f"{res['language']} / {res['category']}"
    if cat not in by_cat:
        by_cat[cat] = []
    by_cat[cat].append((t.get('filename'), res['artist'], res['album'], res['title'], t.get('is_duplicate', False)))

print(f"Matched {len(test_tracks) - none_count} tracks. Non-matching: {none_count}")

for cat, items in sorted(by_cat.items()):
    active_items = [it for it in items if not it[4]]
    dup_items = [it for it in items if it[4]]
    print(f"\n=== {cat} (Total: {len(items)}, Active: {len(active_items)}, Duplicates: {len(dup_items)}) ===")
    print(f"    Album: {items[0][2]} | Artist: {items[0][1]}")
    for fn, art, alb, tit, is_dup in active_items[:6]:
        dup_str = " [DUP]" if is_dup else ""
        print(f"      File: {fn[:45]:45s} -> Title: {tit}{dup_str}")
    if len(active_items) > 6:
        print(f"      ... and {len(active_items)-6} more active tracks")
