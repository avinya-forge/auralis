"""
Auralis - Fix Final Discrepancies
1. Moves Bollywood 'Rockstar' tracks from English\\Nickelback to Hindi\\Soundtracks\\Rockstar.
2. Moves Marathi songs (Gagan Sadan Tejomay, Pavool Padate Pudhe) to Marathi\\Lata Mangeshkar.
3. Merges D:\\Songs\\organized\\Ringtones into D:\\Songs\\organized\\Ringtones & Alerts.
4. Merges English\\John Lennon - The Gold Collection into English\\The Beatles.
5. Populates missing ID3 title tags with clean song titles.
"""

import os
import sys
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.path_sanitizer import clean_audio_title, sanitize_filename
from src.engine.master_acoustic_organizer import write_id3_metadata

ORGANIZED = r"D:\Songs\organized"

def fix_rockstar_tracks():
    nb_dir = os.path.join(ORGANIZED, "English", "Nickelback")
    target_dir = os.path.join(ORGANIZED, "Hindi", "Soundtracks", "Rockstar")
    os.makedirs(target_dir, exist_ok=True)

    moved = 0
    if os.path.exists(nb_dir):
        for f in os.listdir(nb_dir):
            if any(w in f.lower() for w in ["aur ho", "tum ho", "tum ko", "hawaa hawaa", "sheher mein", "katiya karun", "kun faya kun", "phir se ud chala", "saadda haq", "jo bhi main"]):
                src = os.path.join(nb_dir, f)
                # Clean song title
                clean_name = f.replace("Rockstar - - ", "").replace("Rockstar - ", "")
                dst = os.path.join(target_dir, clean_name)
                shutil.move(src, dst)
                write_id3_metadata(dst, clean_audio_title(os.path.splitext(clean_name)[0]), "A.R. Rahman", "Rockstar", "Hindi")
                moved += 1
    print(f"Moved {moved} Bollywood Rockstar tracks to Hindi\\Soundtracks\\Rockstar.")

def fix_marathi_tracks():
    lata_hindi = os.path.join(ORGANIZED, "Hindi", "Artists", "Lata Mangeshkar")
    lata_marathi = os.path.join(ORGANIZED, "Marathi", "Lata Mangeshkar")
    os.makedirs(lata_marathi, exist_ok=True)

    moved = 0
    if os.path.exists(lata_hindi):
        for f in os.listdir(lata_hindi):
            if "marathi" in f.lower() or any(w in f.lower() for w in ["gagan sadan", "pavool padate"]):
                src = os.path.join(lata_hindi, f)
                dst = os.path.join(lata_marathi, f)
                shutil.move(src, dst)
                write_id3_metadata(dst, clean_audio_title(os.path.splitext(f)[0]), "Lata Mangeshkar", "Marathi Bhavgeet", "Marathi")
                moved += 1
    print(f"Moved {moved} Marathi tracks to Marathi\\Lata Mangeshkar.")

def merge_ringtones():
    rt_src = os.path.join(ORGANIZED, "Ringtones")
    rt_dst = os.path.join(ORGANIZED, "Ringtones & Alerts")
    os.makedirs(rt_dst, exist_ok=True)

    moved = 0
    if os.path.exists(rt_src):
        for root, dirs, files in os.walk(rt_src):
            for f in files:
                sp = os.path.join(root, f)
                dp = os.path.join(rt_dst, f)
                if os.path.exists(dp):
                    stem, ext = os.path.splitext(dp)
                    dp = f"{stem} - Part 2{ext}"
                try:
                    shutil.move(sp, dp)
                    moved += 1
                except Exception:
                    pass
        try:
            shutil.rmtree(rt_src)
        except Exception:
            pass
    print(f"Merged {moved} ringtones into Ringtones & Alerts.")

def merge_john_lennon():
    jl_src = os.path.join(ORGANIZED, "English", "John Lennon - The Gold Collection")
    jl_dst = os.path.join(ORGANIZED, "English", "The Beatles")
    os.makedirs(jl_dst, exist_ok=True)

    moved = 0
    if os.path.exists(jl_src):
        for f in os.listdir(jl_src):
            sp = os.path.join(jl_src, f)
            dp = os.path.join(jl_dst, f)
            if os.path.exists(dp):
                stem, ext = os.path.splitext(dp)
                dp = f"{stem} - Part 2{ext}"
            try:
                shutil.move(sp, dp)
                moved += 1
            except Exception:
                pass
        try:
            shutil.rmtree(jl_src)
        except Exception:
            pass
    print(f"Merged {moved} John Lennon tracks into English\\The Beatles.")

def fix_missing_titles():
    import mutagen
    from mutagen.id3 import ID3, TIT2, ID3NoHeaderError

    tagged = 0
    for root, _, files in os.walk(ORGANIZED):
        for f in files:
            if not f.lower().endswith(".mp3"):
                continue
            fp = os.path.join(root, f)
            try:
                mf = mutagen.File(fp)
                if not mf or not mf.tags or "TIT2" not in mf.tags or not str(mf.tags["TIT2"]).strip():
                    try:
                        audio = ID3(fp)
                    except ID3NoHeaderError:
                        audio = ID3()
                    clean_title = clean_audio_title(os.path.splitext(f)[0])
                    audio["TIT2"] = TIT2(encoding=3, text=clean_title)
                    audio.save(fp, v2_version=3)
                    tagged += 1
            except Exception:
                pass
    print(f"Updated clean TIT2 tags for {tagged} files.")

def main():
    print("Executing final discrepancy fixes...")
    fix_rockstar_tracks()
    fix_marathi_tracks()
    merge_ringtones()
    merge_john_lennon()
    fix_missing_titles()
    print("Final discrepancy fixes complete!")

if __name__ == "__main__":
    main()
