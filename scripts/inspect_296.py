import sys
sys.path.insert(0, '.')
import json
from scripts.test_comprehensive_resolver import *

rem = []
for t in eg:
    fn = t['filename']
    n = norm(fn)
    dur = t.get('duration', 0)
    
    if re.search(r"\bcd[12]\s*track\d+\b", n):
        continue
    if any(rt in n for rt in RINGTONE_TRIGGERS) or (dur > 0 and dur < 40 and "mp3" in fn.lower()):
        continue
    if n in MARATHI_TRACKS_MAP:
        continue
    if any(aj in n for aj in ANUP_JALOTA_TRACKS) or "anup jalota" in t.get('tag_artist', '').lower():
        continue
    if n in HINDI_ALBUMS_MAP or n in ENGLISH_TRACKS_MAP or n in BOLLYWOOD_TRACK_MAP:
        continue
    cat_path = by_norm.get(n)
    if cat_path:
        continue
    rem.append(t)

print(f"Total remaining: {len(rem)}")
with open('scripts/remaining_296.txt', 'w', encoding='utf-8') as f:
    for t in rem:
        f.write(f"{t['filename']} || {t['tag_title']} || {t['tag_artist']} || {t['tag_album']}\n")

print("Saved to scripts/remaining_296.txt")
