import sys
sys.path.insert(0, '.')
import json
from src.engine.catalog_resolver import lookup_catalog_track, normalize_title
from src.engine.pattern_classifier import extract_bollywood_movie_and_song, is_valid_album

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen Classics: {len(eg)}")
catalog_hits = 0
extract_hits = 0
unresolved = []

for t in eg:
    fn = t['filename']
    cat_res = lookup_catalog_track(fn)
    if cat_res and cat_res[1] != 'Evergreen Classics':
        catalog_hits += 1
    else:
        # test extract_bollywood_movie_and_song
        import os
        stem = os.path.splitext(fn)[0]
        from src.engine.pattern_classifier import clean_watermarks
        c_stem = clean_watermarks(stem)
        mov, sng = extract_bollywood_movie_and_song(c_stem, stem, t.get('source_path', ''), t.get('tag_album', ''), t.get('tag_artist', ''), t.get('tag_title', ''))
        if mov:
            extract_hits += 1
        else:
            unresolved.append(t)

print(f"Catalog Hits (missed or ignored): {catalog_hits}")
print(f"Bollywood Pattern Hits: {extract_hits}")
print(f"Still unresolved: {len(unresolved)}")

print("\nSample 25 unresolved tracks:")
for t in unresolved[:25]:
    print(f"FN: {t['filename']} | Title: {t['tag_title']} | Artist: {t['tag_artist']} | Album: {t['tag_album']}")
