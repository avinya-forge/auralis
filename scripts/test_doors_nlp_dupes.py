import os
import re
from collections import defaultdict
import mutagen

doors = r"D:\Songs\organized\English\The Doors"
files = os.listdir(doors)

def canonical_nlp_title(name):
    s = os.path.splitext(name)[0].lower()
    # Normalize spelling
    s = s.replace("whisky", "whiskey")
    # Strip prefixes
    s = re.sub(r"^(the doors\s*-\s*|ra\.one\s*-\s*-\s*)", "", s)
    # Strip part / no suffixes
    s = re.sub(r"\s*-\s*part\s*\d+", "", s)
    s = re.sub(r"\s+no\.?\s*\d*", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

groups = defaultdict(list)
for f in files:
    fp = os.path.join(doors, f)
    mf = mutagen.File(fp)
    dur = round(getattr(mf.info, "length", 0)) if mf else 0
    canon = canonical_nlp_title(f)
    # Group by canonical title and duration rounded to 4 seconds
    key = (canon, round(dur / 4) * 4)
    groups[key].append((f, dur, os.path.getsize(fp)))

print("=== The Doors NLP + Duration Duplicate Groups ===")
dup_count = 0
for (canon, dur_bucket), members in sorted(groups.items()):
    if len(members) > 1:
        dup_count += (len(members) - 1)
        print(f"GROUP: \"{canon}\" (~{dur_bucket}s):")
        for m in members:
            print(f"   {m[0]} (dur: {m[1]}s, size: {m[2]} bytes)")

print(f"Total redundant duplicates in The Doors: {dup_count}")
