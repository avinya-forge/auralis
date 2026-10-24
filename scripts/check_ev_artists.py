import json
import re

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))
tracks = [t for t in data['tracks'] if not t.get('is_duplicate')]
ev = [t for t in tracks if t.get('language') == 'Hindi' and t.get('category') == 'Evergreen Classics']
print('Total Evergreen Classics tracks:', len(ev))

hindi_artists = [
    'lata mangeshkar', 'lata', 'kishore kumar', 'kishore', 'mohammed rafi', 'mohd rafi', 'rafi',
    'mukesh', 'asha bhosle', 'asha', 'pankaj udhas', 'pankaj udas', 'jagjit singh', 'jagjit',
    'manna dey', 'talat mahmood', 'talat', 'hemant kumar', 'hemant', 'geeta dutt', 'yesudas',
    'mahendra kapoor', 'arijit singh', 'arijit', 'shreya ghoshal', 'shreya', 'sonu nigam', 'sonu',
    'shaan', 'kk', 'udit narayan', 'kumar sanu', 'alka yagnik', 'kavita krishnamurthy', 'lucky ali',
    'kailash kher', 'atif aslam', 'atif', 'mohit chauhan', 'sukhwinder singh', 'sukhwinder',
    'mika singh', 'sunidhi chauhan', 'sunidhi', 'neha kakkar', 'himesh reshammiya', 'anuradha paudwal',
    'suresh wadkar', 'bappi lahiri', 'adnan sami', 'rd burman', 'r d burman', 'r.d. burman', 'burman',
    'sd burman', 's d burman', 's.d. burman', 'kalyanji anandji', 'laxmikant pyarelal', 'naushad',
    'madan mohan', 'khayyam', 'salil chowdhury', 'roshan', 'op nayyar', 'o.p. nayyar', 'ravi'
]

with_singer = 0
for t in ev:
    text = f"{t['filename']} {t.get('tag_title', '')} {t.get('tag_artist', '')} {t.get('source_path', '')}".lower()
    for s in hindi_artists:
        if re.search(r'\b' + re.escape(s) + r'\b', text):
            with_singer += 1
            break

print(f"Tracks with identifiable singer/composer in tags/path: {with_singer} ({with_singer/len(ev)*100:.1f}%)")
