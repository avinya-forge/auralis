import json

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total remaining in Evergreen Classics: {len(eg)}")
with open('scripts/all_359_evergreen.txt', 'w', encoding='utf-8') as f:
    for i, t in enumerate(eg):
        f.write(f"{i+1}. FN: {t['filename']} || Title: {t['tag_title']} || Artist: {t['tag_artist']} || Album: {t['tag_album']}\n")

print("Saved all 359 to scripts/all_359_evergreen.txt")
