"""
Auralis - Consolidate Single-File Artist Folders to Ensure >= 2 Tracks Per Folder
1. English single-file artists -> Move to English\\Singles (while preserving Artist, Title, Album, Artwork tags).
2. Hindi single-file soundtracks -> Move to Hindi\\Soundtracks\\Soundtrack Singles (preserving all tags).
3. Marathi single-file artist -> Move Pralhad Shinde Bappa Morya Re to Marathi\\Ganpati Geete (preserving all tags).
4. Sweep all resulting empty directories.
"""

import os
import shutil

ORGANIZED_ROOT = r"D:\Songs\organized"

def consolidate_single_files():
    print("=" * 80)
    print("CONSOLIDATING SINGLE-FILE FOLDERS")
    print("=" * 80)

    # 1. Marathi Pralhad Shinde -> Ganpati Geete
    ps_file = os.path.join(ORGANIZED_ROOT, "Marathi", "Pralhad Shinde", "Bappa Morya Re.mp3")
    if os.path.exists(ps_file):
        dst = os.path.join(ORGANIZED_ROOT, "Marathi", "Ganpati Geete", "Bappa Morya Re.mp3")
        shutil.move(ps_file, dst)
        print(f"[MOVED] {ps_file} -> {dst}")

    # 2. Hindi single-file soundtracks -> Soundtrack Singles
    st_singles_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Soundtrack Singles")
    os.makedirs(st_singles_dir, exist_ok=True)

    klsh_file = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Kya Love Story Hai", "It's Rocking.mp3")
    if os.path.exists(klsh_file):
        dst = os.path.join(st_singles_dir, "It's Rocking.mp3")
        shutil.move(klsh_file, dst)
        print(f"[MOVED] {klsh_file} -> {dst}")

    raaz_file = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Raaz The Mystery Continues", "Soniyo.mp3")
    if os.path.exists(raaz_file):
        dst = os.path.join(st_singles_dir, "Soniyo.mp3")
        shutil.move(raaz_file, dst)
        print(f"[MOVED] {raaz_file} -> {dst}")

    # 3. English single-file artist folders -> English\Singles
    english_root = os.path.join(ORGANIZED_ROOT, "English")
    english_singles_dir = os.path.join(english_root, "Singles")
    os.makedirs(english_singles_dir, exist_ok=True)

    for item in list(os.listdir(english_root)):
        sub_dir = os.path.join(english_root, item)
        if os.path.isdir(sub_dir) and item not in ["Singles", "Assorted Pop & Rock", "Classic Rock", "Trance", "Indian Rock Bands"]:
            files = [f for f in os.listdir(sub_dir) if os.path.isfile(os.path.join(sub_dir, f))]
            subdirs = [d for d in os.listdir(sub_dir) if os.path.isdir(os.path.join(sub_dir, d))]
            if len(files) == 1 and len(subdirs) == 0:
                single_file = files[0]
                src = os.path.join(sub_dir, single_file)
                dst = os.path.join(english_singles_dir, single_file)
                if os.path.exists(dst):
                    base, ext = os.path.splitext(single_file)
                    dst = os.path.join(english_singles_dir, f"{base} - {item}{ext}")
                shutil.move(src, dst)
                print(f"[MOVED TO SINGLES] {src} -> {dst}")

    # 4. Sweep empty directories
    print("\nSweeping empty directories...")
    deleted = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        if root == ORGANIZED_ROOT:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
                print(f"[REMOVED] {root}")
                deleted += 1
            except Exception as e:
                print(f"Error removing {root}: {e}")
    print(f"Total empty directories removed: {deleted}")

if __name__ == "__main__":
    consolidate_single_files()
