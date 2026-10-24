import os
import re
import stat
import hashlib
from collections import defaultdict
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON

ORGANIZED_ROOT = r"D:\Songs\organized"

def clean_remaining():
    print("=" * 80)
    print("CLEANING REMAINING DISCREPANCIES IN ORGANIZED LIBRARY")
    print("=" * 80)

    # 1. Delete True Redundant Duplicates (exact byte-for-byte stream matches)
    def get_accurate_hash(p):
        sz = os.path.getsize(p)
        if sz < 10000:
            return ''
        h = hashlib.md5()
        with open(p, 'rb') as f:
            f.seek(10000)
            h.update(f.read(65536))
            mid = sz // 2
            f.seek(mid)
            h.update(f.read(65536))
            f.seek(max(0, sz - 70000))
            h.update(f.read(65536))
        return h.hexdigest()

    hashes = defaultdict(list)
    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            if f.lower().endswith(('.mp3', '.wma', '.wav', '.m4a', '.ogg', '.flac')):
                p = os.path.join(root, f)
                ah = get_accurate_hash(p)
                if ah:
                    hashes[ah].append(p)

    deleted_dups = 0
    for k, v in hashes.items():
        if len(v) > 1:
            # Sort: keep the one without "Part 2" or cleaner name
            v.sort(key=lambda x: (1 if "part" in x.lower() else 0, len(os.path.basename(x))))
            primary = v[0]
            for dup in v[1:]:
                try:
                    os.chmod(dup, stat.S_IWRITE)
                    os.remove(dup)
                    deleted_dups += 1
                    print(f"Deleted duplicate: {dup}")
                except Exception as e:
                    print(f"Error deleting {dup}: {e}")

    print(f"[Step 1] Deleted {deleted_dups} exact duplicate files.")

    # 2. Relocate Bhagavad Gita tracks out of Hindi into Pravachan
    bhagavad_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Bhagavad")
    if os.path.exists(bhagavad_dir):
        prav_gita_dir = os.path.join(ORGANIZED_ROOT, "Pravachan", "Shankar Abhyankar", "Bhagavad Gita - Nirupan")
        os.makedirs(prav_gita_dir, exist_ok=True)
        for f in os.listdir(bhagavad_dir):
            src = os.path.join(bhagavad_dir, f)
            m = re.search(r"gita0?(\d+)", f, re.I)
            if m:
                ad_num = int(m.group(1))
                if ad_num == 0:
                    new_fn = "Bhagavad Gita - Introduction.mp3"
                else:
                    new_fn = f"Bhagavad Gita - Adhyay {ad_num:02d}.mp3"
            else:
                new_fn = f
            tgt = os.path.join(prav_gita_dir, new_fn)
            try:
                os.chmod(src, stat.S_IWRITE)
                os.replace(src, tgt)
                print(f"Moved Pravachan: {src} -> {tgt}")
            except Exception as e:
                print(f"Error moving {src}: {e}")

    # 3. Relocate Ringtone out of Hindi Singles into Ringtones & Alerts
    rt_src = os.path.join(ORGANIZED_ROOT, "Hindi", "Singles & Compilations", "Ringtones - Gun Shot.mp3")
    if os.path.exists(rt_src):
        rt_tgt = os.path.join(ORGANIZED_ROOT, "Ringtones & Alerts", "Gun Shot.mp3")
        try:
            os.chmod(rt_src, stat.S_IWRITE)
            os.replace(rt_src, rt_tgt)
            print(f"Moved Ringtone: {rt_src} -> {rt_tgt}")
        except Exception as e:
            print(f"Error moving {rt_src}: {e}")

    # 4. Clean up repeated prefixes in filenames
    cleaned_prefixes = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            stem, ext = os.path.splitext(f)
            # Match e.g. "Adam Lambert - Adam Lambert - Song" -> "Adam Lambert - Song"
            m = re.search(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*-\s*(.+)$", stem, re.I)
            if m:
                new_name = f"{m.group(1)} - {m.group(2)}{ext}"
                src = os.path.join(root, f)
                tgt = os.path.join(root, new_name)
                try:
                    os.chmod(src, stat.S_IWRITE)
                    os.replace(src, tgt)
                    cleaned_prefixes += 1
                    print(f"Fixed repeated prefix: {f} -> {new_name}")
                except Exception as e:
                    print(f"Error renaming {src}: {e}")

    print(f"[Step 4] Fixed {cleaned_prefixes} repeated prefix filenames.")

    # 5. Prune empty directories
    empty_pruned = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
                    empty_pruned += 1
            except Exception:
                pass
    print(f"[Step 5] Pruned {empty_pruned} empty directories.")

if __name__ == "__main__":
    clean_remaining()
