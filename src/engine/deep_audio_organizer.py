"""
Auralis - Deep Audio Analysis & Intelligent Master Organizer
Performs strict, per-file deep analysis, language and domain classification,
embedded tag writing (ID3v2.4 / ASF / Vorbis / MP4), canonical renaming,
quality-aware deduplication, and atomic organization.
"""

import os
import re
import sys
import stat
import time
import hashlib
import sqlite3
import shutil
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Tuple

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, ID3NoHeaderError
from mutagen.asf import ASF
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4

logger = logging.getLogger("auralis.deep_organizer")

AUDIO_EXTENSIONS = {".mp3", ".wma", ".ogg", ".flac", ".wav", ".m4a", ".aac", ".ra", ".ram"}

KNOWN_BOLLYWOOD_MOVIES = [
    "omkara", "dil se", "lagaan", "rock on", "3 idiots", "kabhie khushi kabhie gham",
    "kal ho naa ho", "jab we met", "dhoom", "devdas", "aashiqui", "gangs of wasseypur",
    "teesri kasam", "shree 420", "don", "taare zameen par", "swades", "rang de basanti",
    "wake up sid", "zindagi na milegi dobara", "barfi", "yeh jawaani hai deewani",
    "kaminey", "highway", "haider", "dil chahta hai", "fanaa", "guru", "raanjhanaa",
    "kuch kuch hota hai", "ddlj", "dilwale dulhania le jayenge", "mohra", "baazigar",
    "saajan", "hum aapke hain koun", "raaz", "murder", "gangster", "jannat", "woh lamhe",
    "life in a metro", "delhi 6", "ajab prem ki ghazab kahani", "anwar", "ghajini",
    "chak de india", "dostana", "new york", "kaminey", "race", "partner", "namastey london"
]

OMKARA_TRACKS = ["beedi", "naina", "namak", "omkara", "jag ja ri gudiya", "o saathi re", "laakad"]

SUKTA_PATTERNS = [
    (r"purush(a)?[- ]?sukta?m?", "Purusha Suktam"),
    (r"shr[ei]{1,2}[- ]?sukta?m?", "Shree Suktam"),
    (r"\brudra(m)?\b|\bchamaka(m)?\b|\bnamaka(m)?\b|laghunyasa", "Shri Rudram"),
    (r"pavaman(a)?[- ]?(\d+)?", "Pavamana Suktam"),
    (r"ganapat(i|ya)[- ]?a?atharvash[ei]{1,2}rsha|ganapati[- ]?sukta", "Ganapati Atharvashirsha"),
    (r"\bsaur(a)?(\.wma|\.mp3|[- ]?sukta)", "Saura Suktam"),
    (r"trisuparna", "Trisuparna Suktam"),
    (r"ratri[- ]?sukta?m?", "Ratri Suktam"),
    (r"durga[- ]?sukta?m?", "Durga Suktam"),
    (r"medha[- ]?sukta?m?", "Medha Suktam"),
    (r"manyu[- ]?sukta?m?", "Manyu Suktam"),
    (r"nasadiya", "Nasadiya Suktam"),
    (r"ayushya[- ]?sukta?m?", "Ayushya Suktam"),
    (r"bhagya[- ]?sukta?m?", "Bhagya Suktam"),
    (r"shanti[- ]?(path|suktam?)", "Shanti Suktam")
]

STOTRA_PATTERNS = [
    (r"vishnu[- ]?saha[st]{1,3}rana[am]", "Vishnu Sahasranama Stotram"),
    (r"lalitha[- ]?sahas?rana[am]", "Lalitha Sahasranama Stotram"),
    (r"shiva[- ]?tandav(a)?", "Shiva Tandava Stotram"),
    (r"mahishasur[ -]?mardini", "Mahishasuramardini Stotram"),
    (r"shiva[- ]?mahimna", "Shiva Mahimna Stotram"),
    (r"shiva[- ]?manas(a)?[- ]?poo?ja", "Shiva Manasa Pooja"),
    (r"shiva[- ]?panchakshara", "Shiva Panchakshara Stotram"),
    (r"nirvana[- ]?shatakam?|nirvanashatakam?", "Nirvana Shatakam"),
    (r"bhavany?[- ]?ashtakam?", "Bhavani Ashtakam"),
    (r"madhur[- ]?ashtakam?", "Madhurashtakam"),
    (r"bilv[- ]?ashtakam?", "Bilvashtakam"),
    (r"guru[- ]?ashtakam?", "Guru Ashtakam"),
    (r"ling[- ]?ashtakam?", "Lingashtakam"),
    (r"kalabhairav(a)?[- ]?ashtakam?", "Kalabhairava Ashtakam"),
    (r"daridraya[- ]?dahana", "Daridraya Dahana Stotram"),
    (r"venkatesh(a)?[- ]?(stotram?|suprabhatam)", "Shri Venkatesha Stotram"),
    (r"dattatreya[- ]?stotram?", "Shri Dattatreya Stotram"),
    (r"navagraha[- ]?stotram?", "Shri Navagraha Stotram"),
    (r"suryamandal(a)?|aditya[- ]?hridaya", "Shri Suryamandala Stotram"),
    (r"annapoorna[- ]?stotram?", "Annapoorna Stotram"),
    (r"charpat[- ]?panjarika|bhaja[- ]?govindam", "Charpat Panjarika Stotram (Bhaja Govindam)"),
    (r"dvadash[- ]?panjarika", "Dvadash Panjarika Stotram"),
    (r"shatpadi[- ]?stotram?", "Shatpadi Stotram"),
    (r"shakambhari[- ]?stotram?", "Shri Shakambhari Stotram"),
    (r"gopi[- ]?geet(am)?", "Shri Gopi Gitam"),
    (r"aghorakashtoddharan", "Aghorakashtoddharana Stotra"),
    (r"arbudadevi", "Arbudadevi Stotra"),
    (r"ardanarinateshwar", "Ardhanarishwara Stotra")
]

CANONICAL_ARTISTS_MAP = {
    "coldplay": "Coldplay",
    "nirvana": "Nirvana",
    "the beatles": "The Beatles",
    "beatles": "The Beatles",
    "john lennon": "John Lennon",
    "lennon": "John Lennon",
    "paul mccartney": "The Beatles",
    "george harrison": "The Beatles",
    "queen": "Queen",
    "led zeppelin": "Led Zeppelin",
    "the doors": "The Doors",
    "doors": "The Doors",
    "the police": "The Police",
    "police": "The Police",
    "sting": "The Police",
    "deep purple": "Deep Purple",
    "black sabbath": "Black Sabbath",
    "the eagles": "The Eagles",
    "eagles": "The Eagles",
    "pink floyd": "Pink Floyd",
    "u2": "U2",
    "green day": "Green Day",
    "iron maiden": "Iron Maiden",
    "metallica": "Metallica",
    "megadeth": "Megadeth",
    "pearl jam": "Pearl Jam",
    "linkin park": "Linkin Park",
    "red hot chili peppers": "Red Hot Chili Peppers",
    "radiohead": "Radiohead",
    "rage against the machine": "Rage Against The Machine",
    "audioslave": "Audioslave",
    "soundgarden": "Soundgarden",
    "faith no more": "Faith No More",
    "dire straits": "Dire Straits",
    "guns n roses": "Guns N Roses",
    "guns and roses": "Guns N Roses",
    "switchfoot": "Switchfoot",
    "rammstein": "Rammstein",
    "nickelback": "Nickelback",
    "eminem": "Eminem",
    "michael jackson": "Michael Jackson",
    "enrique iglesias": "Enrique Iglesias",
    "bryan adams": "Bryan Adams",
    "bon jovi": "Bon Jovi",
    "bob marley": "Bob Marley",
    "scorpions": "Scorpions",
    "aerosmith": "Aerosmith",
    "david guetta": "David Guetta",
    "pitbull": "Pitbull",
    "when chai met toast": "When Chai Met Toast",
    "pankaj udhas": "Pankaj Udhas",
    "pankaj udas": "Pankaj Udhas",
    "jagjit singh": "Jagjit Singh",
    "mukesh": "Mukesh",
    "lata mangeshkar": "Lata Mangeshkar",
    "lata": "Lata Mangeshkar",
    "kishore kumar": "Kishore Kumar",
    "kishore": "Kishore Kumar",
    "mohd rafi": "Mohammed Rafi",
    "mohammed rafi": "Mohammed Rafi",
    "rafi": "Mohammed Rafi",
    "asha bhosle": "Asha Bhosle",
    "asha": "Asha Bhosle",
    "rd burman": "R.D. Burman",
    "manna dey": "Manna Dey",
    "talat mahmood": "Talat Mahmood",
    "hemant kumar": "Hemant Kumar",
    "geeta dutt": "Geeta Dutt",
    "ar rahman": "A.R. Rahman",
    "arijit singh": "Arijit Singh",
    "shankar mahadevan": "Shankar Mahadevan",
    "shreya ghoshal": "Shreya Ghoshal",
    "sonu nigam": "Sonu Nigam",
    "lucky ali": "Lucky Ali",
    "kailash kher": "Kailash Kher",
    "atif aslam": "Atif Aslam",
    "shaan": "Shaan",
    "kk": "KK",
    "udit narayan": "Udit Narayan",
    "kumar sanu": "Kumar Sanu",
    "alka yagnik": "Alka Yagnik",
    "sunidhi chauhan": "Sunidhi Chauhan",
    "vaibhavi shete": "Vaibhavi Shete",
    "ramdas kamat": "Ramdas Kamat",
    "vasantrao deshpande": "Vasantrao Deshpande",
    "suresh wadkar": "Suresh Wadkar",
    "bhimsen joshi": "Pt. Bhimsen Joshi"
}

JUNK_WATERMARKS = [
    r"\[.*?djluv.*?\]", r"\[.*?songs\.pk.*?\]", r"\[.*?bindassbuzz.*?\]",
    r"\[.*?mp3.*?\]", r"\[.*?128kbps.*?\]", r"\[.*?320kbps.*?\]", r"\[.*?256kbps.*?\]",
    r"\[.*?kbps.*?\]", r"\[.*?rip.*?\]", r"\[.*?edition.*?\]", r"\[.*?tuberip.*?\]",
    r"www\.[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,4}", r"\(.*?mp3.*?\)", r"_www\.[a-zA-Z0-9_\-\.]+",
    r"\[.*?\]"
]

def clean_watermark_text(text: str) -> str:
    cleaned = text
    for pat in JUNK_WATERMARKS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("_", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned

def clean_title_str(s: str) -> str:
    s = clean_watermark_text(s)
    s = re.sub(r"^\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\s*\(\d{4}\)$", "", s)
    s = re.sub(r"\b(com|pk|in|net|org|us|info|co)\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(apniisp|pakheaven|papuyaar|fmw11|songs\.pk|djluv)\b", "", s, flags=re.IGNORECASE)
    s = s.strip(" ._-\\/")
    return s.strip().title()

def sanitize_filesystem_name(name: str) -> str:
    invalid_chars = r'<>:"/\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "")
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name or "Untitled"

def compute_audio_hash(file_path: str, block_size: int = 131072) -> Optional[str]:
    """Computes fast signature hash: size + MD5 of head, mid, tail frames."""
    try:
        size = os.path.getsize(file_path)
        if size == 0:
            return None
        hasher = hashlib.md5(usedforsecurity=False)
        with open(file_path, "rb") as f:
            if size <= block_size * 3:
                hasher.update(f.read())
            else:
                hasher.update(f.read(block_size))
                f.seek(size // 2)
                hasher.update(f.read(block_size))
                f.seek(max(0, size - block_size))
                hasher.update(f.read(block_size))
        return f"{size}_{hasher.hexdigest()}"
    except Exception:
        return None

class DeepAudioOrganizer:
    """Enterprise-grade deep audio analysis and organization engine."""

    def __init__(
        self,
        unorganized_root: str = r"D:\Songs\unorganized",
        organized_root: str = r"D:\Songs\organized",
        db_path: str = r"D:\Code\avinya-forge\auralis\auralis_inventory.db",
        num_workers: int = 8
    ):
        self.unorganized_root = unorganized_root
        self.organized_root = organized_root
        self.duplicates_dir = os.path.join(unorganized_root, "_duplicates_backup")
        self.corrupt_dir = os.path.join(unorganized_root, "_corrupted_backup")
        self.db_path = db_path
        self.num_workers = num_workers
        self._db_lock = threading.Lock()
        
        # In-memory deduplication registry: hash -> (organized_file_path, bitrate, duration)
        self.organized_registry: Dict[str, Tuple[str, int, float]] = {}
        self.init_database()

    def init_database(self) -> None:
        os.makedirs(self.organized_root, exist_ok=True)
        os.makedirs(self.duplicates_dir, exist_ok=True)
        os.makedirs(self.corrupt_dir, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS master_organized_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT NOT NULL,
            organized_path TEXT NOT NULL,
            language TEXT,
            category TEXT,
            clean_title TEXT,
            clean_artist TEXT,
            album TEXT,
            duration REAL,
            bitrate INTEGER,
            file_hash TEXT,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # Schema migration check
        cols = [c[1] for c in cur.execute("PRAGMA table_info(master_organized_transactions)").fetchall()]
        for col, col_type in [("duration", "REAL"), ("bitrate", "INTEGER"), ("file_hash", "TEXT")]:
            if col not in cols:
                cur.execute(f"ALTER TABLE master_organized_transactions ADD COLUMN {col} {col_type}")

        cur.execute("CREATE INDEX IF NOT EXISTS idx_mot_hash ON master_organized_transactions(file_hash)")
        conn.commit()
        conn.close()

    def read_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Reads audio properties and embedded tags using Mutagen."""
        meta: Dict[str, Any] = {
            "duration": 0.0,
            "bitrate": 0,
            "channels": 2,
            "sample_rate": 44100,
            "tag_title": "",
            "tag_artist": "",
            "tag_album": "",
            "tag_genre": "",
            "tag_year": "",
            "is_corrupt": False
        }
        try:
            size = os.path.getsize(file_path)
            if size == 0:
                meta["is_corrupt"] = True
                return meta

            audio = mutagen.File(file_path)
            if audio is None or not hasattr(audio, "info") or audio.info is None:
                # If MP3, attempt specialized MP3 reader
                if file_path.lower().endswith(".mp3"):
                    try:
                        mp3_f = MP3(file_path)
                        audio = mp3_f
                    except Exception:
                        meta["is_corrupt"] = True
                        return meta
                else:
                    meta["is_corrupt"] = True
                    return meta

            dur = getattr(audio.info, "length", 0.0)
            br = getattr(audio.info, "bitrate", 0)
            ch = getattr(audio.info, "channels", 2)
            sr = getattr(audio.info, "samplerate", 44100)

            meta["duration"] = float(round(dur, 2)) if isinstance(dur, (int, float)) else 0.0
            meta["bitrate"] = int(br) if isinstance(br, (int, float)) else 0
            meta["channels"] = int(ch) if isinstance(ch, int) else 2
            meta["sample_rate"] = int(sr) if isinstance(sr, int) else 44100

            if meta["duration"] <= 0.5:
                meta["is_corrupt"] = True
                return meta

            # Extract tags safely across formats
            tags = audio.tags
            if tags:
                def get_tag_val(*keys) -> str:
                    for k in keys:
                        if k in tags:
                            v = tags[k]
                            if isinstance(v, (list, tuple)) and v:
                                return str(v[0]).strip()
                            return str(v).strip()
                    return ""

                # Format specific keys
                if isinstance(audio, MP3) or isinstance(tags, ID3):
                    meta["tag_title"] = get_tag_val("TIT2")
                    meta["tag_artist"] = get_tag_val("TPE1")
                    meta["tag_album"] = get_tag_val("TALB")
                    meta["tag_genre"] = get_tag_val("TCON")
                    meta["tag_year"] = get_tag_val("TDRC")
                elif isinstance(audio, ASF):
                    meta["tag_title"] = get_tag_val("Title")
                    meta["tag_artist"] = get_tag_val("Author", "WM/AlbumArtist")
                    meta["tag_album"] = get_tag_val("WM/AlbumTitle")
                    meta["tag_genre"] = get_tag_val("WM/Genre")
                    meta["tag_year"] = get_tag_val("WM/Year")
                elif isinstance(audio, (FLAC, OggVorbis)):
                    meta["tag_title"] = get_tag_val("title")
                    meta["tag_artist"] = get_tag_val("artist")
                    meta["tag_album"] = get_tag_val("album")
                    meta["tag_genre"] = get_tag_val("genre")
                    meta["tag_year"] = get_tag_val("date", "year")
                elif isinstance(audio, MP4):
                    meta["tag_title"] = get_tag_val("\xa9nam")
                    meta["tag_artist"] = get_tag_val("\xa9ART")
                    meta["tag_album"] = get_tag_val("\xa9alb")
                    meta["tag_genre"] = get_tag_val("\xa9gen")
                    meta["tag_year"] = get_tag_val("\xa9day")

        except Exception:
            meta["is_corrupt"] = True

        return meta

    def update_embedded_tags(
        self,
        file_path: str,
        title: str,
        artist: str,
        album: str,
        genre: str,
        year: str = ""
    ) -> bool:
        """Writes clean standard tags into the audio file with NTFS read-only clearance."""
        try:
            try:
                os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass

            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".mp3":
                try:
                    audio = ID3(file_path)
                except ID3NoHeaderError:
                    audio = ID3()
                if title: audio["TIT2"] = TIT2(encoding=3, text=title)
                if artist: audio["TPE1"] = TPE1(encoding=3, text=artist)
                if album: audio["TALB"] = TALB(encoding=3, text=album)
                if genre: audio["TCON"] = TCON(encoding=3, text=genre)
                if year: audio["TDRC"] = TDRC(encoding=3, text=year)
                audio["TPE2"] = TPE2(encoding=3, text=artist)
                audio.save(file_path, v2_version=4)
                return True

            elif ext == ".wma":
                audio = ASF(file_path)
                if title: audio["Title"] = [title]
                if artist: audio["Author"] = [artist]; audio["WM/AlbumArtist"] = [artist]
                if album: audio["WM/AlbumTitle"] = [album]
                if genre: audio["WM/Genre"] = [genre]
                if year: audio["WM/Year"] = [year]
                audio.save()
                return True

            elif ext in [".ogg", ".flac"]:
                audio = mutagen.File(file_path)
                if audio is not None:
                    if title: audio["title"] = [title]
                    if artist: audio["artist"] = [artist]
                    if album: audio["album"] = [album]
                    if genre: audio["genre"] = [genre]
                    if year: audio["date"] = [year]
                    audio.save()
                    return True

            elif ext == ".m4a":
                audio = MP4(file_path)
                if title: audio["\xa9nam"] = [title]
                if artist: audio["\xa9ART"] = [artist]
                if album: audio["\xa9alb"] = [album]
                if genre: audio["\xa9gen"] = [genre]
                if year: audio["\xa9day"] = [year]
                audio.save()
                return True

        except Exception:
            return False

        return False

    def classify_audio_track(
        self,
        file_path: str,
        filename: str,
        tag_title: str = "",
        tag_artist: str = "",
        tag_album: str = "",
        tag_genre: str = ""
    ) -> Dict[str, str]:
        """
        Deep linguistic & domain classification:
        Language First -> Topic/Scripture/Soundtrack -> Canonical Title & Artist.
        """
        stem, ext = os.path.splitext(filename)
        clean_stem = clean_watermark_text(stem)
        combined = f"{filename.lower()} {tag_title.lower()} {tag_artist.lower()} {tag_album.lower()} {file_path.lower()}"

        # 1. SPECIAL CASE: OMKARA BOLLYWOOD SOUNDTRACK (NEVER SANSKRIT)
        is_omkara = False
        if "omkara" in combined:
            if any(tr in combined for tr in OMKARA_TRACKS) or any(a in combined for a in ["vishal", "bhardwaj", "sukhwinder", "sunidhi", "rekha", "rahat", "gulzar"]):
                is_omkara = True
            elif "beedi" in combined or "namak" in combined or "naina" in combined:
                is_omkara = True

        if is_omkara:
            found_title = "Omkara"
            for tr in OMKARA_TRACKS:
                if tr in combined:
                    found_title = tr.title()
                    break
            return {
                "language": "Hindi",
                "category": "Soundtracks\\Omkara",
                "title": found_title,
                "artist": "Vishal Bhardwaj",
                "album": "Omkara",
                "genre": "Bollywood Soundtrack"
            }

        # 2. SANSKRIT SACRED CHANTS DISAMBIGUATION
        # A. Vedic Suktas
        for pat, canon_name in SUKTA_PATTERNS:
            if re.search(pat, combined, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Vedic Suktas",
                    "title": canon_name,
                    "artist": "Traditional Vedic Chants",
                    "album": "Vedic Suktas",
                    "genre": "Sanskrit / Vedic Suktas"
                }

        # B. Stotras & Ashtakams (Includes Nirvana Shatakam, avoiding English Nirvana band trap)
        for pat, canon_name in STOTRA_PATTERNS:
            if re.search(pat, combined, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Stotras & Ashtakams",
                    "title": canon_name,
                    "artist": "Traditional Sanskrit Chants",
                    "album": "Stotras & Ashtakams",
                    "genre": "Sanskrit / Stotras"
                }

        # C. Vedic Samhita & Parayanam
        if "atharva veda" in combined or "atharva-veda" in combined or re.search(r"\bkanda\s*\d+", combined, re.IGNORECASE):
            m_kanda = re.search(r"(kanda\s*\d+[^.]+)", stem, re.IGNORECASE)
            t_name = clean_title_str(m_kanda.group(1)) if m_kanda else clean_title_str(clean_stem)
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Atharva Veda",
                "title": t_name,
                "artist": "Vedic Scholars",
                "album": "Atharva Veda Samhita",
                "genre": "Sanskrit / Vedic Samhita"
            }

        if "bh-samhita" in combined or "shrimad-bhagawat-samhita" in combined or "bhagavat samhita" in combined:
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Shrimad Bhagawat Samhita",
                "title": clean_title_str(clean_stem),
                "artist": "Traditional Vedic Chants",
                "album": "Shrimad Bhagawat Samhita",
                "genre": "Sanskrit / Vedic Samhita"
            }

        # D. Upanishads
        if "chaakshushopnishad" in combined or "chakshushopanishad" in combined:
            return {
                "language": "Sanskrit",
                "category": "Upanishads",
                "title": "Chakshushopanishad",
                "artist": "Traditional Vedic Chants",
                "album": "Upanishads",
                "genre": "Sanskrit / Upanishads"
            }

        # E. General Sanskrit Chants
        sanskrit_kw = ["suktam", "sukta", "stotram", "stotra", "ashtakam", "ashtak", "vedic", "atharvashirsha"]
        if any(k in combined for k in sanskrit_kw):
            return {
                "language": "Sanskrit",
                "category": "Vedic Suktas",
                "title": clean_title_str(clean_stem),
                "artist": "Traditional Vedic Chants",
                "album": "Vedic Suktas & Stotras",
                "genre": "Sanskrit"
            }

        # 3. PRAVACHAN & SPIRITUAL DISCOURSES
        pravachan_keys = ["pravachan", "discourse", "katha", "adhyay", "purushottamyog", "ghaisasi", "kavishwar", "abhyankar"]
        if any(k in combined for k in pravachan_keys) and not any(b in combined for b in ["talaash", "bollywood", "soundtrack"]):
            if "ghaisasi" in combined:
                return {
                    "language": "Pravachan",
                    "category": "Bhagwat Katha\\Ghaisasi Guruji",
                    "title": clean_title_str(clean_stem),
                    "artist": "Ghaisasi Guruji",
                    "album": "Bhagwat Katha",
                    "genre": "Pravachan / Katha"
                }
            elif "kavishwar" in combined:
                return {
                    "language": "Pravachan",
                    "category": "Bhagwat Katha\\Kavishwar Maharaj",
                    "title": clean_title_str(clean_stem),
                    "artist": "Kavishwar Maharaj",
                    "album": "Bhagwat Katha",
                    "genre": "Pravachan / Katha"
                }
            elif "abhyankar" in combined or "purushottam" in combined or "gita" in combined or "geeta" in combined:
                spk = "Aparna Abhyankar" if "aparna" in combined else "Shankar Abhyankar"
                return {
                    "language": "Pravachan",
                    "category": f"Bhagavad Gita\\{spk}",
                    "title": clean_title_str(clean_stem),
                    "artist": spk,
                    "album": "Bhagavad Gita Discourses",
                    "genre": "Pravachan / Gita"
                }
            return {
                "language": "Pravachan",
                "category": "Spiritual Discourses",
                "title": clean_title_str(clean_stem),
                "artist": "Discourses",
                "album": "Spiritual Discourses",
                "genre": "Pravachan"
            }

        # 4. MARATHI MUSIC (Natyasangeet, Vaibhavi Shete, Abhang)
        if any(k in combined for k in ["natyasangeet", "naman natwara", "abhang", "vitthal", "mauli", "tukaram", "shete", "bhavgeet", "dnyaneshwar"]):
            if "shete" in combined or "akhilam madhuram" in combined:
                return {
                    "language": "Marathi",
                    "category": "Vaibhavi Shete\\Akhilam Madhuram",
                    "title": clean_title_str(clean_stem),
                    "artist": "Vaibhavi Shete",
                    "album": "Akhilam Madhuram",
                    "genre": "Marathi Devotional"
                }
            elif "natyasangeet" in combined or "naman natwara" in combined:
                return {
                    "language": "Marathi",
                    "category": "Natyasangeet",
                    "title": clean_title_str(clean_stem),
                    "artist": tag_artist or "Traditional Marathi Natyasangeet",
                    "album": "Marathi Natyasangeet",
                    "genre": "Natyasangeet"
                }
            elif "abhang" in combined or "vitthal" in combined or "mauli" in combined:
                return {
                    "language": "Marathi",
                    "category": "Abhang & Bhakti",
                    "title": clean_title_str(clean_stem),
                    "artist": tag_artist or "Marathi Bhakti Sangeet",
                    "album": "Vitthal Abhang",
                    "genre": "Marathi Abhang"
                }
            return {
                "language": "Marathi",
                "category": "Bhavgeet & Classics",
                "title": clean_title_str(clean_stem),
                "artist": tag_artist or "Various Marathi Artists",
                "album": "Marathi Bhavgeet",
                "genre": "Marathi"
            }

        # 5. ENGLISH / WESTERN ROCK, METAL & POP (Strict Word Boundaries)
        for canon_key, canon_name in CANONICAL_ARTISTS_MAP.items():
            if re.search(r"\b" + re.escape(canon_key) + r"\b", combined, re.IGNORECASE):
                # Ensure it's not an Indian artist matching English rule
                if canon_name not in ["Lata Mangeshkar", "Kishore Kumar", "Mohammed Rafi", "Mukesh", "Asha Bhosle", "Jagjit Singh", "Pankaj Udhas", "Vaibhavi Shete", "Ramdas Kamat", "Vasantrao Deshpande", "Suresh Wadkar", "Pt. Bhimsen Joshi", "A.R. Rahman", "Arijit Singh", "Sonu Nigam", "Shankar Mahadevan", "Shreya Ghoshal", "Lucky Ali"]:
                    return {
                        "language": "English",
                        "category": canon_name,
                        "title": clean_title_str(clean_stem),
                        "artist": canon_name,
                        "album": tag_album or canon_name,
                        "genre": "Rock & Pop"
                    }

        # 6. HINDI BOLLYWOOD & CLASSICS
        # A. Check known Bollywood movies
        for mov in KNOWN_BOLLYWOOD_MOVIES:
            if re.search(r"\b" + re.escape(mov) + r"\b", combined, re.IGNORECASE):
                return {
                    "language": "Hindi",
                    "category": f"Soundtracks\\{mov.title()}",
                    "title": clean_title_str(clean_stem),
                    "artist": tag_artist or "Various Artists",
                    "album": mov.title(),
                    "genre": "Bollywood Soundtrack"
                }

        # B. Check Golden Era Classics & Ghazals
        for art_key in ["pankaj udhas", "pankaj udas", "jagjit singh"]:
            if art_key in combined:
                c_name = CANONICAL_ARTISTS_MAP[art_key]
                return {
                    "language": "Hindi",
                    "category": f"Ghazals\\{c_name}",
                    "title": clean_title_str(clean_stem),
                    "artist": c_name,
                    "album": tag_album or f"Best of {c_name}",
                    "genre": "Hindi Ghazals"
                }

        for art_key in ["lata", "rafi", "kishore", "mukesh", "asha", "rd burman", "manna dey", "talat", "hemant", "geeta dutt"]:
            if re.search(r"\b" + re.escape(art_key) + r"\b", combined, re.IGNORECASE):
                c_name = CANONICAL_ARTISTS_MAP.get(art_key, art_key.title())
                return {
                    "language": "Hindi",
                    "category": f"Classics\\{c_name}",
                    "title": clean_title_str(clean_stem),
                    "artist": c_name,
                    "album": tag_album or f"Classics of {c_name}",
                    "genre": "Bollywood Classics"
                }

        # C. Contemporary Hits
        for art_key in ["arijit", "sonu nigam", "sonu", "shreya", "shaan", "kk", "lucky ali", "kailash kher", "atif", "sukhwinder", "sunidhi", "shankar mahadevan"]:
            if re.search(r"\b" + re.escape(art_key) + r"\b", combined, re.IGNORECASE):
                c_name = CANONICAL_ARTISTS_MAP.get(art_key, art_key.title())
                return {
                    "language": "Hindi",
                    "category": f"Pop & Hits\\{c_name}",
                    "title": clean_title_str(clean_stem),
                    "artist": c_name,
                    "album": tag_album or f"Hits of {c_name}",
                    "genre": "Hindi Pop"
                }

        # D. Devotional (e.g. Jai Shiva Omkara)
        if "jai shiva omkara" in combined or "shiva omkara" in combined or "bhajan" in combined or "aarti" in combined:
            return {
                "language": "Hindi",
                "category": "Devotional & Bhajans",
                "title": clean_title_str(clean_stem),
                "artist": tag_artist or "Devotional",
                "album": "Bhajan & Aarti Sangrah",
                "genre": "Hindi Devotional"
            }

        # Check if path indicates English directory
        if r"\english" in file_path.lower():
            parent_dir = os.path.basename(os.path.dirname(file_path))
            eng_cat = tag_artist or (parent_dir if parent_dir.lower() not in ["english", "bmw-music", "unorganized", "organized"] else "Rock & Pop")
            return {
                "language": "English",
                "category": clean_title_str(eng_cat),
                "title": clean_title_str(clean_stem),
                "artist": tag_artist or eng_cat,
                "album": tag_album or eng_cat,
                "genre": "English"
            }

        # Default Hindi Album / Evergreen Classics
        alb = clean_title_str(tag_album) if tag_album and len(tag_album) > 2 else "Evergreen Classics"
        return {
            "language": "Hindi",
            "category": alb,
            "title": clean_title_str(clean_stem),
            "artist": tag_artist or "Various Artists",
            "album": alb,
            "genre": "Hindi"
        }

    def process_single_file(self, file_path: str) -> Dict[str, Any]:
        """Processes ONE single file with strict physical analysis, tagging, deduplication, and relocation."""
        result: Dict[str, Any] = {
            "original_path": file_path,
            "organized_path": "",
            "status": "FAILED",
            "language": "",
            "category": "",
            "title": "",
            "artist": "",
            "error": None
        }

        if not os.path.exists(file_path):
            result["error"] = "File not found"
            return result

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        # Step 1: Physical Audio Analysis
        meta = self.read_audio_metadata(file_path)
        if meta["is_corrupt"]:
            dest_corrupt = os.path.join(self.corrupt_dir, filename)
            try:
                shutil.move(file_path, dest_corrupt)
                result["status"] = "CORRUPT_QUARANTINE"
                result["organized_path"] = dest_corrupt
                self._record_transaction(file_path, dest_corrupt, "Corrupt", "Corrupted Files", filename, "N/A", "N/A", 0.0, 0, None, "CORRUPT_QUARANTINE")
            except Exception as e:
                result["error"] = str(e)
            return result

        # Step 2: Content Signature for Deduplication
        f_hash = compute_audio_hash(file_path)
        duration = meta["duration"]
        bitrate = meta["bitrate"]

        # Step 3: Deep Linguistic & Metadata Classification
        classification = self.classify_audio_track(
            file_path=file_path,
            filename=filename,
            tag_title=meta["tag_title"],
            tag_artist=meta["tag_artist"],
            tag_album=meta["tag_album"],
            tag_genre=meta["tag_genre"]
        )

        lang = classification["language"]
        cat = classification["category"]
        title = classification["title"]
        artist = classification["artist"]
        album = classification["album"]
        genre = classification["genre"]
        year = meta["tag_year"]

        result["language"] = lang
        result["category"] = cat
        result["title"] = title
        result["artist"] = artist

        # Step 4: Write Clean ID3 / Embedded Tags
        self.update_embedded_tags(
            file_path=file_path,
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            year=year
        )

        # Step 5: Canonical Destination Filename
        clean_fn = sanitize_filesystem_name(title) + ext
        cat_parts = [sanitize_filesystem_name(p) for p in cat.replace("/", "\\").split("\\") if p.strip()]
        dest_dir = os.path.join(self.organized_root, lang, *cat_parts)
        target_path = os.path.join(dest_dir, clean_fn)

        # Step 6: Deduplication Check
        # Check against in-memory registry or target collision
        is_duplicate = False
        with self._db_lock:
            if f_hash and f_hash in self.organized_registry:
                existing_path, existing_br, existing_dur = self.organized_registry[f_hash]
                is_duplicate = True
                # If current file has higher bitrate, replace the existing one!
                if bitrate > existing_br and os.path.exists(existing_path):
                    # Move existing to duplicates backup
                    dup_dest = os.path.join(self.duplicates_dir, os.path.basename(existing_path))
                    if os.path.exists(dup_dest):
                        base, e = os.path.splitext(dup_dest)
                        dup_dest = f"{base}_{int(time.time())}{e}"
                    shutil.move(existing_path, dup_dest)
                    self._record_transaction(existing_path, dup_dest, "Duplicates", "Lower Bitrate", os.path.basename(existing_path), "N/A", "N/A", existing_dur, existing_br, f_hash, "EXACT_DUPLICATE_BACKUP")
                    # Update registry with new superior file
                    self.organized_registry[f_hash] = (target_path, bitrate, duration)
                    is_duplicate = False

        if is_duplicate:
            dup_dest = os.path.join(self.duplicates_dir, filename)
            if os.path.exists(dup_dest):
                base, e = os.path.splitext(dup_dest)
                dup_dest = f"{base}_{int(time.time())}{e}"
            try:
                shutil.move(file_path, dup_dest)
                result["status"] = "DUPLICATE_BACKUP"
                result["organized_path"] = dup_dest
                self._record_transaction(file_path, dup_dest, "Duplicates", "Identical Audio", title, artist, album, duration, bitrate, f_hash, "EXACT_DUPLICATE_BACKUP")
            except Exception as e:
                result["error"] = str(e)
            return result

        # Step 7: Atomic Move to Organized
        os.makedirs(dest_dir, exist_ok=True)
        # Avoid filename collisions with different songs
        final_dest = target_path
        if os.path.exists(final_dest):
            # Check if identical file already exists at target
            if compute_audio_hash(final_dest) == f_hash:
                # Same file already at destination, archive this redundant copy
                dup_dest = os.path.join(self.duplicates_dir, filename)
                if os.path.exists(dup_dest):
                    base, e = os.path.splitext(dup_dest)
                    dup_dest = f"{base}_{int(time.time())}{e}"
                shutil.move(file_path, dup_dest)
                result["status"] = "DUPLICATE_BACKUP"
                result["organized_path"] = dup_dest
                self._record_transaction(file_path, dup_dest, "Duplicates", "Identical Audio", title, artist, album, duration, bitrate, f_hash, "EXACT_DUPLICATE_BACKUP")
                return result
            else:
                # Different song with same title, append artist or counter
                art_suffix = sanitize_filesystem_name(artist)
                final_dest = os.path.join(dest_dir, f"{sanitize_filesystem_name(title)} - {art_suffix}{ext}")
                if os.path.exists(final_dest):
                    i = 2
                    while os.path.exists(os.path.join(dest_dir, f"{sanitize_filesystem_name(title)} ({i}){ext}")):
                        i += 1
                    final_dest = os.path.join(dest_dir, f"{sanitize_filesystem_name(title)} ({i}){ext}")

        try:
            shutil.move(file_path, final_dest)
            result["status"] = "ORGANIZED"
            result["organized_path"] = final_dest

            with self._db_lock:
                if f_hash:
                    self.organized_registry[f_hash] = (final_dest, bitrate, duration)

            self._record_transaction(file_path, final_dest, lang, cat, title, artist, album, duration, bitrate, f_hash, "ORGANIZE_UNIQUE")
        except Exception as e:
            result["error"] = str(e)

        return result

    def _record_transaction(
        self,
        orig: str,
        dest: str,
        lang: str,
        cat: str,
        title: str,
        artist: str,
        album: str,
        duration: float,
        bitrate: int,
        f_hash: Optional[str],
        status: str
    ) -> None:
        """Thread-safe SQLite transaction recorder."""
        try:
            with self._db_lock:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO master_organized_transactions 
                (original_path, organized_path, language, category, clean_title, clean_artist, album, duration, bitrate, file_hash, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (orig, dest, lang, cat, title, artist, album, duration, bitrate, f_hash, status))
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")

    def execute_reorganization(self, max_files: Optional[int] = None) -> Dict[str, Any]:
        """Gathers all audio files in unorganized, runs multi-threaded deep analysis and organization."""
        print(f"[*] Discovering audio files in: {self.unorganized_root}...")
        all_files: List[str] = []

        for root, dirs, files in os.walk(self.unorganized_root):
            # Skip backup directories from re-scanning
            if "_duplicates_backup" in root or "_corrupted_backup" in root:
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in AUDIO_EXTENSIONS:
                    all_files.append(os.path.join(root, f))

        total_discovered = len(all_files)
        print(f"[*] Discovered {total_discovered} audio tracks to analyze and organize.")

        if max_files and max_files < total_discovered:
            all_files = all_files[:max_files]
            print(f"[*] Limiting batch to {max_files} files.")

        stats = {
            "total_processed": 0,
            "organized": 0,
            "duplicates": 0,
            "corrupt": 0,
            "errors": 0,
            "by_language": {}
        }

        start_time = time.time()
        print(f"[*] Starting {self.num_workers} parallel workers (strict per-file focus)...")

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_file = {executor.submit(self.process_single_file, f): f for f in all_files}

            for future in as_completed(future_to_file):
                f_path = future_to_file[future]
                try:
                    res = future.result()
                    stats["total_processed"] += 1
                    status = res["status"]

                    if status == "ORGANIZED":
                        stats["organized"] += 1
                        lang = res.get("language", "Unknown")
                        stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1
                    elif status == "DUPLICATE_BACKUP":
                        stats["duplicates"] += 1
                    elif status == "CORRUPT_QUARANTINE":
                        stats["corrupt"] += 1
                    else:
                        stats["errors"] += 1

                    if stats["total_processed"] % 250 == 0 or stats["total_processed"] == len(all_files):
                        elapsed = time.time() - start_time
                        fps = stats["total_processed"] / elapsed if elapsed > 0 else 0
                        print(f"[{stats['total_processed']}/{len(all_files)}] Organized: {stats['organized']} | Dupes: {stats['duplicates']} | ({fps:.1f} tracks/sec)")

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Worker failure on {f_path}: {e}")

        elapsed_total = time.time() - start_time
        print(f"\n=======================================================")
        print(f"[*] Master Reorganization Complete in {elapsed_total:.2f} seconds!")
        print(f"[*] Total Processed: {stats['total_processed']}")
        print(f"[*] Organized (Unique): {stats['organized']}")
        print(f"[*] Redundant Duplicates Archived: {stats['duplicates']}")
        print(f"[*] Corrupted Files Quarantined: {stats['corrupt']}")
        print(f"[*] Processing Velocity: {stats['total_processed'] / elapsed_total:.1f} files/sec")
        print(f"[*] Breakdown by Language: {stats['by_language']}")
        print(f"=======================================================\n")

        return stats

if __name__ == "__main__":
    organizer = DeepAudioOrganizer()
    organizer.execute_reorganization()
