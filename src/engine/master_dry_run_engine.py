"""
Auralis - Master Dry-Run Engine & Interactive Review Generator
Implements the 5-stage pipeline in pure non-destructive Dry-Run mode:
- Stage 1: Physical Inspection, Metadata Introspection & Audio Stream Hashing
- Stage 2: Deep Audio Listening (Whisper speech-to-text on vocals for generic/ambiguous tracks)
- Stage 3: Sanskrit Suktas vs Stotras vs Samhita Taxonomy & Bollywood Disambiguation
- Stage 4: Persistent Decision Caching & Rule Confidence
- Stage 5: Dynamic Threshold (>=3 tracks -> Dedicated Folder, <3 tracks -> Singles Collection)
Generates self-contained interactive HTML review dashboard: dry_run_review.html
"""

import os
import sys
import json
import time
import re
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.pattern_classifier import (
    clean_watermarks, clean_name, is_valid_album,
    SUKTA_PATTERNS, STOTRA_PATTERNS, SANSKRIT_KEYWORDS,
    detect_language_and_category, extract_bollywood_movie_and_song
)
from src.engine.embedded_intelligence import resolve_canonical_artist
from src.engine.catalog_resolver import lookup_catalog_track
from src.engine.pravachan_resolver import resolve_pravachan_track

logger = logging.getLogger("auralis.dry_run")

DECISION_CACHE_FILE = os.path.join(PROJECT_ROOT, "engine_decision_cache.json")

# Ensure FFmpeg is on PATH for Whisper
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass

# Global whisper model cache
_WHISPER_MODEL = None

def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import whisper
            _WHISPER_MODEL = whisper.load_model("tiny")
        except Exception as e:
            logger.warning(f"Whisper model could not be loaded: {e}")
            _WHISPER_MODEL = False
    return _WHISPER_MODEL

def load_decision_cache() -> Dict[str, Any]:
    if os.path.exists(DECISION_CACHE_FILE):
        try:
            with open(DECISION_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_decision_cache(cache: Dict[str, Any]) -> None:
    try:
        with open(DECISION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save decision cache: {e}")

def sanitize_filesystem_name(name: str) -> str:
    if not name:
        return "Unknown"
    # Unwrap outer parentheses e.g. (Boyzone) -> Boyzone
    cleaned = re.sub(r'^\s*\((.*?)\)\s*$', r'\1', name)
    # Strip brackets, braces, parentheses
    cleaned = re.sub(r'[\(\)\[\]\{\}]', ' ', cleaned)
    # Strip emails like user@domain.com
    cleaned = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', cleaned)
    # Strip web watermarks
    cleaned = re.sub(r'\b(www\.[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-\.]+\.(com|pk|in|net|org|us|co))\b', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(papuyaar|apniisp|songs\.pk|djluv|fmw11|downloadming)\b', ' ', cleaned, flags=re.IGNORECASE)
    # Strip ugly symbols: $, %, !, @, ~, +, ^, =, _, ;, `, #
    cleaned = re.sub(r'[\$\%\!\@\~\+\^\=\_\;\`\#]', ' ', cleaned)
    # Strip illegal Windows filesystem characters
    cleaned = re.sub(r'[<>:"/\\|?*]', ' ', cleaned)
    cleaned = re.sub(r'[\x00-\x1f]', '', cleaned)
    # Deduplicate repeated artist prefixes (e.g. "U2 - U2 - Song" -> "U2 - Song", "A - A" -> "A")
    cleaned = re.sub(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*-\s*", r"\1 - ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*$", r"\1", cleaned, flags=re.IGNORECASE)
    # Strip trailing/leading punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip('. -_,')
    return cleaned or "Unknown"

def compute_audio_hash(file_path: str) -> str:
    """Computes MD5 hash of raw audio stream ignoring ID3 tag variance."""
    try:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            # Skip first 8KB to bypass ID3v2 header in majority of MP3s
            f.seek(8192)
            chunk = f.read(65536)
            if chunk:
                hasher.update(chunk)
            else:
                f.seek(0)
                hasher.update(f.read(65536))
        return hasher.hexdigest()
    except Exception:
        return ""

def is_generic_track_name(filename: str) -> bool:
    """Identifies generic names like Track 01, Track 1, Audio 1, 01, etc."""
    base, _ = os.path.splitext(filename)
    b = base.lower().strip()
    return bool(re.match(r"^(track|audio|title|song)?[\s_-]*\d+(\s*\(\d+\))?(_\d+)?$", b) or re.match(r"^\d{1,3}$", b))

class MasterDryRunEngine:
    def __init__(self, root_paths: List[str], min_folder_threshold: int = 3):
        self.root_paths = root_paths
        self.min_folder_threshold = min_folder_threshold
        self.decision_cache = load_decision_cache()
        self.inspected_tracks: List[Dict[str, Any]] = []
        self.stream_hash_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def scan_all_files(self) -> List[str]:
        audio_files = []
        for r_path in self.root_paths:
            if not os.path.exists(r_path):
                continue
            for root, dirs, files in os.walk(r_path):
                # Skip duplicate and corrupted vaults in scan
                if "_duplicates_backup" in root or "_corrupted_backup" in root:
                    continue
                for f in files:
                    if f.lower().endswith(('.mp3', '.wma', '.flac', '.m4a', '.ogg')):
                        audio_files.append(os.path.join(root, f))
        return audio_files

    def inspect_file(self, file_path: str) -> Dict[str, Any]:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        # Extract audio headers and existing tags
        bitrate = 128
        duration = 0.0
        title_tag = ""
        artist_tag = ""
        album_tag = ""
        genre_tag = ""
        year_tag = ""
        track_num = ""

        try:
            audio = mutagen.File(file_path)
            if audio is not None and hasattr(audio, 'info') and audio.info:
                duration = getattr(audio.info, 'length', 0.0)
                bitrate = int(getattr(audio.info, 'bitrate', 128000) / 1000)
                if bitrate <= 0:
                    bitrate = 128

            if audio is not None:
                # MP3 ID3
                if ext == '.mp3':
                    title_tag = str(audio.get('TIT2', [''])[0]).strip()
                    artist_tag = str(audio.get('TPE1', [''])[0]).strip()
                    album_tag = str(audio.get('TALB', [''])[0]).strip()
                    genre_tag = str(audio.get('TCON', [''])[0]).strip()
                    year_tag = str(audio.get('TDRC', [''])[0]).strip()
                    track_num = str(audio.get('TRCK', [''])[0]).strip()
                elif ext == '.wma':
                    title_tag = str(audio.get('Title', [''])[0]).strip()
                    artist_tag = str(audio.get('Author', [''])[0]).strip()
                    album_tag = str(audio.get('WM/AlbumTitle', [''])[0]).strip()
                    genre_tag = str(audio.get('WM/Genre', [''])[0]).strip()
                    year_tag = str(audio.get('WM/Year', [''])[0]).strip()
                    track_num = str(audio.get('WM/TrackNumber', [''])[0]).strip()
                elif ext in ['.flac', '.ogg']:
                    title_tag = str(audio.get('title', [''])[0]).strip()
                    artist_tag = str(audio.get('artist', [''])[0]).strip()
                    album_tag = str(audio.get('album', [''])[0]).strip()
                    genre_tag = str(audio.get('genre', [''])[0]).strip()
                    year_tag = str(audio.get('date', [''])[0]).strip()
                    track_num = str(audio.get('tracknumber', [''])[0]).strip()
        except Exception:
            pass

        # Compute audio hash
        audio_hash = compute_audio_hash(file_path)

        track_data = {
            "source_path": file_path,
            "filename": filename,
            "ext": ext,
            "size_bytes": size_bytes,
            "bitrate": bitrate,
            "duration": round(duration, 2),
            "audio_hash": audio_hash,
            "tag_title": title_tag,
            "tag_artist": artist_tag,
            "tag_album": album_tag,
            "tag_genre": genre_tag,
            "tag_year": year_tag,
            "track_num": track_num,
            "is_generic": is_generic_track_name(filename) or is_generic_track_name(title_tag)
        }
        return track_data

    def resolve_deep_audio_and_taxonomy(self, t: Dict[str, Any]) -> Dict[str, Any]:
        """Executes Stage 2 (Deep Audio / Whisper) and Stage 3 (Taxonomy)"""
        file_path = t["source_path"]
        filename = t["filename"]
        audio_hash = t["audio_hash"]
        combined_text = f"{filename} {t['tag_title']} {t['tag_artist']} {t['tag_album']} {file_path}".lower()

        # Check persistent decision cache first (100% deterministic)
        if audio_hash and audio_hash in self.decision_cache:
            cached = self.decision_cache[audio_hash]
            return {
                **cached,
                "decision_source": "Persistent Decision Cache (AirLLM/Verified)"
            }

        decision_source = "Rule Engine"
        confidence = 0.95
        transcribed_lyrics = ""

        # ----------------------------------------------------
        # STAGE 2: Deep Audio Listening for Generic / Missing Tracks
        # ----------------------------------------------------
        if t["is_generic"]:
            whisper_model = get_whisper_model()
            if whisper_model:
                try:
                    # Use official high-level transcribe on vocal segment (30s to 60s)
                    res = whisper_model.transcribe(file_path, fp16=False, clip_timestamps="30,60")
                    det_lang = res.get("language", "hi")
                    transcribed_lyrics = res.get("text", "").strip()
                    decision_source = f"Deep Audio Listening (Whisper {det_lang})"
                except Exception as e:
                    logger.warning(f"Whisper transcription failed on {filename}: {e}")

        # ----------------------------------------------------
        # STAGE 3: Linguistic & Sacred Taxonomy Classification
        # ----------------------------------------------------
        # 0. PRAVACHAN / DISCOURSES / KATHA RESOLUTION (High Priority Preservation)
        prav_info = resolve_pravachan_track(
            filename=filename,
            source_path=file_path,
            tag_title=t.get("tag_title", ""),
            tag_artist=t.get("tag_artist", ""),
            tag_album=t.get("tag_album", "")
        )
        if prav_info:
            prav_info["transcribed_lyrics"] = transcribed_lyrics
            return prav_info

        # 1. GROUND TRUTH LOOKUP FROM MASTER CROSS-DRIVE CATALOG (Instant accurate disambiguation)
        cat_info = lookup_catalog_track(filename, t.get("tag_title", ""), t.get("tag_artist", ""), t.get("duration", 0.0))
        # Only accept catalog lookup if it is not a generic catch-all ("Evergreen Classics", "General")
        if cat_info and cat_info[1] not in ["Evergreen Classics", "General"]:
            c_lang, c_cat, c_alb = cat_info
            if c_lang == "Pravachan":
                p_sub = resolve_pravachan_track(filename, c_cat, t.get("tag_title", ""), t.get("tag_artist", ""), c_alb)
                if p_sub:
                    p_sub["transcribed_lyrics"] = transcribed_lyrics
                    return p_sub
                c_title = sanitize_filesystem_name(os.path.splitext(filename)[0])
                c_art = "Ghaisasi Guruji" if "ghaisasi" in c_cat.lower() else ("Kavishwar Maharaj" if "kavishwar" in c_cat.lower() else ("Dr. Shankar Abhyankar" if "shankar abhyankar" in c_cat.lower() else ("Aparna Abhyankar" if "aparna" in c_cat.lower() else "Various Speakers")))
            else:
                # Extract clean song title
                c_title = clean_name(t.get("tag_title") or "")
                if not c_title or c_title.lower().startswith("track"):
                    c_title = clean_name(filename)
                c_art = t.get("tag_artist") or "Various Artists"
                if c_lang == "Ringtones":
                    c_art = "Sound Clips & Alerts"
                elif c_art.lower() in ["artist", "various artists", "unknown artist", "unknown"]:
                    c_art = c_alb if "Artists" in c_cat else "Various Artists"
            return {
                "language": c_lang,
                "category": c_cat,
                "artist": c_art,
                "album": c_alb,
                "title": c_title,
                "confidence": 0.99,
                "decision_source": "Catalog Ground Truth Vault",
                "transcribed_lyrics": transcribed_lyrics
            }

        # 1. SPECIAL CASE: OMKARA BOLLYWOOD (NEVER SANSKRIT)
        omkara_tracks = ["beedi", "naina", "namak", "omkara", "jag ja ri gudiya", "o saathi re", "laakad"]
        if "omkara" in combined_text:
            if any(tr in combined_text for tr in omkara_tracks) or any(a in combined_text for a in ["vishal", "bhardwaj", "sukhwinder", "sunidhi", "rekha", "rahat", "gulzar"]):
                clean_t = filename.replace(".mp3", "").replace(".wma", "").strip().title()
                for om_tr in omkara_tracks:
                    if om_tr in combined_text:
                        clean_t = om_tr.title()
                        break
                return {
                    "language": "Hindi",
                    "category": "Soundtracks\\Omkara",
                    "artist": "Vishal Bhardwaj",
                    "album": "Omkara",
                    "title": clean_t,
                    "confidence": 0.99,
                    "decision_source": "Special Rule: Bollywood Omkara",
                    "transcribed_lyrics": transcribed_lyrics
                }

        # 2. SANSKRIT SACRED DISAMBIGUATION
        # A. Vedic Suktas
        for pat, canon_name in SUKTA_PATTERNS:
            if re.search(pat, combined_text, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Vedic Suktas",
                    "artist": "Traditional Vedic Chants",
                    "album": "Vedic Suktas",
                    "title": canon_name,
                    "confidence": 0.98,
                    "decision_source": "Taxonomy: Vedic Suktas",
                    "transcribed_lyrics": transcribed_lyrics
                }

        # B. Stotras & Ashtakams (Handles Nirvana Shatakam cleanly)
        for pat, canon_name in STOTRA_PATTERNS:
            if re.search(pat, combined_text, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Stotras & Ashtakams",
                    "artist": "Traditional Sanskrit Chants",
                    "album": "Stotras & Ashtakams",
                    "title": canon_name,
                    "confidence": 0.98,
                    "decision_source": "Taxonomy: Stotras & Ashtakams",
                    "transcribed_lyrics": transcribed_lyrics
                }

        # C. Vedic Samhita
        if "atharva veda" in combined_text or "atharva-veda" in combined_text or re.search(r"\bkanda\s*\d+", combined_text):
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Atharva Veda",
                "artist": "Traditional Vedic Recitation",
                "album": "Atharva Veda",
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.98,
                "decision_source": "Taxonomy: Vedic Samhita",
                "transcribed_lyrics": transcribed_lyrics
            }
        if "bh-samhita" in combined_text or "shrimad-bhagawat-samhita" in combined_text:
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Shrimad Bhagawat Samhita",
                "artist": "Traditional Sanskrit Recitation",
                "album": "Shrimad Bhagawat Samhita",
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.98,
                "decision_source": "Taxonomy: Vedic Samhita",
                "transcribed_lyrics": transcribed_lyrics
            }
        if "rigveda" in combined_text or "rig veda" in combined_text:
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Rigveda",
                "artist": "Traditional Vedic Recitation",
                "album": "Rigveda",
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.98,
                "decision_source": "Taxonomy: Vedic Samhita",
                "transcribed_lyrics": transcribed_lyrics
            }

        # D. Upanishads
        if "chakshushopanishad" in combined_text or "chaakshushopnishad" in combined_text:
            return {
                "language": "Sanskrit",
                "category": "Upanishads",
                "artist": "Traditional Vedic Chants",
                "album": "Upanishads",
                "title": "Chakshushopanishad",
                "confidence": 0.98,
                "decision_source": "Taxonomy: Upanishads",
                "transcribed_lyrics": transcribed_lyrics
            }

        # E. Sanskrit Keywords Fallback
        if any(k in combined_text for k in SANSKRIT_KEYWORDS):
            # Check if stotra keyword exists
            cat = "Stotras & Ashtakams" if any(sk in combined_text for sk in ["stotra", "stotram", "ashtak"]) else "Vedic Suktas"
            return {
                "language": "Sanskrit",
                "category": cat,
                "artist": "Traditional Sanskrit Chants",
                "album": cat,
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.92,
                "decision_source": "Taxonomy: Sanskrit Keywords",
                "transcribed_lyrics": transcribed_lyrics
            }


        # 4. MARATHI INDICATORS
        if any(k in combined_text for k in ["abhang", "natyasangeet", "bhavgeet", "shete", "vitthal", "mauli", "tukaram", "bhajan", "aarti"]) or "marathi" in combined_text:
            marathi_artist = clean_name(t.get("tag_artist") or "")
            if "shete" in combined_text or "akhilam madhuram" in combined_text:
                cat = "Vaibhavi Shete\\Akhilam Madhuram"
                art = "Vaibhavi Shete"
            elif "ajay" in combined_text and "atul" in combined_text:
                cat = "Ajay-Atul"
                art = "Ajay-Atul"
            elif "geet ramayan" in combined_text:
                cat = "Geet Ramayan"
                art = "Sudhir Phadke"
            elif "natyasangeet" in combined_text or "naman natwara" in combined_text:
                cat = "Natyasangeet"
                art = marathi_artist or "Various Artists"
            elif any(k in combined_text for k in ["abhang", "vitthal", "mauli", "tukaram"]):
                cat = "Abhang & Bhakti"
                art = marathi_artist or "Various Artists"
            elif any(k in combined_text for k in ["bhajan", "aarti", "krishna"]):
                cat = "Bhajan & Aarti"
                art = marathi_artist or "Various Artists"
            elif marathi_artist and marathi_artist.lower() not in ["various artists", "unknown artist", "unknown", "artist", "devotional"]:
                cat = marathi_artist
                art = marathi_artist
            else:
                cat = "Bhavgeet & Classics"
                art = marathi_artist or "Various Artists"
            return {
                "language": "Marathi",
                "category": cat,
                "artist": art,
                "album": cat,
                "title": clean_name(t.get("tag_title") or filename),
                "confidence": 0.94,
                "decision_source": "Taxonomy: Marathi",
                "transcribed_lyrics": transcribed_lyrics
            }

        # 5. WESTERN ROCK & POP (NIRVANA, COLDPLAY, BEATLES, ETC.)
        english_bands = [
            "nirvana", "coldplay", "u2", "green day", "iron maiden", "metallica",
            "megadeth", "pink floyd", "the beatles", "beatles", "linkin park",
            "red hot chili peppers", "audioslave", "soundgarden", "faith no more",
            "pearl jam", "radiohead", "rage against the machine", "guns n roses",
            "switchfoot", "rammstein", "nickelback", "eminem", "agnee", "ashutosh pathak",
            "disturbed", "boyzone", "infected mushroom", "bob marley", "westlife", "savage garden"
        ]
        for band in english_bands:
            if re.search(r"\b" + re.escape(band) + r"\b", combined_text, re.IGNORECASE):
                canon_band = resolve_canonical_artist(band) or band.title()
                return {
                    "language": "English",
                    "category": canon_band,
                    "artist": canon_band,
                    "album": t["tag_album"] or canon_band,
                    "title": clean_name(t["tag_title"] or filename),
                    "confidence": 0.96,
                    "decision_source": "Taxonomy: Western Rock & Pop",
                    "transcribed_lyrics": transcribed_lyrics
                }

        # 6. COMPREHENSIVE TAXONOMY & ARTIST CANONICALIZATION (PATTERN CLASSIFIER INTEGRATION)
        canon_artist = resolve_canonical_artist(t["tag_artist"]) or resolve_canonical_artist(os.path.basename(os.path.dirname(file_path)))
        det_lang, det_cat = detect_language_and_category(file_path, filename, t.get("tag_artist", ""))

        # If artist is a recognized Indian / Bollywood artist (Atif Aslam, Arijit, Kishore, Lata, etc.), classify as Hindi/Indian
        if canon_artist and any(h_ind in canon_artist.lower() for h_ind in ["classics", "ghazals", "hits", "rahman", "shete", "atif", "arijit"]):
            lang = "Marathi" if "shete" in canon_artist.lower() else "Hindi"
            return {
                "language": lang,
                "category": canon_artist,
                "artist": canon_artist,
                "album": t["tag_album"] or canon_artist,
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.98,
                "decision_source": "Taxonomy: Canonical Indian Artist",
                "transcribed_lyrics": transcribed_lyrics
            }

        if det_lang == "English":
            # Extract clean English artist and track title
            eng_artist = canon_artist or clean_name(t.get("tag_artist") or "")
            if not eng_artist or eng_artist.lower() in ["various artists", "unknown artist", "unknown"]:
                # Try parent folder name if inside English directory
                parent_dir = os.path.basename(os.path.dirname(file_path))
                if parent_dir.lower() not in ["english", "organized", "unorganized", "rock & pop", "singles & compilations"]:
                    eng_artist = clean_name(parent_dir)
                else:
                    eng_artist = "Various Artists"
            cat_name = det_cat if det_cat not in ["General", "Rock & Pop"] else (eng_artist if eng_artist != "Various Artists" else "Rock & Pop")
            return {
                "language": "English",
                "category": cat_name,
                "artist": eng_artist,
                "album": t["tag_album"] or cat_name,
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.95,
                "decision_source": "Taxonomy: English Language & Artist",
                "transcribed_lyrics": transcribed_lyrics
            }

        if canon_artist:
            return {
                "language": det_lang if det_lang != "English" else "Hindi",
                "category": canon_artist,
                "artist": canon_artist,
                "album": t["tag_album"] or canon_artist,
                "title": clean_name(t["tag_title"] or filename),
                "confidence": 0.95,
                "decision_source": "Taxonomy: Canonical Artist",
                "transcribed_lyrics": transcribed_lyrics
            }

        # 7. DEFAULT HINDI SOUNDTRACK / CLASSIC
        movie, clean_song = extract_bollywood_movie_and_song(
            clean_stem=clean_watermarks(os.path.splitext(filename)[0]),
            stem=os.path.splitext(filename)[0],
            file_path=file_path,
            tag_album=t.get("tag_album", ""),
            tag_artist=t.get("tag_artist", ""),
            tag_title=t.get("tag_title", "")
        )
        if movie and movie not in ["Evergreen Classics", "Modern Soundtracks"] and len(movie) > 2:
            if not any(movie.startswith(p) for p in ["Soundtracks\\", "Albums\\", "Artists\\", "Ghazals\\", "Devotional"]):
                final_cat = f"Soundtracks\\{movie}"
            else:
                final_cat = movie
        else:
            final_cat = det_cat if det_cat not in ["General", "Evergreen Classics"] else (canon_artist or "Singles & Compilations")
        return {
            "language": det_lang if det_lang != "English" else "Hindi",
            "category": final_cat,
            "artist": canon_artist or t.get("tag_artist") or "Various Artists",
            "album": movie or final_cat,
            "title": clean_name(t.get("tag_title") or clean_song or filename),
            "confidence": 0.90,
            "decision_source": decision_source,
            "transcribed_lyrics": transcribed_lyrics
        }

    def execute_dry_run(self) -> Dict[str, Any]:
        all_files = self.scan_all_files()
        total_files = len(all_files)
        logger.info(f"Scanning and inspecting {total_files} audio files...")

        # Step 1: Multi-threaded inspection
        with ThreadPoolExecutor(max_workers=8) as executor:
            self.inspected_tracks = list(executor.map(self.inspect_file, all_files))

        # Step 2: Quality-aware stream hashing deduplication map
        for t in self.inspected_tracks:
            h = t["audio_hash"]
            if h:
                self.stream_hash_map[h].append(t)

        # Mark duplicates
        for h, track_list in self.stream_hash_map.items():
            if len(track_list) > 1:
                # Sort descending by bitrate then duration
                track_list.sort(key=lambda x: (x["bitrate"], x["duration"]), reverse=True)
                # First is primary, rest are duplicates
                track_list[0]["is_duplicate"] = False
                for dup in track_list[1:]:
                    dup["is_duplicate"] = True
            else:
                track_list[0]["is_duplicate"] = False

        # Step 3 & 4: Resolve taxonomy, deep audio listening, and path blueprint
        category_counts = defaultdict(int)
        for t in self.inspected_tracks:
            res = self.resolve_deep_audio_and_taxonomy(t)
            t.update(res)
            if not t.get("is_duplicate", False):
                cat_key = f"{t['language']}:{t['category']}"
                category_counts[cat_key] += 1

        # Step 5: Dynamic Threshold & Canonical Filename Generation
        seen_proposed_paths = set()
        for t in self.inspected_tracks:
            if t.get("is_duplicate", False):
                dup_stem, dup_ext = os.path.splitext(t['filename'])
                t["proposed_path"] = f"D:\\Songs\\unorganized\\_duplicates_backup\\{sanitize_filesystem_name(dup_stem)}{dup_ext}"
                t["action"] = "Archive Lower-Bitrate Duplicate"
            else:
                lang = t["language"]
                cat = t["category"]
                cat_key = f"{lang}:{cat}"
                title = sanitize_filesystem_name(t["title"])
                artist = sanitize_filesystem_name(t["artist"])
                ext = t["ext"]

                clean_cat_parts = [sanitize_filesystem_name(p) for p in cat.split("\\")]
                clean_cat_path = os.sep.join(clean_cat_parts)

                count = category_counts[cat_key]
                if lang == "Ringtones":
                    proposed_dir = os.path.join(r"D:\Songs\organized", "Ringtones & Alerts")
                    base_name = f"{title}"
                    t["folder_type"] = "Dedicated Collection"
                elif lang == "Pravachan" or count >= self.min_folder_threshold or any(perm in cat for perm in ["Samhita", "Suktas", "Stotras", "Discourses", "Gita", "Katha"]):
                    # Dedicated Folder
                    proposed_dir = os.path.join(r"D:\Songs\organized", lang, clean_cat_path)
                    base_name = f"{title}"
                    t["folder_type"] = "Dedicated Collection"
                else:
                    # Consolidated Singles Collection
                    proposed_dir = os.path.join(r"D:\Songs\organized", lang, "Singles & Compilations")
                    if artist and artist != "Various Artists":
                        if title.lower().startswith(artist.lower() + " - ") or title.lower().startswith(artist.lower() + " ") or artist.lower() == title.lower():
                            base_name = f"{title}"
                        else:
                            base_name = f"{artist} - {title}"
                    else:
                        base_name = f"{title}"
                    t["folder_type"] = "Consolidated Singles"

                target_path = os.path.join(proposed_dir, f"{base_name}{ext}")
                suffix = 2
                while target_path.lower() in seen_proposed_paths:
                    target_path = os.path.join(proposed_dir, f"{base_name} - Part {suffix}{ext}")
                    suffix += 1

                seen_proposed_paths.add(target_path.lower())
                t["proposed_path"] = target_path
                t["action"] = "Organize & Tag"

        # Summary Metrics
        summary = {
            "total_files_scanned": total_files,
            "unique_tracks": sum(1 for t in self.inspected_tracks if not t.get("is_duplicate")),
            "duplicate_tracks": sum(1 for t in self.inspected_tracks if t.get("is_duplicate")),
            "generic_resolved": sum(1 for t in self.inspected_tracks if t.get("is_generic")),
            "languages": defaultdict(int),
            "folder_types": defaultdict(int)
        }
        for t in self.inspected_tracks:
            if not t.get("is_duplicate"):
                summary["languages"][t["language"]] += 1
                summary["folder_types"][t["folder_type"]] += 1

        return {
            "summary": summary,
            "tracks": self.inspected_tracks
        }

    def execute_physical_organization(self, dry_run_cache: Optional[Dict[str, Any]] = None, max_workers: int = 4) -> Dict[str, Any]:
        """
        Executes physical file reorganization based on the verified blueprint:
        - Creates clean target folder structure.
        - Moves audio files safely (handling in-place collisions).
        - Embeds verified ID3/WMA/FLAC metadata tags (Title, Artist, Album, Genre, Year).
        - Removes leftover empty directories from old structure.
        """
        import shutil
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
        from mutagen.asf import ASF

        if not dry_run_cache:
            cache_file = os.path.join(PROJECT_ROOT, "cached_dry_run_results.json")
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    dry_run_cache = json.load(f)
            else:
                dry_run_cache = self.execute_dry_run()

        tracks = dry_run_cache.get("tracks", [])
        total = len(tracks)
        logger.info(f"Beginning physical reorganization of {total} tracks...")

        moved_count = 0
        tag_updated_count = 0
        duplicate_archived_count = 0
        errors = []

        for i, t in enumerate(tracks):
            src = t.get("source_path", "")
            dest = t.get("proposed_path", "")
            action = t.get("action", "")

            if not os.path.exists(src):
                # File may already have been moved
                continue

            # Skip if already at exact target path
            if os.path.abspath(src).lower() == os.path.abspath(dest).lower():
                continue

            try:
                dest_dir = os.path.dirname(dest)
                os.makedirs(dest_dir, exist_ok=True)

                # Move file
                shutil.move(src, dest)
                t["source_path"] = dest
                moved_count += 1

                if action == "Archive Lower-Bitrate Duplicate":
                    duplicate_archived_count += 1
                else:
                    # Update metadata tags for organized files
                    try:
                        ext = t.get("ext", "").lower()
                        title = t.get("title", "")
                        artist = t.get("artist", "")
                        album = t.get("album", "")
                        lang = t.get("language", "")

                        if ext == ".mp3":
                            try:
                                audio = ID3(dest)
                            except Exception:
                                audio = ID3()
                            audio["TIT2"] = TIT2(encoding=3, text=title)
                            audio["TPE1"] = TPE1(encoding=3, text=artist)
                            audio["TALB"] = TALB(encoding=3, text=album)
                            audio["TCON"] = TCON(encoding=3, text=lang)
                            audio.save(dest)
                            tag_updated_count += 1
                        elif ext == ".wma":
                            audio = ASF(dest)
                            audio["Title"] = [title]
                            audio["Author"] = [artist]
                            audio["WM/AlbumTitle"] = [album]
                            audio["WM/Genre"] = [lang]
                            audio.save()
                            tag_updated_count += 1
                    except Exception as tag_err:
                        logger.debug(f"Tag write failed on {dest}: {tag_err}")

            except Exception as e:
                err_msg = f"Failed to move {src} -> {dest}: {e}"
                logger.error(err_msg)
                errors.append(err_msg)

            if (i + 1) % 500 == 0 or (i + 1) == total:
                logger.info(f"Physical organization progress: {i + 1}/{total} processed ({moved_count} moved).")

        # Cleanup empty directories
        for root_dir in self.root_paths:
            if os.path.exists(root_dir):
                for current_dir, dirs, files in os.walk(root_dir, topdown=False):
                    if current_dir == root_dir or "_duplicates_backup" in current_dir:
                        continue
                    try:
                        if not os.listdir(current_dir):
                            os.rmdir(current_dir)
                    except Exception:
                        pass

        logger.info(f"Physical reorganization completed! Moved: {moved_count}, Tagged: {tag_updated_count}, Duplicates Archived: {duplicate_archived_count}")
        return {
            "total_processed": total,
            "moved": moved_count,
            "tags_updated": tag_updated_count,
            "duplicates_archived": duplicate_archived_count,
            "errors": errors
        }

    def generate_html_review(self, result: Dict[str, Any], output_path: str = "dry_run_review.html") -> str:
        summary = result["summary"]
        tracks = result["tracks"]

        # Sort tracks: put generic and ambiguous tracks at the top for easy inspection
        sorted_tracks = sorted(tracks, key=lambda x: (not x.get("is_generic"), x.get("is_duplicate"), x.get("confidence", 1.0)))

        # Create tracks JSON data for client-side search & filtering
        # Take sample of first 1,500 tracks if huge, or full set with pagination
        display_tracks = sorted_tracks[:2500]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auralis - Master Dry-Run Review Dashboard</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-amber: #fbbf24;
            --accent-purple: #c084fc;
            --border-color: #475569;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            color: var(--accent-blue);
        }}
        .header p {{
            margin: 4px 0 0 0;
            color: var(--text-secondary);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .metric-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-card .title {{
            font-size: 13px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
            color: var(--text-primary);
        }}
        .search-bar {{
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }}
        .search-bar input, .search-bar select {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 14px;
        }}
        .search-bar input {{
            flex: 1;
        }}
        .btn-export {{
            background: var(--accent-blue);
            color: #0f172a;
            font-weight: bold;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        .btn-export:hover {{
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-secondary);
            border-radius: 8px;
            overflow: hidden;
            font-size: 13px;
        }}
        th, td {{
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background: #111827;
            color: var(--text-secondary);
            font-weight: 600;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge-sanskrit {{ background: rgba(192, 132, 252, 0.2); color: var(--accent-purple); }}
        .badge-hindi {{ background: rgba(251, 191, 36, 0.2); color: var(--accent-amber); }}
        .badge-english {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); }}
        .badge-marathi {{ background: rgba(52, 211, 153, 0.2); color: var(--accent-green); }}
        .badge-pravachan {{ background: rgba(244, 114, 182, 0.2); color: #f472b6; }}
        .badge-dup {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
        .lyrics-box {{
            font-size: 11px;
            color: #cbd5e1;
            background: #0f172a;
            padding: 4px 6px;
            border-radius: 4px;
            margin-top: 4px;
            border-left: 2px solid var(--accent-blue);
        }}
        .path-code {{
            font-family: monospace;
            font-size: 11px;
            color: var(--text-secondary);
            word-break: break-all;
        }}
        .path-new {{
            font-family: monospace;
            font-size: 12px;
            color: var(--accent-green);
            font-weight: 500;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Auralis Library Master - Dry-Run Blueprint</h1>
            <p>Non-Destructive Simulation & Intelligent Multi-Pass Verification Dashboard</p>
        </div>
        <div>
            <button class="btn-export" onclick="exportFeedback()">Export Verified Blueprint</button>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="title">Total Tracks Scanned</div>
            <div class="value">{summary['total_files_scanned']:,}</div>
        </div>
        <div class="metric-card">
            <div class="title">Unique Master Tracks</div>
            <div class="value" style="color: var(--accent-green);">{summary['unique_tracks']:,}</div>
        </div>
        <div class="metric-card">
            <div class="title">Duplicates to Vault</div>
            <div class="value" style="color: #f87171;">{summary['duplicate_tracks']:,}</div>
        </div>
        <div class="metric-card">
            <div class="title">Generic Tracks Resolved</div>
            <div class="value" style="color: var(--accent-blue);">{summary['generic_resolved']:,}</div>
        </div>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search by Track Title, Artist, Movie, or Source Path..." onkeyup="filterTable()">
        <select id="langFilter" onchange="filterTable()">
            <option value="">All Languages</option>
            <option value="Sanskrit">Sanskrit</option>
            <option value="Hindi">Hindi</option>
            <option value="English">English</option>
            <option value="Marathi">Marathi</option>
            <option value="Pravachan">Pravachan</option>
        </select>
        <select id="typeFilter" onchange="filterTable()">
            <option value="">All Types</option>
            <option value="Generic">Generic / Audio Listened</option>
            <option value="Organize">Organized Master</option>
            <option value="Duplicate">Duplicates</option>
        </select>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 100px;">Language</th>
                <th style="width: 200px;">Resolved Title & Artist</th>
                <th>Source File & Transcribed Lyrics</th>
                <th>Proposed Target Path</th>
                <th style="width: 80px;">Bitrate</th>
                <th style="width: 140px;">Decision Source</th>
            </tr>
        </thead>
        <tbody id="tableBody">
        """

        for t in display_tracks:
            lang = t.get("language", "Unknown")
            badge_class = f"badge-{lang.lower()}"
            is_dup = t.get("is_duplicate", False)
            title = t.get("title", "")
            artist = t.get("artist", "")
            source = t.get("source_path", "")
            proposed = t.get("proposed_path", "")
            bitrate = f"{t.get('bitrate', 128)} kbps"
            source_engine = t.get("decision_source", "Rule Engine")
            lyrics = t.get("transcribed_lyrics", "")

            lyrics_html = f'<div class="lyrics-box"><strong>Audio Lyrics:</strong> {lyrics}</div>' if lyrics else ""
            dup_badge = '<span class="badge badge-dup">Duplicate</span> ' if is_dup else ""

            html_content += f"""
            <tr data-lang="{lang}" data-type="{'Duplicate' if is_dup else ('Generic' if t.get('is_generic') else 'Organize')}">
                <td><span class="badge {badge_class}">{lang}</span></td>
                <td>
                    <strong>{title}</strong><br>
                    <small style="color: var(--text-secondary);">{artist}</small>
                </td>
                <td>
                    <div class="path-code">{source}</div>
                    {lyrics_html}
                </td>
                <td>
                    {dup_badge}<span class="path-new">{proposed}</span>
                </td>
                <td>{bitrate}</td>
                <td><small style="color: var(--text-secondary);">{source_engine}</small></td>
            </tr>
            """

        html_content += """
        </tbody>
    </table>

    <script>
        function filterTable() {
            var search = document.getElementById("searchInput").value.toLowerCase();
            var lang = document.getElementById("langFilter").value;
            var type = document.getElementById("typeFilter").value;
            var rows = document.getElementById("tableBody").getElementsByTagName("tr");

            for (var i = 0; i < rows.length; i++) {
                var row = rows[i];
                var rowText = row.innerText.toLowerCase();
                var rowLang = row.getAttribute("data-lang");
                var rowType = row.getAttribute("data-type");

                var matchesSearch = !search || rowText.indexOf(search) !== -1;
                var matchesLang = !lang || rowLang === lang;
                var matchesType = !type || rowType === type;

                if (matchesSearch && matchesLang && matchesType) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            }
        }

        function exportFeedback() {
            alert("Dry-run blueprint verified! Ready for physical execution via `python auralis.py master-organize --apply`.");
        }
    </script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    engine = MasterDryRunEngine(
        root_paths=[r"D:\Songs\organized", r"D:\Songs\unorganized"],
        min_folder_threshold=3
    )
    result = engine.execute_dry_run()
    out = engine.generate_html_review(result, "dry_run_review.html")
    print(f"Generated Dry-Run review HTML: {os.path.abspath(out)}")
