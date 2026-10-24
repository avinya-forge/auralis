"""
Auralis - Precision Library Polisher & Typography Harmonizer
Implements comprehensive perfection polishing across D:\\Songs\\organized:
1. Re-homes 26 misplaced Marathi masterpieces from Hindi\\Artists\\Lata Mangeshkar to Marathi\\Lata Mangeshkar.
2. Re-homes misfiled English/Hindi tracks (Megadeth -> Ek Deewana Tha, The Beatles\\Lobo -> Assorted Pop & Rock).
3. Eliminates all redundant movie prefixes in Hindi Soundtracks (Dum Maaro Dum, Ek Deewana Tha, Choti Si Baat, Jism 2, etc.).
4. Eliminates redundant artist/band prefixes (The Beatles, Bob Marley, Linkin Park, Demonic Resurrection).
5. Fixes bad apostrophe casing across filenames and ID3/ASF tags (Can'T -> Can't, It'S -> It's, Dylan'S -> Dylan's).
6. Fixes bad ordinal casing across filenames and ID3/ASF tags (115Th -> 115th, 21St -> 21st).
7. Strips artist and movie names from embedded title tags (Vishal Dadlani - Kurbaan Hua -> Kurbaan Hua).
8. Performs quality-aware deduplication on alternative masters (retaining 320kbps full tracks).
"""

import os
import sys
import re
import shutil
import difflib
from typing import Dict, Any, List, Tuple

import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TYER
from mutagen.mp3 import MP3
from mutagen.asf import ASF
from mutagen.mp4 import MP4

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_organizer import MasterOrganizer

ORGANIZED_ROOT = r"D:\Songs\organized"
BACKUP_DUPLICATES_ROOT = r"D:\Songs\unorganized\_duplicates_backup"

APOSTROPHE_MAP = {
    r"\b([A-Za-z]+)'T\b": r"\1't",
    r"\b([A-Za-z]+)'S\b": r"\1's",
    r"\b([A-Za-z]+)'M\b": r"\1'm",
    r"\b([A-Za-z]+)'D\b": r"\1'd",
    r"\b([A-Za-z]+)'Ll\b": r"\1'll",
    r"\b([A-Za-z]+)'Ve\b": r"\1've",
    r"\b([A-Za-z]+)'Re\b": r"\1're",
    r"\bRock\s*'N'\s*Roll\b": "Rock 'n' Roll",
    r"\bRock\s+N\s+Roll\b": "Rock 'n' Roll",
    r"\bGuns\s+N\s+Roses\b": "Guns N' Roses",
}

ORDINAL_MAP = {
    r"\b(\d+)(?:St)\b": r"\1st",
    r"\b(\d+)(?:Nd)\b": r"\1nd",
    r"\b(\d+)(?:Rd)\b": r"\1rd",
    r"\b(\d+)(?:Th)\b": r"\1th",
}

def clean_typography(text: str) -> str:
    """Corrects English apostrophe casing, ordinals, and spacing artifacts."""
    if not text:
        return ""
    res = text
    for pat, repl in APOSTROPHE_MAP.items():
        res = re.sub(pat, repl, res, flags=re.IGNORECASE if "Rock" in pat or "Guns" in pat else 0)
    for pat, repl in ORDINAL_MAP.items():
        res = re.sub(pat, repl, res)
    res = re.sub(r'\s+', ' ', res).strip()
    return res

class PrecisionPolisher:
    def __init__(self, organized_root: str = ORGANIZED_ROOT):
        self.organized_root = organized_root
        self.organizer = MasterOrganizer()

    def run_all_passes(self) -> Dict[str, int]:
        stats = {
            "rehomed_marathi": 0,
            "rehomed_cross_genre": 0,
            "movie_prefixes_cleaned": 0,
            "artist_prefixes_cleaned": 0,
            "typography_renamed": 0,
            "tags_updated": 0,
            "duplicates_archived": 0,
        }

        print("=" * 80)
        print("STARTING AURALIS PRECISION LIBRARY POLISHER")
        print("=" * 80)

        # 1. Re-home Lata Mangeshkar Marathi songs
        stats["rehomed_marathi"] += self._rehome_lata_marathi()

        # 2. Re-home misplaced tracks (Megadeth -> Ek Deewana Tha, Beatles -> Lobo)
        stats["rehomed_cross_genre"] += self._rehome_misplaced_tracks()

        # 3. Clean movie prefixes in Hindi Soundtracks
        stats["movie_prefixes_cleaned"] += self._clean_soundtrack_prefixes()

        # 4. Clean artist prefixes and deduplicate in The Beatles & Bob Marley
        stats["artist_prefixes_cleaned"] += self._clean_artist_prefixes()

        # 5. Fix title tags leaking artist/movie names
        stats["tags_updated"] += self._clean_leaked_title_tags()

        # 6. Global typography and casing polishing (filenames & embedded tags)
        typo_renamed, typo_tagged = self._polish_library_typography()
        stats["typography_renamed"] += typo_renamed
        stats["tags_updated"] += typo_tagged

        print("\n" + "=" * 80)
        print("PRECISION POLISHING COMPLETE - SUMMARY:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        print("=" * 80)

        return stats

    def _rehome_lata_marathi(self) -> int:
        print("\n>>> PASS 1: Re-homing Marathi Masterpieces to Marathi\\Lata Mangeshkar...")
        src_dir = os.path.join(self.organized_root, "Hindi", "Artists", "Lata Mangeshkar")
        dst_dir = os.path.join(self.organized_root, "Marathi", "Lata Mangeshkar")
        os.makedirs(dst_dir, exist_ok=True)

        marathi_files = [
            "Akhercha Ha Tula Dandavat.mp3", "Baai Baai Man Moracha.mp3", "Bai Mi Vikat Ghetala Shyam.mp3",
            "Chapha Bolena.mp3", "Datuni Kantha Yethi.mp3", "Erneechya Deva.m4a", "Ganga Jamuna Dolyat Ubhya Ka.mp3",
            "Ghanu Waje Ghuna Ghuna.mp3", "Hridayi Jaga Tu Anuraga.mp3", "Kashi Kaal Nagini Sakhe Ga.mp3",
            "Maalyachya Malyamadhi.mp3", "Madhu Ghatachi Rikame.mp3", "Malvuni Taak Deep.mp3", "Mawaltya Dinakara.mp3",
            "Mee Maj Harpun Basale Ga.mp3", "Mendichya Panawar.mp3", "Nabh Utaru Aala.mp3", "Nahi Kashi Mhanu Tula.mp3",
            "Navwadhu Priya Mee Bawarate.mp3", "Nilya Aabhali.mp3", "Pahuni Raghunandan Sawala.mp3",
            "Pratima Uri Dharuni.mp3", "Reshmachya Dhagyani.mp3", "Sawar Re Sawar Re.mp3",
            "Teenhi Sanja Sakhe Milalya.mp3", "Thakale Re Nandlala.mp3"
        ]

        count = 0
        for f in marathi_files:
            s = os.path.join(src_dir, f)
            d = os.path.join(dst_dir, f)
            if os.path.exists(s):
                shutil.move(s, d)
                # Update tags to reflect Marathi
                stem = os.path.splitext(f)[0]
                self.organizer.write_id3_tags(
                    file_path=d,
                    title=stem,
                    artist="Lata Mangeshkar",
                    album="Marathi Bhavgeete",
                    genre="Marathi"
                )
                count += 1
                print(f"  Moved: {f} -> Marathi\\Lata Mangeshkar")
        return count

    def _rehome_misplaced_tracks(self) -> int:
        print("\n>>> PASS 2: Re-homing Misplaced Cross-Genre Tracks...")
        count = 0

        # 1. Megadeth -> Ek Deewana Tha
        src1 = os.path.join(self.organized_root, "English", "Megadeth", "Ekk Deewana Tha - Broken Promises.mp3")
        dst1_dir = os.path.join(self.organized_root, "Hindi", "Soundtracks", "Ek Deewana Tha")
        dst1 = os.path.join(dst1_dir, "Broken Promises.mp3")
        if os.path.exists(src1):
            os.makedirs(dst1_dir, exist_ok=True)
            shutil.move(src1, dst1)
            self.organizer.write_id3_tags(
                file_path=dst1,
                title="Broken Promises",
                artist="A.R. Rahman",
                album="Ek Deewana Tha",
                genre="Soundtrack",
                year="2012"
            )
            count += 1
            print("  Moved: Megadeth\\Ekk Deewana Tha -> Hindi\\Soundtracks\\Ek Deewana Tha\\Broken Promises.mp3")

        # 2. The Beatles\Lobo -> English\Assorted Pop & Rock
        src2 = os.path.join(self.organized_root, "English", "The Beatles", "Lobo - Id Love You To Want Me.mp3")
        dst2_dir = os.path.join(self.organized_root, "English", "Assorted Pop & Rock")
        dst2 = os.path.join(dst2_dir, "I'd Love You To Want Me.mp3")
        if os.path.exists(src2):
            shutil.move(src2, dst2)
            self.organizer.write_id3_tags(
                file_path=dst2,
                title="I'd Love You to Want Me",
                artist="Lobo",
                album="Of a Simple Man",
                genre="Pop",
                year="1972"
            )
            count += 1
            print("  Moved: The Beatles\\Lobo -> English\\Assorted Pop & Rock\\I'd Love You To Want Me.mp3")

        return count

    def _clean_soundtrack_prefixes(self) -> int:
        print("\n>>> PASS 3: Cleaning Redundant Movie Prefixes from Soundtracks...")
        count = 0
        st_dir = os.path.join(self.organized_root, "Hindi", "Soundtracks")
        if not os.path.exists(st_dir):
            return 0

        for movie in os.listdir(st_dir):
            mp = os.path.join(st_dir, movie)
            if not os.path.isdir(mp):
                continue
            for f in os.listdir(mp):
                if not f.lower().endswith(('.mp3', '.wma', '.m4a')):
                    continue
                if " - " in f:
                    pfx, rest = f.split(" - ", 1)
                    ratio = difflib.SequenceMatcher(None, movie.lower(), pfx.lower()).ratio()
                    m_words = set(movie.lower().split())
                    p_words = set(pfx.lower().split())
                    if ratio >= 0.65 or (len(m_words & p_words) >= 1 and len(p_words) <= 3 and len(m_words) <= 3):
                        # Clean rest of filename
                        new_f = rest.strip()
                        # Avoid duplicates
                        src = os.path.join(mp, f)
                        dst = os.path.join(mp, new_f)
                        if src != dst and not os.path.exists(dst):
                            shutil.move(src, dst)
                            # Update ID3 title tag
                            clean_t = os.path.splitext(new_f)[0]
                            existing_artist = movie
                            try:
                                id3 = ID3(dst)
                                if id3.get("TPE1"):
                                    existing_artist = str(id3.get("TPE1"))
                            except Exception:
                                pass
                            self.organizer.write_id3_tags(
                                file_path=dst,
                                title=clean_t,
                                artist=existing_artist,
                                album=movie,
                                genre="Soundtrack"
                            )
                            count += 1
                            print(f"  [{movie}] Stripped prefix: {f} -> {new_f}")
        return count

    def _clean_artist_prefixes(self) -> int:
        print("\n>>> PASS 4: Cleaning Artist Prefixes & Quality-Aware Deduplication...")
        count = 0

        # 1. The Beatles
        beatles_dir = os.path.join(self.organized_root, "English", "The Beatles")
        if os.path.exists(beatles_dir):
            # Handle Rock and Roll Music: replace 99s truncated one with 152s complete 320kbps master
            trunc_p = os.path.join(beatles_dir, "Rock And Roll Music.mp3")
            full_p = os.path.join(beatles_dir, "Beatles Rock and Roll Music.mp3")
            if os.path.exists(trunc_p) and os.path.exists(full_p):
                backup_p = os.path.join(BACKUP_DUPLICATES_ROOT, "Rock And Roll Music (99s).mp3")
                os.makedirs(BACKUP_DUPLICATES_ROOT, exist_ok=True)
                shutil.move(trunc_p, backup_p)
                shutil.move(full_p, trunc_p)
                self.organizer.write_id3_tags(file_path=trunc_p, title="Rock and Roll Music", artist="The Beatles", album="Beatles for Sale", genre="Rock")
                count += 1
                print("  Replaced truncated Rock and Roll Music with full 320kbps master.")

            # Honey Don't
            honey_p = os.path.join(beatles_dir, "Beatles Honey Don'T.mp3")
            honey_dst = os.path.join(beatles_dir, "Honey Don't.mp3")
            if os.path.exists(honey_p):
                shutil.move(honey_p, honey_dst)
                self.organizer.write_id3_tags(file_path=honey_dst, title="Honey Don't", artist="The Beatles", album="Beatles for Sale", genre="Rock")
                count += 1
                print("  Renamed Beatles Honey Don'T -> Honey Don't.mp3")

            # Clean John Lennon & Paul McCartney solo prefixes in The Beatles
            for old_fn, new_fn, art in [
                ("John Lennon - Dream.mp3", "Dream.mp3", "John Lennon"),
                ("John Lennon - Imagine.mp3", "Imagine.mp3", "John Lennon"),
                ("Paul Mccartney - My Valentine.mp3", "My Valentine.mp3", "Paul McCartney")
            ]:
                s = os.path.join(beatles_dir, old_fn)
                d = os.path.join(beatles_dir, new_fn)
                if os.path.exists(s) and not os.path.exists(d):
                    shutil.move(s, d)
                    self.organizer.write_id3_tags(file_path=d, title=os.path.splitext(new_fn)[0], artist=art, album="The Beatles", genre="Rock")
                    count += 1
                    print(f"  Renamed: {old_fn} -> {new_fn}")

            # Archive redundant 'Beatles ' duplicates
            for b_fn in os.listdir(beatles_dir):
                if b_fn.startswith("Beatles "):
                    target_name = b_fn[len("Beatles "):].strip()
                    s = os.path.join(beatles_dir, b_fn)
                    d = os.path.join(beatles_dir, target_name)
                    if os.path.exists(d):
                        # Archive to duplicates backup
                        bk = os.path.join(BACKUP_DUPLICATES_ROOT, b_fn)
                        os.makedirs(BACKUP_DUPLICATES_ROOT, exist_ok=True)
                        shutil.move(s, bk)
                        count += 1
                        print(f"  Archived duplicate: {b_fn} -> _duplicates_backup")
                    else:
                        shutil.move(s, d)
                        count += 1
                        print(f"  Renamed: {b_fn} -> {target_name}")

        # 2. Bob Marley - Buffalo Soldier
        marley_dir = os.path.join(self.organized_root, "English", "Bob Marley")
        if os.path.exists(marley_dir):
            messy_bs = os.path.join(marley_dir, "Reggea - Bob Marley - Buffalo Soldier.mp3")
            clean_bs = os.path.join(marley_dir, "Buffalo Soldier.mp3")
            if os.path.exists(messy_bs) and os.path.exists(clean_bs):
                # Check bitrate: keep 320kbps
                m_messy = MP3(messy_bs)
                m_clean = MP3(clean_bs)
                if (m_messy.info.bitrate or 0) > (m_clean.info.bitrate or 0):
                    bk = os.path.join(BACKUP_DUPLICATES_ROOT, "Buffalo Soldier (256kbps).mp3")
                    os.makedirs(BACKUP_DUPLICATES_ROOT, exist_ok=True)
                    shutil.move(clean_bs, bk)
                    shutil.move(messy_bs, clean_bs)
                    self.organizer.write_id3_tags(file_path=clean_bs, title="Buffalo Soldier", artist="Bob Marley", album="Confrontation", genre="Reggae", year="1983")
                    count += 1
                    print("  Replaced 256kbps Buffalo Soldier with 320kbps master.")

        # 3. Assorted Pop & Rock\Blur - Song 2.mp3 -> Song 2.mp3
        blur_p = os.path.join(self.organized_root, "English", "Assorted Pop & Rock", "Blur - Song 2.mp3")
        blur_dst = os.path.join(self.organized_root, "English", "Assorted Pop & Rock", "Song 2.mp3")
        if os.path.exists(blur_p) and not os.path.exists(blur_dst):
            shutil.move(blur_p, blur_dst)
            self.organizer.write_id3_tags(file_path=blur_dst, title="Song 2", artist="Blur", album="Blur", genre="Rock", year="1997")
            count += 1
            print("  Renamed Blur - Song 2.mp3 -> Song 2.mp3")

        # 4. English\Soundtracks\Rocky - Gonna Fly Now.mp3 -> Gonna Fly Now.mp3
        rocky_p = os.path.join(self.organized_root, "English", "Soundtracks", "Rocky - Gonna Fly Now.mp3")
        rocky_dst = os.path.join(self.organized_root, "English", "Soundtracks", "Gonna Fly Now.mp3")
        if os.path.exists(rocky_p) and not os.path.exists(rocky_dst):
            shutil.move(rocky_p, rocky_dst)
            self.organizer.write_id3_tags(file_path=rocky_dst, title="Gonna Fly Now", artist="Bill Conti", album="Rocky", genre="Soundtrack", year="1976")
            count += 1
            print("  Renamed Rocky - Gonna Fly Now.mp3 -> Gonna Fly Now.mp3")

        # 5. Demonic Resurrection - Title Track.mp3
        dr_p = os.path.join(self.organized_root, "English", "Indian Rock Bands", "Demonic Resurrection", "Demonic Resurrection - Title Track.mp3")
        dr_dst = os.path.join(self.organized_root, "English", "Indian Rock Bands", "Demonic Resurrection", "Title Track.mp3")
        if os.path.exists(dr_p) and not os.path.exists(dr_dst):
            shutil.move(dr_p, dr_dst)
            self.organizer.write_id3_tags(file_path=dr_dst, title="Title Track", artist="Demonic Resurrection", album="Demonic Resurrection", genre="Rock")
            count += 1
            print("  Renamed Demonic Resurrection - Title Track.mp3 -> Title Track.mp3")

        return count

    def _clean_leaked_title_tags(self) -> int:
        print("\n>>> PASS 5: Cleaning Leaked Artist & Movie Names from Title Tags...")
        fixes = [
            (r"English\Linkin Park\Evanescence - Numb Linkin Park Cover.mp3", "Numb - Evanescence Cover", "Evanescence", "Linkin Park Covers", "Rock"),
            (r"Hindi\Soundtracks\Kurbaan\Vishal Dadlani - Kurbaan Hua.mp3", "Kurbaan Hua", "Vishal Dadlani", "Kurbaan", "Soundtrack"),
            (r"Hindi\Soundtracks\Rockford\Shankar Ehsaan Loy - Rockford-Aasmaanke.mp3", "Aasmaan Ke", "Shankar-Ehsaan-Loy", "Rockford", "Soundtrack"),
            (r"Hindi\Soundtracks\Wake Up Sid\Iktara - Male Version - By Tochi Raina- Wake Up Sid.mp3", "Iktara - Male Version", "Tochi Raina", "Wake Up Sid", "Soundtrack"),
            (r"Pravachan\Shankar Abhyankar\Bhagavad Gita - Nirupan\Mokshasanyasayoga\Mokshasanyasyog 02 - Shankar Abhyankar.mp3", "Mokshasanyasayoga 02", "Dr. Shankar Abhyankar", "Mokshasanyasayoga", "Pravachan")
        ]

        count = 0
        for rel_p, clean_t, art, alb, gen in fixes:
            full_p = os.path.join(self.organized_root, rel_p)
            if os.path.exists(full_p):
                # Also rename file if needed
                ext = os.path.splitext(full_p)[1]
                parent = os.path.dirname(full_p)
                clean_fn = f"{clean_t}{ext}"
                target_p = os.path.join(parent, clean_fn)
                if full_p != target_p and not os.path.exists(target_p):
                    shutil.move(full_p, target_p)
                    full_p = target_p

                self.organizer.write_id3_tags(
                    file_path=full_p,
                    title=clean_t,
                    artist=art,
                    album=alb,
                    genre=gen
                )
                count += 1
                print(f"  Polished: {rel_p} -> Title: '{clean_t}', Artist: '{art}'")
        return count

    def _polish_library_typography(self) -> Tuple[int, int]:
        print("\n>>> PASS 6: Global Typography & Capitalization Polish across 6,800+ tracks...")
        renamed_count = 0
        tagged_count = 0

        for root, dirs, files in os.walk(self.organized_root):
            for f in files:
                if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav')):
                    continue
                old_p = os.path.join(root, f)
                stem, ext = os.path.splitext(f)

                # Clean filename typography
                clean_stem = clean_typography(stem)

                # If changed, rename file (handles Windows case-insensitivity cleanly)
                target_p = old_p
                if clean_stem != stem:
                    new_fn = f"{clean_stem}{ext}"
                    new_p = os.path.join(root, new_fn)
                    try:
                        temp_p = os.path.join(root, f"__tmp_ren_{abs(hash(stem))}_{ext}")
                        os.rename(old_p, temp_p)
                        os.rename(temp_p, new_p)
                        target_p = new_p
                        renamed_count += 1
                    except Exception:
                        target_p = old_p

                # Clean embedded ID3/ASF title tag typography
                if ext.lower() == ".mp3":
                    try:
                        id3 = ID3(target_p)
                        old_t = str(id3.get("TIT2", ""))
                        clean_t = clean_typography(old_t)
                        if clean_t and clean_t != old_t:
                            id3["TIT2"] = TIT2(encoding=3, text=clean_t)
                            id3.save(target_p)
                            tagged_count += 1
                    except Exception:
                        pass
                elif ext.lower() == ".wma":
                    try:
                        asf = ASF(target_p)
                        if asf and asf.tags and "Title" in asf.tags:
                            old_t = str(asf.tags["Title"][0])
                            clean_t = clean_typography(old_t)
                            if clean_t and clean_t != old_t:
                                from mutagen.asf import ASFUnicodeAttribute
                                asf.tags["Title"] = [ASFUnicodeAttribute(clean_t)]
                                asf.save()
                                tagged_count += 1
                    except Exception:
                        pass

        print(f"  Global Typography Polish: Renamed {renamed_count} files | Updated {tagged_count} tags.")
        return renamed_count, tagged_count

if __name__ == "__main__":
    polisher = PrecisionPolisher()
    polisher.run_all_passes()
