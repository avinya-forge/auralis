import os
import difflib

ORGANIZED_ROOT = r"D:\Songs\organized\Hindi\Soundtracks"
prefixed_movies = []

for movie in os.listdir(ORGANIZED_ROOT):
    mp = os.path.join(ORGANIZED_ROOT, movie)
    if not os.path.isdir(mp):
        continue
    files = [f for f in os.listdir(mp) if f.lower().endswith(('.mp3', '.wma', '.m4a'))]
    if not files:
        continue
    
    prefixed_files = []
    for f in files:
        if " - " in f:
            pfx = f.split(" - ")[0].strip()
            # Similarity ratio between movie directory name and prefix
            ratio = difflib.SequenceMatcher(None, movie.lower(), pfx.lower()).ratio()
            # Also check if words in movie match prefix
            m_words = set(movie.lower().split())
            p_words = set(pfx.lower().split())
            if ratio >= 0.65 or (len(m_words & p_words) >= 1 and len(p_words) <= 3 and len(m_words) <= 3):
                prefixed_files.append((f, pfx, ratio))
    if prefixed_files:
        prefixed_movies.append((movie, len(prefixed_files), len(files), prefixed_files))

print(f"Total movie soundtrack folders with movie prefixes: {len(prefixed_movies)}")
for m, cnt, tot, flist in prefixed_movies:
    print(f"\n[{m}] ({cnt}/{tot} files):")
    for f, pfx, ratio in flist:
        print(f"   {f} -> Prefix: '{pfx}' (Ratio: {ratio:.2f})")
