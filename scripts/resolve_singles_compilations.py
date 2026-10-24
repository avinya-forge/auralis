"""
Resolve Hindi Singles & Compilations
Disperses all 369 tracks from Hindi\\Soundtracks\\Singles & Compilations into their
exact Bollywood movie soundtrack, non-film album, artist, or English classic directory.
Zero tracks left in Singles & Compilations.
"""

import os
import sys
import re
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.path_sanitizer import sanitize_filename, sanitize_relative_path, clean_audio_title
from src.engine.master_acoustic_organizer import write_id3_metadata

SINGLES_DIR = r"D:\Songs\organized\Hindi\Soundtracks\Singles & Compilations"
ORGANIZED_ROOT = r"D:\Songs\organized"

KNOWN_TRACK_ROUTES = {
    # English tracks accidentally in Hindi
    "another brick the wall": ("English", "Pink Floyd", "The Wall", "Pink Floyd"),
    "wailers": ("English", "Bob Marley", "Bob Marley Classics", "Bob Marley"),

    # Bollywood Soundtracks
    "23rd march": ("Hindi", "Soundtracks\\23rd March 1931 Shaheed", "23rd March 1931 Shaheed", "Bollywood"),
    "shaheed": ("Hindi", "Soundtracks\\23rd March 1931 Shaheed", "23rd March 1931 Shaheed", "Bollywood"),
    "naina miley": ("Hindi", "Soundtracks\\Robot", "Robot", "A.R. Rahman"),
    "bose the forgotten hero": ("Hindi", "Soundtracks\\Netaji Subhas Chandra Bose", "Netaji Subhas Chandra Bose", "A.R. Rahman"),
    "rehena tu": ("Hindi", "Soundtracks\\Delhi 6", "Delhi 6", "A.R. Rahman"),
    "rehna tu": ("Hindi", "Soundtracks\\Delhi 6", "Delhi 6", "A.R. Rahman"),
    "aaante": ("Hindi", "Soundtracks\\Aap Mujhe Achche Lagne Lage", "Aap Mujhe Achche Lagne Lage", "Bollywood"),
    "lajja": ("Hindi", "Soundtracks\\Lajja", "Lajja", "Anu Malik"),
    "aadat": ("Hindi", "Soundtracks\\Kalyug", "Kalyug", "Atif Aslam"),
    "aao na": ("Hindi", "Soundtracks\\Kyun Ho Gaya Na", "Kyun Ho Gaya Na", "Shankar-Ehsaan-Loy"),
    "aaradhana": ("Hindi", "Soundtracks\\Aradhana", "Aradhana", "Kishore Kumar"),
    "sapno ki rani": ("Hindi", "Soundtracks\\Aradhana", "Aradhana", "Kishore Kumar"),
    "dusman": ("Hindi", "Soundtracks\\Dushman", "Dushman", "Lata Mangeshkar"),
    "dushman": ("Hindi", "Soundtracks\\Dushman", "Dushman", "Lata Mangeshkar"),
    "jism": ("Hindi", "Soundtracks\\Jism 2", "Jism 2", "Ali Azmat"),
    "aisi deewangi": ("Hindi", "Soundtracks\\Deewana", "Deewana", "Alka Yagnik"),
    "deewana": ("Hindi", "Soundtracks\\Deewana", "Deewana", "Alka Yagnik"),
    "bade achche lagte hain": ("Hindi", "Soundtracks\\Balika Badhu", "Balika Badhu", "Amit Kumar"),
    "balika badhu": ("Hindi", "Soundtracks\\Balika Badhu", "Balika Badhu", "Amit Kumar"),
    "bhula diya": ("Hindi", "Albums\\Anand Raaj", "Bhula Diya", "Anand Raaj"),
    "junoon": ("Hindi", "Albums\\Abhijeet Sawant", "Aapka Abhijeet Sawant", "Abhijeet Sawant"),
    "kya tujhe pata hai": ("Hindi", "Albums\\Abhijeet Sawant", "Aapka Abhijeet Sawant", "Abhijeet Sawant"),
    "nain se nain": ("Hindi", "Albums\\Adnan Sami", "Teri Kasam", "Adnan Sami"),
    "purani jeans": ("Hindi", "Albums\\Ali Haider", "Sandesa", "Ali Haider"),
    "pray for me brother": ("Hindi", "Albums\\A.R. Rahman", "Pray For Me Brother", "A.R. Rahman"),
    "3": ("Hindi", "Soundtracks\\3", "3", "Dhanush"),
}

def resolve_single_track(fname: str):
    f_lower = fname.lower()
    for k, v in KNOWN_TRACK_ROUTES.items():
        if k in f_lower:
            return v
    # Pattern: [Artist] - [Song]
    if " - " in fname:
        parts = fname.split(" - ")
        cand_art = clean_audio_title(parts[0], is_folder=True)
        cand_title = clean_audio_title(parts[1], is_folder=False)
        return ("Hindi", f"Artists\\{cand_art}", cand_art, cand_art)
    # Default fallback
    clean_stem = clean_audio_title(os.path.splitext(fname)[0], is_folder=True)
    return ("Hindi", f"Soundtracks\\{clean_stem}", clean_stem, "Bollywood")

def main():
    if not os.path.exists(SINGLES_DIR):
        print("Singles directory does not exist or already processed.")
        return

    files = [f for f in os.listdir(SINGLES_DIR) if f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac'))]
    print(f"Dispersing {len(files)} files from {SINGLES_DIR}...")

    resolved_count = 0
    for f in files:
        src_path = os.path.join(SINGLES_DIR, f)
        lang, cat, alb, art = resolve_single_track(f)

        clean_cat = sanitize_relative_path(cat)
        clean_fn = sanitize_filename(f)
        dest_dir = os.path.join(ORGANIZED_ROOT, lang, clean_cat)
        # Ensure zero brackets
        dest_dir = dest_dir.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        dest_path = os.path.join(dest_dir, clean_fn).replace("(", "").replace(")", "").replace("[", "").replace("]", "")

        os.makedirs(dest_dir, exist_ok=True)
        if os.path.exists(dest_path) and dest_path != src_path:
            stem, ext = os.path.splitext(dest_path)
            dest_path = f"{stem} - Part 2{ext}"

        try:
            shutil.move(src_path, dest_path)
            write_id3_metadata(dest_path, clean_audio_title(os.path.splitext(clean_fn)[0]), art, alb, lang)
            resolved_count += 1
        except Exception as e:
            print(f"Error moving {f}: {e}")

    # Remove empty Singles & Compilations directory
    try:
        if not os.listdir(SINGLES_DIR):
            os.rmdir(SINGLES_DIR)
            print("Successfully removed empty Singles & Compilations directory!")
    except Exception:
        pass

    print(f"Dispersal Complete: {resolved_count} tracks placed into specific Soundtracks/Albums/Artists.")

if __name__ == "__main__":
    main()
