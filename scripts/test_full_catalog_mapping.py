import sqlite3
import json
import re
import os
from collections import Counter, defaultdict

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()

print("Loading master catalog from F and J drives...")
c.execute("SELECT file_path, filename, file_size FROM master_audio_catalog WHERE drive_letter IN ('F', 'J') AND file_path NOT LIKE '%organized%'")
fj_rows = c.fetchall()
print(f"Loaded {len(fj_rows)} F/J catalog entries.")

def norm(s):
    if not s:
        return ""
    s = re.sub(r"\.[a-zA-Z0-9]+$", "", s)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps|ringtone|webrip)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return s

by_size = defaultdict(list)
by_norm = defaultdict(list)

for fp, fn, sz in fj_rows:
    by_size[sz].append(fp)
    n = norm(fn)
    if n and len(n) > 3:
        by_norm[n].append(fp)

def parse_orig_path(fp):
    p_lower = fp.lower()
    parts = fp.split("\\")
    
    # 1. Ringtones
    if "ringtone" in p_lower:
        return "Ringtones", "Ringtones & Audio Clips", "Ringtones"
        
    # 2. Sanskrit
    if any(k in p_lower for k in ["vidik sukta", "vaidik sukta", "sanskrit"]):
        if "samhita" in p_lower:
            return "Sanskrit", "Vedic Samhita", "Vedic Samhita"
        elif any(st in p_lower for st in ["stotra", "ashtak"]):
            return "Sanskrit", "Stotras & Ashtakams", "Stotras & Ashtakams"
        else:
            return "Sanskrit", "Vedic Suktas", "Vedic Suktas"
            
    # 3. Pravachan
    if "pravachan" in p_lower or "katha" in p_lower:
        if "ghaisasi" in p_lower:
            return "Pravachan", "Bhagwat Katha\\Ghaisasi Guruji", "Bhagwat Katha"
        elif "kavishwar" in p_lower:
            return "Pravachan", "Bhagwat Katha\\Kavishwar Maharaj", "Bhagwat Katha"
        elif "abhyankar" in p_lower or "gita" in p_lower:
            spk = "Aparna Abhyankar" if "aparna" in p_lower else "Shankar Abhyankar"
            return "Pravachan", f"Bhagavad Gita\\{spk}", "Bhagavad Gita"
        else:
            return "Pravachan", "Discourses", "Discourses"
            
    # 4. Marathi
    if "marathi" in p_lower:
        if "ajay" in p_lower and "atul" in p_lower:
            return "Marathi", "Ajay-Atul", "Ajay-Atul Hits"
        elif "geet ramayan" in p_lower or "g d malgulkar" in p_lower:
            return "Marathi", "Geet Ramayan", "Geet Ramayan"
        elif "natya sangeet" in p_lower:
            return "Marathi", "Natyasangeet", "Natyasangeet"
        elif "abhang" in p_lower:
            return "Marathi", "Abhang & Bhakti", "Abhang & Bhakti"
        for i, p in enumerate(parts):
            if p.lower() == "marathi" and i + 1 < len(parts) - 1:
                sub = parts[i+1].strip()
                if sub.lower() not in ["marathi songs", "random", "artist"]:
                    return "Marathi", sub, sub
        return "Marathi", "Bhavgeet & Classics", "Bhavgeet & Classics"

    # 5. English
    if "english" in p_lower:
        for b in ["metallica", "megadeth", "nirvana", "nickelback", "opeth", "coldplay", "iron maiden", "pink floyd", "the beatles", "beatles", "linkin park", "u2", "green day"]:
            if b in p_lower:
                return "English", b.title(), b.title()
        return "English", "Rock & Pop", "Rock & Pop"
        
    # 6. Hindi
    if "old movies" in p_lower:
        for i, p in enumerate(parts):
            if p.lower() == "old movies" and i + 1 < len(parts) - 1:
                mov = re.sub(r"^\d+\s*", "", parts[i+1]).strip()
                return "Hindi", f"Soundtracks\\{mov}", mov
    elif "albums" in p_lower:
        for i, p in enumerate(parts):
            if p.lower() == "albums" and i + 1 < len(parts) - 1:
                alb = re.sub(r"^\d+\s*", "", parts[i+1]).strip()
                return "Hindi", f"Albums\\{alb}", alb
    elif "new" in p_lower:
        for i, p in enumerate(parts):
            if p.lower() == "new" and i + 1 < len(parts) - 1:
                mov = re.sub(r"^\d+\s*", "", parts[i+1]).strip()
                if mov and mov.lower() not in ["new folder", "sama", "albums"]:
                    return "Hindi", f"Soundtracks\\{mov}", mov
    for art in ["lata", "kishore", "rafi", "mukesh", "pankaj udhas", "pankaj udas", "yesudas", "asha", "jagjit"]:
        if art in p_lower:
            canon = "Pankaj Udhas" if "pankaj" in art else art.title()
            return "Hindi", f"Artists\\{canon}", canon
            
    return None

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"\nAnalyzing 1091 Evergreen Classics tracks against F/J paths:")
resolved_counts = Counter()
for t in eg:
    sz = t.get('size_bytes', 0)
    fn = t['filename']
    n = norm(fn)
    hits = by_size.get(sz, []) or by_norm.get(n, [])
    resolved = None
    if hits:
        for h in hits:
            res = parse_orig_path(h)
            if res:
                resolved = res
                break
    if resolved:
        resolved_counts[f"{resolved[0]}: {resolved[1]}"] += 1
    else:
        resolved_counts["Unresolved (Remains Hindi)"] += 1

print("\nTop 30 newly resolved categories from Evergreen Classics:")
for k, v in resolved_counts.most_common(30):
    print(f"  {k}: {v} tracks")

print(f"\nTotal resolved from original backup: {sum(v for k, v in resolved_counts.items() if not k.startswith('Unresolved'))} / {len(eg)}")
conn.close()
