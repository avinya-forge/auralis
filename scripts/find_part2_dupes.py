import os
import re
from collections import defaultdict
import mutagen

pairs = []
for root, _, files in os.walk(r"D:\Songs\organized"):
    rel = os.path.relpath(root, r"D:\Songs\organized")
    # Skip Pravachan and Samhita where Part 1 / Part 2 are genuine sequential discourses
    if any(k in rel.lower() for k in ["pravachan", "samhita", "p. l. deshpande", "deshpande"]):
        continue

    f_map = {}
    for f in files:
        if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac')):
            continue
        fp = os.path.join(root, f)
        try:
            mf = mutagen.File(fp)
            dur = round(getattr(mf.info, "length", 0)) if mf else 0
        except Exception:
            dur = 0
        f_map[f] = (dur, os.path.getsize(fp), fp)

    for f, (dur, sz, fp) in f_map.items():
        if " - part " in f.lower():
            base = re.sub(r"\s*-\s*part\s*\d+", "", f, flags=re.I)
            if base in f_map:
                base_dur, base_sz, base_fp = f_map[base]
                if abs(dur - base_dur) <= 12:
                    pairs.append((rel, f, base, dur, base_dur, sz, base_sz, fp, base_fp))

print(f"Total Part 2 duplicate pairs within 12s duration: {len(pairs)}")
for rel, f, base, d1, d2, s1, s2, _, _ in pairs[:20]:
    print(f"  [{rel}] {f} ({d1}s, {s1}b) <==> {base} ({d2}s, {s2}b)")
