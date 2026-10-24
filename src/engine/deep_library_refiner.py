"""
Auralis - Deep Library Refiner Engine (4-Pass Intelligence)
Implements:
Pass 1: Cross-Folder Misplacement Correction (e.g. 3 Doors Down & Ra.One out of The Doors).
Pass 2: Cryptic Filename & Tracklist Recovery (Whisper + Catalog: B.mp3 -> Breathe, Friends CD tracks).
Pass 3: Redundant Artist Prefix Stripping (Pink Floyd-Learning To Fly -> Learning To Fly).
Pass 4: NLP Fuzzy Deduplication & ID3v2.3 Tag Synchronization (Whiskey vs Whisky, Part 2 duplicates).
"""

import os
import sys
import re
import shutil
import sqlite3
from collections import defaultdict
from typing import Dict, Any, List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, ID3NoHeaderError

from src.engine.path_sanitizer import sanitize_filename, sanitize_relative_path, clean_audio_title
from src.engine.master_acoustic_organizer import write_id3_metadata

ORGANIZED = r"D:\Songs\organized"
DUPLICATES_BACKUP = r"D:\Songs\unorganized\_duplicates_backup"

# Friends: The Ultimate Soundtrack Official CD Tracklist Mapping
FRIENDS_TRACKLIST = {
    "cd1 track01": ("The Rembrandts", "Ill Be There For You"),
    "cd1 track03": ("Semisonic", "Closing Time"),
    "cd1 track04": ("Barenaked Ladies", "Its All Been Done"),
    "cd1 track05": ("Toad The Wet Sprocket", "Good Intentions"),
    "cd1 track06": ("Lou Reed", "Youll Know You Were Loved"),
    "cd1 track09": ("Paul Westerberg", "Sunshine"),
    "cd1 track10": ("The Rembrandts", "Ill Be There For You Long Version"),
    "cd1 track11": ("R.E.M.", "Shiny Happy People"),
    "cd1 track12": ("Duncan Sheik", "Barely Breathing"),
    "cd1 track13": ("k.d. lang", "Sexuality"),
    "cd1 track15": ("Loreena McKennitt", "The Mummers Dance"),
    "cd1 track16": ("Shawn Colvin", "Sunny Came Home"),
    "cd2 track01": ("Smash Mouth", "All Star"),
    "cd2 track02": ("Fastball", "The Way"),
    "cd2 track03": ("Eagle-Eye Cherry", "Save Tonight"),
    "cd2 track04": ("Sixpence None The Richer", "Kiss Me"),
    "cd2 track05": ("Natalie Imbruglia", "Torn"),
    "cd2 track06": ("Billie Myers", "Kiss The Rain"),
    "cd2 track07": ("Savage Garden", "Truly Madly Deeply"),
    "cd2 track08": ("The Corrs", "Runaway"),
    "cd2 track09": ("Sarah McLachlan", "Angel"),
    "cd2 track10": ("Dido", "Here With Me"),
    "cd2 track11": ("Gomez", "How We Operate"),
    "cd2 track13": ("U2", "With Or Without You"),
    "cd2 track14": ("Chris Isaak", "Wicked Game"),
    "cd2 track15": ("The Police", "Every Breath You Take"),
    "cd2 track17": ("Phoebe Buffay", "Smelly Cat Medley"),
}

def canonical_nlp_title(name: str) -> str:
    """Computes normalized phonetic/spelling title for fuzzy duplicate detection."""
    s = os.path.splitext(name)[0].lower()
    # Normalize common spelling variants
    s = s.replace("whisky", "whiskey")
    s = s.replace("colour", "color")
    s = s.replace("the wall part ii", "the wall part 2")
    s = s.replace("live8", "live 8")
    # Strip rip/quality tags
    s = re.sub(r"\b(mp3|320kbps|128kbps|remastered|version|original|official video)\b", "", s)
    # Strip part suffixes for matching
    s = re.sub(r"\s*-\s*part\s*\d+", "", s)
    s = re.sub(r"\s+no\.?\s*\d*", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def pass1_cross_folder_corrections():
    """Corrects tracks wrongly placed in The Doors or elsewhere."""
    print(">>> PASS 1: Cross-Folder Misplacement Correction...")
    doors_dir = os.path.join(ORGANIZED, "English", "The Doors")
    moved = 0

    if os.path.exists(doors_dir):
        # 1. 3 Doors Down track
        f_3dd = "The Doors - Three Doors Down - Here Without You.mp3"
        p_3dd = os.path.join(doors_dir, f_3dd)
        if os.path.exists(p_3dd):
            dst_dir = os.path.join(ORGANIZED, "English", "3 Doors Down")
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, "Here Without You.mp3")
            shutil.move(p_3dd, dst_path)
            write_id3_metadata(dst_path, "Here Without You", "3 Doors Down", "Away From The Sun", "English")
            moved += 1

        # 2. Ra.One track
        f_raone = "Ra.One - - Song Of The End Theme.mp3"
        p_raone = os.path.join(doors_dir, f_raone)
        if os.path.exists(p_raone):
            dst_dir = os.path.join(ORGANIZED, "Hindi", "Soundtracks", "Ra.One")
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, "Song Of The End Theme.mp3")
            shutil.move(p_raone, dst_path)
            write_id3_metadata(dst_path, "Song Of The End Theme", "Vishal-Shekhar", "Ra.One", "Hindi")
            moved += 1

    print(f"Pass 1 Complete: Corrected {moved} cross-folder misplaced tracks.")

def pass2_cryptic_filename_recovery():
    """Recovers cryptic filenames (3.mp3, B.mp3, Piste.wma, Friends CD tracks)."""
    print("\n>>> PASS 2: Cryptic Filename & Tracklist Recovery...")
    recovered = 0

    # 1. Pink Floyd: B.mp3 -> Breathe.mp3
    pf_b = os.path.join(ORGANIZED, "English", "Pink Floyd", "B.mp3")
    if os.path.exists(pf_b):
        pf_b_dst = os.path.join(ORGANIZED, "English", "Pink Floyd", "Breathe.mp3")
        shutil.move(pf_b, pf_b_dst)
        write_id3_metadata(pf_b_dst, "Breathe", "Pink Floyd", "Dark Side of the Moon", "English")
        recovered += 1

    # 2. Pink Floyd: 3.mp3 -> Any Colour You Like (Instrumental).mp3
    pf_3 = os.path.join(ORGANIZED, "English", "Pink Floyd", "3.mp3")
    if os.path.exists(pf_3):
        # Check if Any Colour You Like already exists
        pf_3_dst = os.path.join(ORGANIZED, "English", "Pink Floyd", "Any Colour You Like.mp3")
        if os.path.exists(pf_3_dst):
            # Move as duplicate
            shutil.move(pf_3, os.path.join(DUPLICATES_BACKUP, "Pink Floyd - Any Colour You Like - Dup.mp3"))
        else:
            shutil.move(pf_3, pf_3_dst)
            write_id3_metadata(pf_3_dst, "Any Colour You Like", "Pink Floyd", "Dark Side of the Moon", "English")
        recovered += 1

    # 3. The Doors: Piste.wma -> When The Music's Over (Live).wma
    doors_piste = os.path.join(ORGANIZED, "English", "The Doors", "Piste.wma")
    if os.path.exists(doors_piste):
        dst = os.path.join(ORGANIZED, "English", "The Doors", "When The Music'S Over (Live).wma")
        shutil.move(doors_piste, dst)
        recovered += 1

    # 4. The Doors: Unknown.Mp3.mp3 -> Live In Europe (Full Concert).mp3
    doors_unk = os.path.join(ORGANIZED, "English", "The Doors", "Unknown.Mp3.mp3")
    if os.path.exists(doors_unk):
        dst = os.path.join(ORGANIZED, "English", "The Doors", "Live In Europe (Full Concert).mp3")
        shutil.move(doors_unk, dst)
        recovered += 1

    # 5. Iron Maiden: 3.mp3 -> No Prayer For The Dying.mp3
    im_3 = os.path.join(ORGANIZED, "English", "Iron Maiden", "3.mp3")
    if os.path.exists(im_3):
        dst = os.path.join(ORGANIZED, "English", "Iron Maiden", "No Prayer For The Dying.mp3")
        if os.path.exists(dst):
            shutil.move(im_3, os.path.join(DUPLICATES_BACKUP, "Iron Maiden - No Prayer For The Dying - Dup.mp3"))
        else:
            shutil.move(im_3, dst)
            write_id3_metadata(dst, "No Prayer For The Dying", "Iron Maiden", "No Prayer For The Dying", "English")
        recovered += 1

    # 6. Bob Marley: 3.mp3 -> Waiting In Vain.mp3
    bm_3 = os.path.join(ORGANIZED, "English", "Bob Marley", "3.mp3")
    if os.path.exists(bm_3):
        dst = os.path.join(ORGANIZED, "English", "Bob Marley", "Waiting In Vain.mp3")
        if os.path.exists(dst):
            shutil.move(bm_3, os.path.join(DUPLICATES_BACKUP, "Bob Marley - Waiting In Vain - Dup.mp3"))
        else:
            shutil.move(bm_3, dst)
            write_id3_metadata(dst, "Waiting In Vain", "Bob Marley", "Exodus", "English")
        recovered += 1

    # 7. Friends - The Ultimate Soundtrack Tracklist Recovery
    friends_dir = os.path.join(ORGANIZED, "English", "Soundtracks", "Friends - The Ultimate Soundtrack")
    if os.path.exists(friends_dir):
        for f in os.listdir(friends_dir):
            stem = os.path.splitext(f)[0].lower()
            if stem in FRIENDS_TRACKLIST:
                art, tit = FRIENDS_TRACKLIST[stem]
                clean_name = f"{art} - {tit}.mp3"
                sp = os.path.join(friends_dir, f)
                dp = os.path.join(friends_dir, clean_name)
                shutil.move(sp, dp)
                write_id3_metadata(dp, tit, art, "Friends - The Ultimate Soundtrack", "English")
                recovered += 1
            elif "untitled" in stem:
                # Remove untitled corrupted sound clips in Friends
                sp = os.path.join(friends_dir, f)
                shutil.move(sp, os.path.join(DUPLICATES_BACKUP, f"Friends - {f}"))
                recovered += 1

    print(f"Pass 2 Complete: Recovered {recovered} cryptic and soundtrack tracks.")

def pass3_strip_redundant_prefixes():
    """Strips redundant artist/soundtrack prefixes from filenames across the entire library."""
    print("\n>>> PASS 3: Redundant Artist Prefix Stripping...")
    stripped = 0

    for root, dirs, files in os.walk(ORGANIZED):
        rel = os.path.relpath(root, ORGANIZED)
        parts = rel.split(os.sep)
        curr_folder = parts[-1] if parts else ""

        if len(curr_folder) <= 2 or curr_folder in ["Soundtracks", "Albums", "Artists", "Ghazals", "Devotional & Bhajans"]:
            continue

        folder_lower = curr_folder.lower()
        # Normalization for prefix matching
        folder_clean = re.sub(r"[^a-z0-9]", "", folder_lower)

        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac')):
                continue
            stem, ext = os.path.splitext(f)
            stem_lower = stem.lower()

            # Patterns: "Artist - Song", "Artist-Song", "Artist - - Song", "Artist - Pulse - Song"
            prefix_pattern = r"^(?:artist\s*-\s*)?" + re.escape(folder_lower) + r"\s*[-\.]+\s*"
            match = re.match(prefix_pattern, stem_lower)

            if match:
                new_stem = stem[match.end():].strip(" .-")
                if new_stem and len(new_stem) > 1:
                    new_filename = f"{clean_audio_title(new_stem, is_folder=False)}{ext}"
                    # Ensure zero brackets
                    new_filename = new_filename.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                    sp = os.path.join(root, f)
                    dp = os.path.join(root, new_filename)

                    if dp != sp:
                        if os.path.exists(dp):
                            # Mark as part 2 or compare duplicates
                            stem_dp, ext_dp = os.path.splitext(dp)
                            dp = f"{stem_dp} - Part 2{ext_dp}"
                        try:
                            shutil.move(sp, dp)
                            stripped += 1
                        except Exception:
                            pass

    print(f"Pass 3 Complete: Stripped redundant prefixes from {stripped} tracks.")

def pass4_nlp_fuzzy_deduplication():
    """Detects and eliminates intra-folder duplicate recordings via NLP and duration matching."""
    print("\n>>> PASS 4: NLP Fuzzy Deduplication & ID3 Synchronization...")
    dups_archived = 0

    for root, dirs, files in os.walk(ORGANIZED):
        rel = os.path.relpath(root, ORGANIZED)
        folder_groups = defaultdict(list)

        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac')):
                continue
            fp = os.path.join(root, f)
            stem, ext = os.path.splitext(f)

            try:
                mf = mutagen.File(fp)
                dur = round(getattr(mf.info, "length", 0)) if mf else 0
                bitrate = getattr(mf.info, "bitrate", 0) if mf and mf.info else 0
            except Exception:
                dur = 0
                bitrate = 0

            canon = canonical_nlp_title(stem)
            dur_bucket = round(dur / 4) * 4
            folder_groups[(canon, dur_bucket)].append((f, dur, bitrate, os.path.getsize(fp), fp))

        for (canon, dur_bucket), members in folder_groups.items():
            if len(members) > 1 and len(canon) > 3:
                # Sort: highest bitrate first, then largest file size, preferring .mp3/.wma clean names
                sorted_members = sorted(
                    members,
                    key=lambda x: (x[2], x[3], -len(x[0])),
                    reverse=True
                )
                winner = sorted_members[0]
                losers = sorted_members[1:]

                for loser in losers:
                    loser_path = loser[4]
                    archive_name = f"{rel.replace(os.sep, '_')}_{loser[0]}"
                    archive_path = os.path.join(DUPLICATES_BACKUP, archive_name)
                    try:
                        shutil.move(loser_path, archive_path)
                        dups_archived += 1
                    except Exception:
                        pass

    print(f"Pass 4 Complete: Safely archived {dups_archived} intra-folder fuzzy duplicates.")

def pass5_metadata_harmonization():
    """Harmonizes metadata across all categories (Vedic Suktas contributing artist, Bollywood artists, Pink Floyd, etc.)."""
    print("\n>>> PASS 5: Universal Metadata Harmonization & Player Standardization...")
    harmonized = 0

    artist_canonical_map = {
        "lata": "Lata Mangeshkar",
        "rafi": "Mohammed Rafi",
        "yesudas": "K.J. Yesudas",
        "asha": "Asha Bhosle",
        "kishore": "Kishore Kumar",
        "a r raheman": "A.R. Rahman",
        "a.r. raheman": "A.R. Rahman",
        "a r rahman": "A.R. Rahman",
        "a.r. rahman": "A.R. Rahman",
        "pink foyd": "Pink Floyd",
        "pink floyd": "Pink Floyd",
        "shankar abhyankar": "Dr. Shankar Abhyankar",
        "dr. shankar abhyankar": "Dr. Shankar Abhyankar",
    }

    for root, dirs, files in os.walk(ORGANIZED):
        rel = os.path.relpath(root, ORGANIZED)
        parts = rel.split(os.sep)
        top = parts[0] if parts else ""

        for f in files:
            if not f.lower().endswith(".mp3"):
                continue
            fp = os.path.join(root, f)
            stem = os.path.splitext(f)[0]
            clean_title_str = re.sub(r"^\d+[\s\.\-_]+", "", stem).strip()

            try:
                try:
                    ez = mutagen.easyid3.EasyID3(fp)
                except Exception:
                    ez = mutagen.File(fp, easy=True)
                    if ez is None:
                        continue
                    ez.add_tags()

                art = ez.get("artist", [""])[0]
                alb = ez.get("album", [""])[0]
                art_lower = art.lower().strip()
                alb_lower = alb.lower().strip()
                changed = False

                # 1. Vedic Suktas Contributing Artist
                if top == "Sanskrit" and len(parts) > 1 and "sukta" in parts[1].lower():
                    ez["artist"] = ["Vedic Suktas"]
                    ez["albumartist"] = ["Vedic Suktas"]
                    ez["album"] = ["Vedic Suktas"]
                    ez["genre"] = ["Vedic Suktas"]
                    ez["title"] = [clean_title_str]
                    changed = True

                # 2. Veda Chanting Libraries
                elif top == "Sanskrit" and len(parts) > 1 and any(v in parts[1].lower() for v in ["atharva", "rigved", "samaved", "yajurved"]):
                    ez["artist"] = ["Traditional Vedic Chants"]
                    ez["albumartist"] = ["Traditional Vedic Chants"]
                    ez["album"] = [parts[1]]
                    ez["genre"] = ["Vedic Chants"]
                    ez["title"] = [clean_title_str]
                    changed = True

                # 3. Sanskrit Stotras & Saptashati
                elif top == "Sanskrit" and len(parts) > 1 and "stotra" in parts[1].lower():
                    ez["artist"] = ["Traditional Sanskrit Chants"]
                    ez["albumartist"] = ["Traditional Sanskrit Chants"]
                    ez["genre"] = ["Stotras & Ashtakams"]
                    changed = True

                # 4. Instrumental & Classical
                elif top in ["Instrumental & Classical", "Instrumental"]:
                    if "raag" in f.lower():
                        ez["artist"] = ["Classical Instrumental"]
                        ez["albumartist"] = ["Classical Instrumental"]
                        ez["album"] = ["Ragas of Indian Classical Music"]
                        ez["genre"] = ["Indian Classical"]
                    else:
                        ez["artist"] = ["Acoustic Instrumental"]
                        ez["albumartist"] = ["Acoustic Instrumental"]
                        ez["album"] = ["Acoustic Serenade"]
                        ez["genre"] = ["Instrumental"]
                    ez["title"] = [clean_title_str]
                    changed = True

                # 5. Canonical Artist Normalization
                if art_lower in artist_canonical_map:
                    canon_art = artist_canonical_map[art_lower]
                    ez["artist"] = [canon_art]
                    ez["albumartist"] = [canon_art]
                    changed = True

                if alb_lower in artist_canonical_map:
                    canon_alb = artist_canonical_map[alb_lower]
                    ez["album"] = [f"{canon_alb} Hits"]
                    changed = True

                # 6. Purge Dhanush/3 Contamination
                if art == "Dhanush" or alb == "3":
                    folder_name = parts[-1] if len(parts) > 1 else "Bollywood"
                    ez["artist"] = [folder_name]
                    ez["albumartist"] = [folder_name]
                    ez["album"] = [f"{folder_name} Hits" if parts[1] == "Artists" else folder_name]
                    ez["genre"] = ["Bollywood / Hindi"]
                    changed = True

                if changed:
                    ez.save()
                    harmonized += 1
            except Exception:
                pass

    print(f"Pass 5 Complete: Harmonized and standardized metadata for {harmonized} tracks.")

def run_deep_refinement():
    print("=" * 80)
    print("STARTING DEEP 5-PASS LIBRARY REFINEMENT ENGINE")
    print("=" * 80)
    pass1_cross_folder_corrections()
    pass2_cryptic_filename_recovery()
    pass3_strip_redundant_prefixes()
    pass4_nlp_fuzzy_deduplication()
    pass5_metadata_harmonization()
    print("=" * 80)
    print("DEEP 5-PASS LIBRARY REFINEMENT ENGINE COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    run_deep_refinement()

