import sys, os, sqlite3
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.engine.pattern_classifier import extract_bollywood_movie_and_song, clean_watermarks

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT filename FROM master_audio_catalog WHERE (file_path LIKE '%Hindi%' OR file_path LIKE '%Old%') AND (filename LIKE '%=%' OR filename LIKE '%___%' OR filename LIKE '%__%')")
rows = c.fetchall()
print('Catalog files with movie separator:', len(rows))
sample_res = {}
for r in rows[:15]:
    fn = r[0]
    stem = fn[:-4] if fn.endswith(('.mp3', '.MP3', '.wma')) else fn
    m, s = extract_bollywood_movie_and_song(clean_watermarks(stem), stem, '', '', '', '')
    sample_res[fn] = (m, s)

for k, v in sample_res.items():
    print(k, '-->', v)
