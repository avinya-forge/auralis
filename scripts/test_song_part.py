import sqlite3
import re
import json

DB_PATH = 'master_cross_drive_catalog.db'

def normalize_title(name: str) -> str:
    if not name:
        return ""
    s = re.sub(r"\.[a-zA-Z0-9]+$", "", name)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps|ringtone|webrip)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zA-Z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def clean_catalog_folder_name(folder: str) -> str:
    s = re.sub(r"\[.*?\]|\(.*?\)", "", folder)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"[^a-zA-Z0-9\s\-&']", " ", s)
    return re.sub(r"\s+", " ", s).strip(" .-_/\\").title()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
rows = c.fetchall()
conn.close()

index = {}
song_index = {}

for path, fname in rows:
    p_lower = path.lower()
    clean_fstem = re.sub(r"\.[a-zA-Z0-9]+$", "", fname)
    found_info = None
    song_part = None
    
    if "=" in clean_fstem:
        parts = clean_fstem.split("=", 1)
        m_cand = clean_catalog_folder_name(parts[0])
        song_part = parts[1]
        if m_cand and len(m_cand) > 2:
            found_info = ("Hindi", f"Soundtracks\\{m_cand}", m_cand)
    elif "___" in clean_fstem or "__" in clean_fstem:
        sep = "___" if "___" in clean_fstem else "__"
        parts = clean_fstem.split(sep, 1)
        m_cand = clean_catalog_folder_name(parts[0])
        song_part = parts[1]
        if m_cand and len(m_cand) > 2:
            found_info = ("Hindi", f"Soundtracks\\{m_cand}", m_cand)
            
    if found_info:
        fn_norm = normalize_title(fname)
        if fn_norm and len(fn_norm) > 3:
            index[fn_norm] = found_info
        if song_part:
            sp_norm = normalize_title(song_part)
            if sp_norm and len(sp_norm) > 3:
                song_index[sp_norm] = found_info

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

hits = 0
for t in eg:
    norm = normalize_title(t['filename'])
    res = index.get(norm) or song_index.get(norm)
    if res:
        hits += 1

print(f"Total Evergreen tested: {len(eg)}")
print(f"Direct song-part matches from catalog: {hits}")

print("\nSample 20 resolved:")
for t in eg:
    norm = normalize_title(t['filename'])
    res = index.get(norm) or song_index.get(norm)
    if res:
        print(f"  {t['filename']} -> {res}")
        hits += 1
        if hits > 20:
            break
