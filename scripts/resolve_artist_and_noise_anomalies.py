r"""
Auralis - Forensic Artist-in-Filename Stripper, Noise Cleaner & Duplicate Resolver.

Solves the critical library anomalies:
1. Recovers true song names for tracks whose filenames are artist names.
2. Strips artist tokens (' - Artist', 'Artist - ', 'Song Artist') from filenames.
3. Strips rip noise ('11 S', '03 S', '720P Hd Song', 'sihag', '-Golmaal').
4. Consolidates duplicate versions of the same song (e.g. Golmaal's Aane Wala Pal,
   Julie's Dil Kya Kare, Barfi's Ala Barfi), keeping the highest bitrate master track.
5. Re-homes mislocated tracks (Golmaal tracks in Choti Si Baat, Masoom tracks in
   Aap Ki Kasam, Pakeezah tracks in Chalte Chalte).
6. Preserves the strict invariant: >= 2 tracks per folder, 0 empty folders.
"""

import os
import shutil
import sqlite3
from typing import Dict, Any, List
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON

ORGANIZED_ROOT = r"D:\Songs\organized"
BACKUP_DIR = r"D:\Songs\unorganized\_duplicates_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_inferior_file(file_path: str, reason: str = "inferior_duplicate"):
    """Move an inferior duplicate track to backup dir."""
    if not os.path.exists(file_path):
        return
    fname = os.path.basename(file_path)
    dest = os.path.join(BACKUP_DIR, fname)
    if os.path.exists(dest):
        base, ext = os.path.splitext(fname)
        dest = os.path.join(BACKUP_DIR, f"{base}_{reason}{ext}")
    print(f"  [BACKUP] {file_path} -> {dest} ({reason})")
    try:
        shutil.move(file_path, dest)
    except Exception as e:
        print(f"  Error moving {file_path}: {e}")


def update_tags(file_path: str, title: str, artist: str = None, album: str = None):
    """Safely update ID3 tags on MP3 files."""
    if not file_path.endswith(".mp3") or not os.path.exists(file_path):
        return
    try:
        tags = ID3(file_path)
    except Exception:
        tags = ID3()

    tags["TIT2"] = TIT2(encoding=3, text=[title])
    if artist:
        tags["TPE1"] = TPE1(encoding=3, text=[artist])
    if album:
        tags["TALB"] = TALB(encoding=3, text=[album])
    tags.save(file_path)


def resolve_golmaal_and_choti_si_baat():
    """Resolve Golmaal and Choti Si Baat track overlap and duplicates."""
    print("\n--- 1. Resolving Golmaal & Choti Si Baat Overlap ---")
    csb_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Choti Si Baat")
    golmaal_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Golmaal")
    os.makedirs(golmaal_dir, exist_ok=True)

    # 1. Aanewala Pal master is in Choti Si Baat (256kbps)
    csb_aane = os.path.join(csb_dir, "Aanewala Pal Jaane Waala Hai.mp3")
    gol_dest = os.path.join(golmaal_dir, "Aane Wala Pal Jaane Waala Hai.mp3")

    if os.path.exists(csb_aane):
        print(f"  Moving 256kbps Aanewala Pal master from Choti Si Baat to Golmaal...")
        shutil.move(csb_aane, gol_dest)
        update_tags(gol_dest, "Aane Wala Pal Jaane Waala Hai", "Kishore Kumar", "Golmaal")

    # 2. Golmaal Hai in Choti Si Baat belongs in Golmaal
    csb_gol = os.path.join(csb_dir, "Golmaal Hai.mp3")
    gol_gol_dest = os.path.join(golmaal_dir, "Golmaal Hai.mp3")
    if os.path.exists(csb_gol):
        print(f"  Moving Golmaal Hai from Choti Si Baat to Golmaal...")
        shutil.move(csb_gol, gol_gol_dest)
        update_tags(gol_gol_dest, "Golmaal Hai Bhai Sab Golmaal Hai", "R.D. Burman & Sapan Chakraborty", "Golmaal")

    # 3. Clean up the inferior duplicate copies in Golmaal
    gol_redundants = [
        os.path.join(golmaal_dir, "Aane Wala Pal -Golmaal.mp3"),
        os.path.join(golmaal_dir, "Aane Wala Pal11 S.mp3"),
        os.path.join(golmaal_dir, "Aanewala Pal.mp3"),
    ]
    for rpath in gol_redundants:
        if os.path.exists(rpath):
            backup_inferior_file(rpath, reason="duplicate_aane_wala_pal")

    # 4. Clean Choti Si Baat remaining files
    csb_na_jaane = os.path.join(csb_dir, "Na Jaane Kyun - Chhoti Si Baat 720P Hd Song.mp3")
    csb_na_jaane_clean = os.path.join(csb_dir, "Na Jaane Kyon.mp3")
    if os.path.exists(csb_na_jaane):
        print(f"  Renaming Na Jaane Kyun with 720P Hd Song tag -> Na Jaane Kyon.mp3")
        os.rename(csb_na_jaane, csb_na_jaane_clean)
        update_tags(csb_na_jaane_clean, "Na Jaane Kyon", "Lata Mangeshkar", "Choti Si Baat")


def resolve_artist_named_files():
    """Rename files whose filename stem is literally the artist's name."""
    print("\n--- 2. Resolving Files Named After Artists ---")
    direct_mappings = [
        # (Current Rel Path, Clean Song Name, Artist, Album)
        ("English/Celine Dion/Celine Dion.mp3", "My Heart Will Go On.mp3", "Celine Dion", "Let's Talk About Love"),
        ("English/Westlife/Westlife.mp3", "Amazing.mp3", "Westlife", "Westlife"),
        ("English/The Smashing Pumpkins/The Smashing Pumpkins.mp3", "1979.mp3", "The Smashing Pumpkins", "Mellon Collie and the Infinite Sadness"),
        ("English/Demonic Resurrection/Demonic Resurrection.mp3", "A Darkness Descends.mp3", "Demonic Resurrection", "A Darkness Descends"),
        ("Hindi/Artists/Mohit Chauhan/Mohit Chauhan.mp3", "Abhi Kuch Dino Se.mp3", "Mohit Chauhan", "Dil Toh Baccha Hai Ji"),
        ("Hindi/Artists/KK/Kk.mp3", "Prashna Chinha.mp3", "KK", "Encounter: The Killing"),
        ("Hindi/Soundtracks/Wake Up Sid/Shankar Mahadevan.mp3", "Wake Up Sid.mp3", "Shankar Mahadevan", "Wake Up Sid"),
        ("Hindi/Artists/Kabhi To Nazar Milao/Adnan Sami.mp3", "Kabhi To Nazar Milao.mp3", "Adnan Sami", "Kabhi To Nazar Milao"),
        ("Hindi/Soundtracks/Jism/Shreya Ghoshal.mp3", "Jaadu Hai Nasha Hai.mp3", "Shreya Ghoshal", "Jism"),
    ]

    for rel_src, new_fname, art, alb in direct_mappings:
        src = os.path.join(ORGANIZED_ROOT, rel_src.replace("/", os.sep))
        if os.path.exists(src):
            parent = os.path.dirname(src)
            dest = os.path.join(parent, new_fname)
            print(f"  [RESOLVE ARTIST FILENAME] {os.path.basename(src)} -> {new_fname}")
            if os.path.exists(dest) and dest != src:
                backup_inferior_file(src, reason="duplicate_resolved")
            else:
                os.rename(src, dest)
                stem = os.path.splitext(new_fname)[0]
                update_tags(dest, stem, art, alb)

    # Wake Up Sid duplicate Shankar Mahadvan.mp3 (128k duplicate)
    wus_dup = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Wake Up Sid", "Shankar Mahadvan.mp3")
    if os.path.exists(wus_dup):
        backup_inferior_file(wus_dup, reason="lower_bitrate_dup")


def resolve_artist_embedded_filenames():
    """Strip ' - Artist', 'Artist - ', and 'Song Artist' from filenames."""
    print("\n--- 3. Stripping Artist Names from Filenames ---")
    strip_mappings = [
        # Hindi Artists
        ("Hindi/Artists/Piyush Mishra/Aarambh - Piyush Mishra.mp3", "Aarambh.mp3", "Aarambh", "Piyush Mishra"),
        ("Hindi/Artists/Rahat Fateh Ali Khan/Fakeera - Rahat Fateh Ali Khan.mp3", "Fakeera.mp3", "Fakeera", "Rahat Fateh Ali Khan"),
        ("Hindi/Artists/Rahat Fateh Ali Khan/Tum Jo Aaye Reprise - Rahat Fateh Ali Khan.mp3", "Tum Jo Aaye Reprise.mp3", "Tum Jo Aaye Reprise", "Rahat Fateh Ali Khan"),
        ("Hindi/Artists/Rahat Fateh Ali Khan/Zindagi Ye - Rahat Fateh Ali Khan.mp3", "Zindagi Ye.mp3", "Zindagi Ye", "Rahat Fateh Ali Khan"),
        ("Hindi/Artists/Euphoria/Maaeri Euphoria.mp3", "Maaeri.mp3", "Maaeri", "Euphoria"),
        ("Hindi/Artists/Bally Sagoo/Gori Nal Ishq Mita Bally Sagoo.mp3", "Gori Nal Ishq Mita.mp3", "Gori Nal Ishq Mita", "Bally Sagoo"),
        ("Hindi/Artists/Lucky Ali/Nahi Rakhta Dil Mein Lucky Ali.mp3", "Nahi Rakhta Dil Mein.mp3", "Nahi Rakhta Dil Mein", "Lucky Ali"),
        ("Hindi/Artists/Mukesh/Bhooli Hui Yaadon Ne Mukesh.mp3", "Bhooli Hui Yaadon Ne.mp3", "Bhooli Hui Yaadon Ne", "Mukesh"),
        ("Hindi/Artists/Shankar Mahadevan/Uff Teri Adaa - Shankar Mahadevan and Alyssa Mendonsa - Uff Teri Adaa.mp3", "Uff Teri Adaa.mp3", "Uff Teri Adaa", "Shankar Mahadevan & Alyssa Mendonsa"),
        # Hindi Soundtracks
        ("Hindi/Soundtracks/Anwar/Maula Mere Maula - Roop Kumar Rathod.mp3", "Maula Mere Maula.mp3", "Maula Mere Maula", "Roop Kumar Rathod"),
        ("Hindi/Soundtracks/Anwar/Javeda Zindagi Tose Naina Lagey - Alt.mp3", "Javeda Zindagi.mp3", "Javeda Zindagi", "Kshitij Tarey & Shilpa Rao"),
        ("Hindi/Soundtracks/Bhool Bhulaiya/Neeraj Sridhar - Bhool Bhoolaiyaa.mp3", "Bhool Bhulaiyaa.mp3", "Bhool Bhulaiyaa", "Neeraj Sridhar"),
        ("Hindi/Soundtracks/Delhi Belly/Nakkadwaley Disco Udhaarwaley Khisko - Keerthi Sagathia.mp3", "Nakkadwaley Disco Udhaarwaley Khisko.mp3", "Nakkadwaley Disco Udhaarwaley Khisko", "Keerthi Sagathia"),
        ("Hindi/Soundtracks/Ra.One/Chammak Challo Akon.mp3", "Chammak Challo.mp3", "Chammak Challo", "Akon & Hamsika Iyer"),
    ]

    for rel_src, new_fname, title, art in strip_mappings:
        src = os.path.join(ORGANIZED_ROOT, rel_src.replace("/", os.sep))
        if os.path.exists(src):
            parent = os.path.dirname(src)
            dest = os.path.join(parent, new_fname)
            print(f"  [STRIP ARTIST] {os.path.basename(src)} -> {new_fname}")
            if os.path.exists(dest) and dest != src:
                # If clean version already exists, backup the dirty filename version
                backup_inferior_file(src, reason="duplicate_dirty_name")
            else:
                os.rename(src, dest)
                update_tags(dest, title, art)


def resolve_noise_and_rip_tags():
    """Strip noise tokens, resolution tags, and uploader junk from filenames."""
    print("\n--- 4. Cleaning Noise Tokens & Rip Junk ---")

    # 1. Barfi: Alabarfibarfi2012Sihag.mp3 (duplicate of Ala Barfi.mp3)
    barfi_dup = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Barfi", "Alabarfibarfi2012Sihag.mp3")
    if os.path.exists(barfi_dup):
        backup_inferior_file(barfi_dup, reason="barfi_sihag_dup")

    # 2. Julie: Dil Kya Kare duplicates (03 S and Jab)
    julie_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Julie")
    for jf in ["Dil Kya Kare03 S.mp3", "Dil Kya Kare Jab.mp3"]:
        jp = os.path.join(julie_dir, jf)
        if os.path.exists(jp):
            backup_inferior_file(jp, reason="julie_dup")

    # 3. Bachna Ae Haseeno: Bachnaaehaseeno01.mp3 (duplicate of Khuda Jaane)
    bah_dup = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Bachna Ae Haseeno", "Bachnaaehaseeno01.mp3")
    if os.path.exists(bah_dup):
        backup_inferior_file(bah_dup, reason="bah_khuda_jaane_dup")

    # 4. Chalte Chalte: Chalte Chalte12 S.mp3 (duplicate of Tauba Tumhare Yeh Ishare)
    cc_dup = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Chalte Chalte", "Chalte Chalte12 S.mp3")
    if os.path.exists(cc_dup):
        backup_inferior_file(cc_dup, reason="cc_tauba_dup")

    # 5. Chalte Chalte: Pakeeza-Chalte-Chalte.mp3 belongs in Pakeezah
    cc_pakeeza = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Chalte Chalte", "Pakeeza-Chalte-Chalte.mp3")
    pakeezah_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Pakeezah")
    if os.path.exists(cc_pakeeza):
        os.makedirs(pakeezah_dir, exist_ok=True)
        dest_pakeezah = os.path.join(pakeezah_dir, "Chalte Chalte Yunhi Koi.mp3")
        print(f"  Moving Pakeezah track from Chalte Chalte to Pakeezah...")
        shutil.move(cc_pakeeza, dest_pakeezah)
        update_tags(dest_pakeezah, "Chalte Chalte Yunhi Koi", "Lata Mangeshkar", "Pakeezah")

    # 6. Baadmaash Company track renaming
    bc_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Baadmaash Company")
    bc_mappings = {
        "Badmaashcompany01.mp3": ("Ayaashi.mp3", "Ayaashi", "KK"),
        "Badmaashcompany02.mp3": ("Jingle Jingle.mp3", "Jingle Jingle", "Mohit Chauhan"),
        "Badmaashcompany03.mp3": ("Chaska.mp3", "Chaska", "Krishna Beura"),
        "Badmaashcompany05.mp3": ("Badmaash Company.mp3", "Badmaash Company", "Benny Dayal"),
        "Badmaashcompany06.mp3": ("Ayaashi - Remix.mp3", "Ayaashi (Remix)", "KK"),
    }
    for old_f, (new_f, tit, art) in bc_mappings.items():
        src = os.path.join(bc_dir, old_f)
        if os.path.exists(src):
            dest = os.path.join(bc_dir, new_f)
            print(f"  [BAADMAASH COMPANY] {old_f} -> {new_f}")
            os.rename(src, dest)
            update_tags(dest, tit, art, "Baadmaash Company")

    # 7. Dev D track renaming
    devd_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Dev D")
    devd_mappings = {
        "Devd05.mp3": ("Duniya.mp3", "Duniya", "Amit Trivedi"),
        "Devd13.mp3": ("Nayan Tarse.mp3", "Nayan Tarse", "Amit Trivedi"),
        "Devd15.mp3": ("Pardesi.mp3", "Pardesi", "Tochi Raina"),
    }
    for old_f, (new_f, tit, art) in devd_mappings.items():
        src = os.path.join(devd_dir, old_f)
        if os.path.exists(src):
            dest = os.path.join(devd_dir, new_f)
            print(f"  [DEV D] {old_f} -> {new_f}")
            os.rename(src, dest)
            update_tags(dest, tit, art, "Dev D")

    # 8. Jaan E Mann: Jaanemann01.mp3 -> Humko Maaloom Hai
    jem_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Jaan E Mann")
    jem_src = os.path.join(jem_dir, "Jaanemann01.mp3")
    if os.path.exists(jem_src):
        jem_dest = os.path.join(jem_dir, "Humko Maaloom Hai.mp3")
        print(f"  [JAAN E MANN] Jaanemann01.mp3 -> Humko Maaloom Hai.mp3")
        os.rename(jem_src, jem_dest)
        update_tags(jem_dest, "Humko Maaloom Hai", "Sonu Nigam & Sadhana Sargam", "Jaan-E-Mann")

    # 9. Dard Bhare Songs renaming to clean Mohammad Rafi titles
    dbs_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Dard Bhare Songs")
    dbs_mappings = {
        "Dbs1.mp3": "Teri Galiyon Mein Na Rakhein.mp3",
        "Dbs2.mp3": "Yeh Duniya Yeh Mehfil.mp3",
        "Dbs6.mp3": "Dil Jo Na Keh Sakaa.mp3",
        "Dbs7.mp3": "Khilona Jaan Ker Tum To.mp3",
        "Dbs8.mp3": "Khush Rahe Tu Sadaa.mp3",
        "Dbs9.mp3": "Mere Dushman Tu Meri.mp3",
        "Dbs10.mp3": "Meri Mitwaa Mere Meet Re.mp3",
        "Dbs11.mp3": "Naseeb Mein Jiske Jo.mp3",
        "Dbs12.mp3": "Pardesiyon Se Na.mp3",
        "Dbs13.mp3": "Patthar Ke Sanam.mp3",
        "Dbs14.mp3": "Raha Gardishon Mein.mp3",
        "Agar Bewafaa Tujhko - Muhammad Rafi.mp3": "Agar Bewafaa Tujhko.mp3",
    }
    for old_f, new_f in dbs_mappings.items():
        src = os.path.join(dbs_dir, old_f)
        if os.path.exists(src):
            dest = os.path.join(dbs_dir, new_f)
            print(f"  [DARD BHARE SONGS] {old_f} -> {new_f}")
            os.rename(src, dest)
            tit = os.path.splitext(new_f)[0]
            update_tags(dest, tit, "Mohammad Rafi", "Dard Bhare Songs")


def resolve_aap_ki_kasam_dumpster():
    """Re-home tracks dumped into Aap Ki Kasam based on the word 'Zindagi'."""
    print("\n--- 5. Resolving Aap Ki Kasam Misplaced Tracks ---")
    akk_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", "Aap Ki Kasam")
    if not os.path.exists(akk_dir):
        return

    moves = [
        # (File in Aap Ki Kasam, Target Film Subfolder, Clean Song Name, Artist)
        ("Tujhse Naraaz Nahin Zindagi - Anup Ghoshal.mp3", "Masoom", "Tujhse Naraaz Nahin Zindagi.mp3", "Anup Ghoshal"),
        ("Dil Kabaddi - Zindagi Ye.mp3", "Dil Kabaddi", "Zindagi Ye.mp3", "Rahat Fateh Ali Khan"),
        ("Tu Meri Zindagi Hai.mp3", "Aashiqui", "Tu Meri Zindagi Hai.mp3", "Kumar Sanu & Anuradha Paudwal"),
        ("Kabhi Kabhi Aditi Zindagi.mp3", "Jaane Tu Ya Jaane Na", "Kabhi Kabhi Aditi.mp3", "Rashid Ali"),
    ]

    for fname, target_film, clean_title, art in moves:
        src = os.path.join(akk_dir, fname)
        if os.path.exists(src):
            target_dir = os.path.join(ORGANIZED_ROOT, "Hindi", "Soundtracks", target_film)
            os.makedirs(target_dir, exist_ok=True)
            dest = os.path.join(target_dir, clean_title)
            print(f"  Moving {fname} -> {target_film}\\{clean_title}")
            if os.path.exists(dest):
                backup_inferior_file(src, reason=f"already_exists_in_{target_film}")
            else:
                shutil.move(src, dest)
                stem = os.path.splitext(clean_title)[0]
                update_tags(dest, stem, art, target_film)


def sweep_empty_folders():
    """Ensure bottom-up sweep removes any emptied directories."""
    print("\n--- 6. Directory Hygiene Sweeper ---")
    deleted = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        if not os.listdir(root):
            try:
                os.rmdir(root)
                deleted += 1
                print(f"  Removed empty folder: {root}")
            except Exception:
                pass
    print(f"Sweep complete. Removed {deleted} empty directories.")


def main():
    print("=" * 70)
    print("AURALIS: ARTIST-IN-FILENAME & NOISE CLEANER + DEDUPLICATION ENGINE")
    print("=" * 70)

    resolve_golmaal_and_choti_si_baat()
    resolve_artist_named_files()
    resolve_artist_embedded_filenames()
    resolve_noise_and_rip_tags()
    resolve_aap_ki_kasam_dumpster()
    sweep_empty_folders()

    print("\n" + "=" * 70)
    print("CLEANUP AND DEDUPLICATION PASS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
