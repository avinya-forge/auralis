"""
Auralis - Consolidate Synonyms, Disambiguate Albums, and Resolve Part Files
Executes targeted consolidations:
1. Hindi\\Devotional vs Hindi\\Devotional & Bhajans
2. English\\Rock & Pop vs English\\Assorted Pop & Rock (+ Imagine Dragons artist folder)
3. Hindi\\Soundtracks\\Hamrahi vs Hindi\\Soundtracks\\Humrahi (upgrade to 192kbps master)
4. Hindi\\Albums\\Love Story (disambiguate & rehome) + Hindi\\Soundtracks\\Love Story -> Love Story 2050
5. Hindi\\Albums\\Atif Aslam (merge Doorie & Meri Kahani, dedupe 64k part2)
6. Cryptic Part Files resolution (Demonic Resurrection, Zero, U2, Westlife, Rafi, Bodyguard, Jodhaa Akbar, Lakshya, Oye Lucky, Soundtrack Singles)
7. Clean up all resulting empty directories
"""

import os
import shutil
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB

ORGANIZED_ROOT = r"D:\Songs\organized"
BACKUP_DIR = r"D:\Songs\unorganized\_duplicates_backup"

os.makedirs(BACKUP_DIR, exist_ok=True)

def update_tags(filepath, title=None, artist=None, album=None):
    """Update title, artist, album while strictly preserving artwork."""
    try:
        audio = mutagen.File(filepath)
        if audio is None:
            return
        if not audio.tags:
            audio.add_tags()
        
        # We use standard ID3 for mp3
        if hasattr(audio, 'tags') and isinstance(audio.tags, ID3):
            if title:
                audio.tags.setall('TIT2', [TIT2(encoding=3, text=[title])])
            if artist:
                audio.tags.setall('TPE1', [TPE1(encoding=3, text=[artist])])
            if album:
                audio.tags.setall('TALB', [TALB(encoding=3, text=[album])])
            audio.save()
        else:
            try:
                ez = EasyID3(filepath)
                if title: ez['title'] = [title]
                if artist: ez['artist'] = [artist]
                if album: ez['album'] = [album]
                ez.save()
            except Exception:
                pass
    except Exception as e:
        print(f"Error updating tags for {filepath}: {e}")

def safe_move(src, dst):
    """Safe move with target dir creation."""
    if not os.path.exists(src):
        print(f"[SKIP] Source does not exist: {src}")
        return False
    dst_dir = os.path.dirname(dst)
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(dst):
        print(f"[COLLISION] Destination already exists: {dst}")
        return False
    shutil.move(src, dst)
    print(f"[MOVED] {src} -> {dst}")
    return True

def safe_rename(old_path, new_name):
    """Atomic rename on Windows."""
    if not os.path.exists(old_path):
        print(f"[SKIP] Path does not exist: {old_path}")
        return None
    parent = os.path.dirname(old_path)
    new_path = os.path.join(parent, new_name)
    if old_path.lower() == new_path.lower() and old_path != new_path:
        # Case-only change
        tmp_path = os.path.join(parent, f"__tmp_ren_{os.path.basename(old_path)}")
        os.rename(old_path, tmp_path)
        os.rename(tmp_path, new_path)
    else:
        os.rename(old_path, new_path)
    print(f"[RENAMED] {old_path} -> {new_path}")
    return new_path

def run_consolidation():
    print("=" * 80)
    print("STARTING SYNONYM CONSOLIDATION AND PART RESOLUTION")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Hindi Devotional Consolidation
    # -------------------------------------------------------------
    print("\n--- 1. Consolidating Hindi Devotional ---")
    dev_root = os.path.join(ORGANIZED_ROOT, "Hindi", "Devotional")
    dev_bhajans_root = os.path.join(ORGANIZED_ROOT, "Hindi", "Devotional & Bhajans")
    dev_classics_target = os.path.join(dev_root, "Devotional Classics")
    os.makedirs(dev_classics_target, exist_ok=True)

    # Move 21 loose files in Hindi\Devotional into Devotional Classics
    if os.path.exists(dev_root):
        for item in list(os.listdir(dev_root)):
            ip = os.path.join(dev_root, item)
            if os.path.isfile(ip):
                target = os.path.join(dev_classics_target, item)
                if not os.path.exists(target):
                    safe_move(ip, target)

    # Move Anup Jalota from Devotional & Bhajans to Devotional\Anup Jalota
    if os.path.exists(dev_bhajans_root):
        aj_src = os.path.join(dev_bhajans_root, "Anup Jalota")
        aj_dst = os.path.join(dev_root, "Anup Jalota")
        if os.path.exists(aj_src):
            if not os.path.exists(aj_dst):
                safe_move(aj_src, aj_dst)
            else:
                for f in os.listdir(aj_src):
                    safe_move(os.path.join(aj_src, f), os.path.join(aj_dst, f))

        # Move Devotional Classics contents from Devotional & Bhajans
        dc_src = os.path.join(dev_bhajans_root, "Devotional Classics")
        if os.path.exists(dc_src):
            for f in os.listdir(dc_src):
                safe_move(os.path.join(dc_src, f), os.path.join(dev_classics_target, f))

        # Move loose files from Devotional & Bhajans
        for f in os.listdir(dev_bhajans_root):
            fp = os.path.join(dev_bhajans_root, f)
            if os.path.isfile(fp):
                safe_move(fp, os.path.join(dev_classics_target, f))

    # -------------------------------------------------------------
    # 2. English Rock & Pop -> English Assorted Pop & Rock
    # -------------------------------------------------------------
    print("\n--- 2. Consolidating English Rock & Pop ---")
    rock_pop_src = os.path.join(ORGANIZED_ROOT, "English", "Rock & Pop")
    assorted_dst = os.path.join(ORGANIZED_ROOT, "English", "Assorted Pop & Rock")
    imagine_dragons_dst = os.path.join(ORGANIZED_ROOT, "English", "Imagine Dragons")
    michael_dst = os.path.join(ORGANIZED_ROOT, "English", "Michael Jackson")
    os.makedirs(assorted_dst, exist_ok=True)
    os.makedirs(imagine_dragons_dst, exist_ok=True)

    if os.path.exists(rock_pop_src):
        # Specific track extractions
        believer = os.path.join(rock_pop_src, "Imagine Dragons Believer.mp3")
        if os.path.exists(believer):
            dst = os.path.join(imagine_dragons_dst, "Believer.mp3")
            safe_move(believer, dst)
            update_tags(dst, title="Believer", artist="Imagine Dragons")

        thunder = os.path.join(rock_pop_src, "Imagine Dragons Thunder.mp3")
        if os.path.exists(thunder):
            dst = os.path.join(imagine_dragons_dst, "Thunder.mp3")
            safe_move(thunder, dst)
            update_tags(dst, title="Thunder", artist="Imagine Dragons")

        you_rock = os.path.join(rock_pop_src, "You Rock My World Radio Edit.mp3")
        if os.path.exists(you_rock):
            dst = os.path.join(michael_dst, "You Rock My World - Radio Edit.mp3")
            safe_move(you_rock, dst)
            update_tags(dst, title="You Rock My World (Radio Edit)", artist="Michael Jackson")

        queen_rock = os.path.join(rock_pop_src, "We Will Rock You -Queen02 S.mp3")
        if os.path.exists(queen_rock):
            dst = os.path.join(BACKUP_DIR, "We Will Rock You -Queen02 S.mp3")
            safe_move(queen_rock, dst)

        charles = os.path.join(rock_pop_src, "Charles Aznavour-For Me Formidable.mp3")
        if os.path.exists(charles):
            dst = os.path.join(assorted_dst, "For Me Formidable.mp3")
            safe_move(charles, dst)
            update_tags(dst, title="For Me Formidable", artist="Charles Aznavour")

        satriani = os.path.join(rock_pop_src, "Joe Satriani-I Believe.mp3")
        if os.path.exists(satriani):
            dst = os.path.join(assorted_dst, "I Believe.mp3")
            safe_move(satriani, dst)
            update_tags(dst, title="I Believe", artist="Joe Satriani")

        pretty_woman = os.path.join(rock_pop_src, "Oh Pretty Woman- Rockapella.mp3")
        if os.path.exists(pretty_woman):
            dst = os.path.join(assorted_dst, "Oh Pretty Woman.mp3")
            safe_move(pretty_woman, dst)
            update_tags(dst, title="Oh Pretty Woman", artist="Rockapella")

        # Move all remaining files in Rock & Pop to Assorted Pop & Rock
        for f in list(os.listdir(rock_pop_src)):
            src_file = os.path.join(rock_pop_src, f)
            if os.path.isfile(src_file):
                dst_file = os.path.join(assorted_dst, f)
                if not os.path.exists(dst_file):
                    safe_move(src_file, dst_file)
                else:
                    safe_move(src_file, os.path.join(BACKUP_DIR, f))

    # -------------------------------------------------------------
    # 3. Hindi Soundtracks: Hamrahi & Humrahi
    # -------------------------------------------------------------
    print("\n--- 3. Consolidating Hamrahi & Humrahi ---")
    hamrahi_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Hamrahi")
    humrahi_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Humrahi")
    os.makedirs(hamrahi_dir, exist_ok=True)

    if os.path.exists(humrahi_dir):
        # Move Man Re Tuhi Bata
        mrtb = os.path.join(humrahi_dir, "Man Re Tuhi Bata.mp3")
        if os.path.exists(mrtb):
            safe_move(mrtb, os.path.join(hamrahi_dir, "Man Re Tuhi Bata.mp3"))

        # Upgrade Yeh Aansoo with 192k master
        master_ya = os.path.join(humrahi_dir, "Yeh Aansoo Mere Dil Ki Zub.mp3")
        low_ya = os.path.join(hamrahi_dir, "Yeh Ansoo Mere Dil Ki Zuban Hai.mp3")
        if os.path.exists(low_ya):
            safe_move(low_ya, os.path.join(BACKUP_DIR, "Yeh Ansoo Mere Dil Ki Zuban Hai_128k.mp3"))
        if os.path.exists(master_ya):
            target_ya = os.path.join(hamrahi_dir, "Yeh Aansoo Mere Dil Ki Zubaan Hai.mp3")
            safe_move(master_ya, target_ya)
            update_tags(target_ya, title="Yeh Aansoo Mere Dil Ki Zubaan Hai", artist="Mukesh", album="Hamrahi")

    # -------------------------------------------------------------
    # 4. Hindi Albums Love Story & Soundtracks Love Story 2050
    # -------------------------------------------------------------
    print("\n--- 4. Disambiguating Love Story ---")
    album_ls = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums", "Love Story")
    if os.path.exists(album_ls):
        delhi_belly = os.path.join(album_ls, "Delhi Belly - I Hate You Like I Love You.mp3")
        if os.path.exists(delhi_belly):
            dst = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Delhi Belly", "I Hate You Like I Love You.mp3")
            safe_move(delhi_belly, dst)
            update_tags(dst, title="I Hate You Like I Love You", artist="Keerthi Sagathia & Shazneen Arethna", album="Delhi Belly")

        rkmania = os.path.join(album_ls, "I Hate You Like I Love You - Rkmania.mp3")
        if os.path.exists(rkmania):
            safe_move(rkmania, os.path.join(BACKUP_DIR, "I Hate You Like I Love You - Rkmania.mp3"))

        ily = os.path.join(album_ls, "I Love You.mp3")
        if os.path.exists(ily):
            safe_move(ily, os.path.join(BACKUP_DIR, "I Love You_LoveStory_dupe.mp3"))

        tera_deewana = os.path.join(album_ls, "Tera Deewana.mp3")
        if os.path.exists(tera_deewana):
            dst = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums", "Adnan Sami", "Tera Deewana.mp3")
            safe_move(tera_deewana, dst)
            update_tags(dst, title="Tera Deewana", artist="Adnan Sami", album="Tera Chehra")

        ranjish = os.path.join(album_ls, "Ranjish Hi Sahi.mp3")
        if os.path.exists(ranjish):
            dst = os.path.join(ORGANIZED_ROOT, "Hindi", "Ghazals", "Mehdi Hassan", "Ranjish Hi Sahi.mp3")
            safe_move(ranjish, dst)
            update_tags(dst, title="Ranjish Hi Sahi", artist="Mehdi Hassan", album="Ghazals")

    # Soundtracks Love Story -> Love Story 2050
    st_ls = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Love Story")
    st_ls2050 = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Love Story 2050")
    if os.path.exists(st_ls):
        safe_rename(st_ls, "Love Story 2050")
    
    # Rename internal Part files in Love Story 2050
    if os.path.exists(st_ls2050):
        meelon_part = os.path.join(st_ls2050, "Meelon Ka Part.mp3")
        if os.path.exists(meelon_part):
            target = safe_rename(meelon_part, "Meelon Ka Jaise Tha Part 2.mp3")
            update_tags(target, title="Meelon Ka Jaise Tha (Part 2)", artist="KK", album="Love Story 2050")
        
        part1 = os.path.join(st_ls2050, "Part.mp3")
        if os.path.exists(part1):
            target = safe_rename(part1, "Love Story Part 1.mp3")
            update_tags(target, title="Love Story (Part 1)", artist="Shaan & Nihira Joshi", album="Love Story 2050")

        # Update album tags for all tracks in Love Story 2050
        for f in os.listdir(st_ls2050):
            fp = os.path.join(st_ls2050, f)
            if os.path.isfile(fp):
                update_tags(fp, album="Love Story 2050")

    # -------------------------------------------------------------
    # 5. Hindi Albums: Atif Aslam Consolidation
    # -------------------------------------------------------------
    print("\n--- 5. Consolidating Atif Aslam Albums ---")
    atif_target = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums", "Atif Aslam")
    os.makedirs(atif_target, exist_ok=True)

    atif_doorie = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums", "Atif Aslam - Doorie")
    if os.path.exists(atif_doorie):
        p2 = os.path.join(atif_doorie, "Part 2.mp3")
        if os.path.exists(p2):
            safe_move(p2, os.path.join(BACKUP_DIR, "Atif_Aslam_Doorie_Part2_64k.mp3"))
        for f in list(os.listdir(atif_doorie)):
            safe_move(os.path.join(atif_doorie, f), os.path.join(atif_target, f))

    atif_mk = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums", "Meri Kahani")
    if os.path.exists(atif_mk):
        for f in list(os.listdir(atif_mk)):
            safe_move(os.path.join(atif_mk, f), os.path.join(atif_target, f))

    # -------------------------------------------------------------
    # 6. Cryptic Part Files Resolution
    # -------------------------------------------------------------
    print("\n--- 6. Resolving Cryptic Part Files ---")
    part_resolutions = [
        # Demonic Resurrection
        (os.path.join(ORGANIZED_ROOT, "English", "Indian Rock Bands", "Demonic Resurrection", "Part 2.mp3"),
         "Apocalyptic Dawn.mp3", "Apocalyptic Dawn", "Demonic Resurrection", "A Darkness Descends"),
        # Zero
        (os.path.join(ORGANIZED_ROOT, "English", "Indian Rock Bands", "Zero", "Part 2.mp3"),
         "Found.mp3", "Found", "Zero", "Albummed"),
        # U2 Part 3
        (os.path.join(ORGANIZED_ROOT, "English", "U2", "Part 3.mp3"),
         "With or Without You.mp3", "With or Without You", "U2", "The Joshua Tree"),
        # Westlife
        (os.path.join(ORGANIZED_ROOT, "English", "Westlife", "Part 2.mp3"),
         "Swear It Again.mp3", "Swear It Again", "Westlife", "Westlife"),
        # Bodyguard Part 2
        (os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Bodyguard", "Part 2.mp3"),
         "Bodyguard - Title Track Remix.mp3", "Bodyguard (Remix)", "Salman Khan & Band of Power", "Bodyguard"),
        # Jodhaa Akbar Part 2
        (os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Jodhaa Akbar", "Part 2.mp3"),
         "Jashn E Baharaa - Instrumental.mp3", "Jashn-E-Baharaa (Instrumental)", "A.R. Rahman", "Jodhaa Akbar"),
        # Oye Lucky Lucky Oye Part 2
        (os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Oye Lucky Lucky Oye", "Part 2.mp3"),
         "Oye Lucky - Title Track.mp3", "Oye Lucky (Title Track)", "Mika Singh", "Oye Lucky! Lucky Oye!"),
        # Soundtrack Singles Part 2
        (os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Soundtrack Singles", "Part 2.mp3"),
         "Ek Mahal Ho Sapno Ka.mp3", "Ek Mahal Ho Sapno Ka", "Kishore Kumar & Lata Mangeshkar", "Ek Mahal Ho Sapno Ka"),
    ]

    for old_path, new_name, title, artist, album in part_resolutions:
        if os.path.exists(old_path):
            new_path = safe_rename(old_path, new_name)
            if new_path:
                update_tags(new_path, title=title, artist=artist, album=album)

    # U2 Part 2 (duplicate of All I Want Is You) -> backup
    u2_p2 = os.path.join(ORGANIZED_ROOT, "English", "U2", "Part 2.mp3")
    if os.path.exists(u2_p2):
        safe_move(u2_p2, os.path.join(BACKUP_DIR, "U2_All_I_Want_Is_You_Part2.mp3"))

    # Lata Mangeshkar Part 2 -> Mohammed Rafi (Koi Sagar Dil Ko Bahlata Nahin)
    lata_p2 = os.path.join(ORGANIZED_ROOT, "Hindi", "Artists", "Lata Mangeshkar", "Part 2.mp3")
    if os.path.exists(lata_p2):
        rafi_target = os.path.join(ORGANIZED_ROOT, "Hindi", "Artists", "Mohammed Rafi", "Koi Sagar Dil Ko Bahlata Nahin.mp3")
        safe_move(lata_p2, rafi_target)
        update_tags(rafi_target, title="Koi Sagar Dil Ko Bahlata Nahin", artist="Mohammed Rafi", album="Dil Diya Dard Liya")

    # Lakshya Part 2 (320kbps master) -> Replace 96kbps Lakshya.mp3
    lakshya_low = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Lakshya", "Lakshya.mp3")
    lakshya_p2 = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Lakshya", "Part 2.mp3")
    if os.path.exists(lakshya_low) and os.path.exists(lakshya_p2):
        safe_move(lakshya_low, os.path.join(BACKUP_DIR, "Lakshya_96k.mp3"))
        new_path = safe_rename(lakshya_p2, "Lakshya - Title Track.mp3")
        update_tags(new_path, title="Lakshya (Title Track)", artist="Shankar Mahadevan", album="Lakshya")

    # -------------------------------------------------------------
    # 7. Sweep Empty Directories
    # -------------------------------------------------------------
    print("\n--- 7. Sweeping Empty Directories ---")
    deleted_count = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        if root == ORGANIZED_ROOT:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
                print(f"[REMOVED EMPTY DIR] {root}")
                deleted_count += 1
            except Exception as e:
                print(f"Error removing {root}: {e}")
    print(f"Total empty directories deleted: {deleted_count}")

    print("\n" + "=" * 80)
    print("CONSOLIDATION AND PART RESOLUTION FINISHED")
    print("=" * 80)

if __name__ == "__main__":
    run_consolidation()
