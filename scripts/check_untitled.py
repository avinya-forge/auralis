import json

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
un = [t for t in data if 'Untitled (' in t['filename']]
print('Count of Untitled:', len(un))
print('With lyrics:', len([t for t in un if t.get('transcribed_lyrics')]))
for t in un[:15]:
    lyr = t.get('transcribed_lyrics', '')
    print(f"{t['filename']} | Dur: {t.get('duration')} | Lyrics: {lyr[:60]}")
