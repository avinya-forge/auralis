import os
import sys
import re
from collections import defaultdict
import mutagen

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.test_doors_nlp_dupes import canonical_nlp_title

pf = r"D:\Songs\organized\English\Pink Floyd"
files = os.listdir(pf)
groups = defaultdict(list)
for f in files:
    fp = os.path.join(pf, f)
    mf = mutagen.File(fp)
    dur = round(getattr(mf.info, "length", 0)) if mf else 0
    # Strip artist prefixes from Pink Floyd
    f_clean = re.sub(r"^(artist\s*-\s*pink\s*floyd\s*-\s*|pink\s*floyd\s*-\s*|greatest\s*guitar\s*solos\s*-\s*pink\s*floyd\s*-\s*|pink\s*floyd-)", "", f, flags=re.I)
    canon = canonical_nlp_title(f_clean)
    key = (canon, round(dur / 4) * 4)
    groups[key].append((f, dur, os.path.getsize(fp)))

print("=== Pink Floyd NLP + Duration Duplicate Groups ===")
dup_count = 0
for (canon, dur_bucket), members in sorted(groups.items()):
    if len(members) > 1:
        dup_count += (len(members) - 1)
        print(f"GROUP: \"{canon}\" (~{dur_bucket}s):")
        for m in members:
            print(f"   {m[0]} (dur: {m[1]}s, size: {m[2]} bytes)")
print(f"Total redundant duplicates in Pink Floyd: {dup_count}")
