import json
from collections import Counter

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen: {len(eg)}")
# Print first 60 filenames
for i in range(0, min(len(eg), 100), 5):
    print(" | ".join([t['filename'] for t in eg[i:i+5]]))
