"""
Auralis - Intelligent Pattern Classifier & Track Normalizer
High-speed rule-based classifier that extracts Language, Category/Artist, Album,
and canonical Song Title from diverse music library naming patterns.
Includes seamless local LLM fallback for ambiguous tracks.
"""

import os
import re
from typing import Dict, Any, Tuple, Optional
from src.engine.embedded_intelligence import resolve_canonical_artist

# Regex to strip website watermarks, quality badges, and rip tags
JUNK_PATTERNS = [
    r"\[.*?djluv.*?\]", r"\[.*?songs\.pk.*?\]", r"\[.*?bindassbuzz.*?\]",
    r"\[.*?mp3.*?\]", r"\[.*?128kbps.*?\]", r"\[.*?320kbps.*?\]", r"\[.*?256kbps.*?\]",
    r"\[.*?kbps.*?\]", r"\[.*?rip.*?\]", r"\[.*?edition.*?\]", r"\[.*?medley.*?\]",
    r"\[.*?xdr.*?\]", r"\[.*?download.*?\]",
    r"www\.[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,4}", r"\(.*?mp3.*?\)", r"_www\.[a-zA-Z0-9_\-\.]+",
    r"\[.*?\]"  # Any remaining bracketed tags
]

GENERIC_PATTERN = re.compile(
    r"^(track\s*\d+|\d{1,3}|audio\s*track\s*\d+|title\s*\d+|song\s*\d+|untitled.*)\.[a-zA-Z0-9]+$",
    re.IGNORECASE
)

SANSKRIT_KEYWORDS = [
    "suktam", "sukta", "stotram", "stotra", "ashtakam", "ashtak", "vedic",
    "mantra", "rudram", "shanti path", "gayatri", "atharvashirsha"
]

MARATHI_KEYWORDS = [
    "abhang", "natyasangeet", "natya sangeet", "lavani", "bhavgeet", "gajar",
    "mauli", "pandharpur", "tukaram", "dnyaneshwar", "vitthal", "shete"
]

PRAVACHAN_KEYWORDS = [
    "pravachan", "katha", "adhyay", "discourse", "updesh", "day 1", "day 2",
    "day 3", "day 4", "day 5", "day 6", "day 7", "day 8", "day 9", "day 10"
]

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

def is_generic_track(filename: str) -> bool:
    """Detects generic filenames like Track1.mp3, 001.wma, Track 02.mp3."""
    return bool(GENERIC_PATTERN.match(filename.strip()))

def clean_watermarks(text: str) -> str:
    """Strips web promotional watermarks and normalizes spacing."""
    cleaned = text
    for pat in JUNK_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("_", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned

def clean_name(s: str) -> str:
    """Cleans names, removes leading track numbers, brackets, stray numbers, and domain leftovers."""
    if not s:
        return ""
    # Strip web watermarks
    s = clean_watermarks(s)
    # Remove leading track numbers like '01 - ', '05 ', '072 '
    s = re.sub(r"^\d+[\s\.\-_]*", "", s)
    # Strip bracketed content like [320kbps], (Official), [1979]
    s = re.sub(r"\[.*?\]", "", s)
    # Strip full parentheses wrappers like (Boyzone) -> Boyzone
    s = re.sub(r"^\s*\((.*?)\)\s*$", r"\1", s)
    # Remove all remaining parentheses, brackets, braces
    s = re.sub(r"[\(\)\[\]\{\}]", " ", s)
    # Strip domain extensions and rip watermarks
    s = re.sub(r"\b(com|pk|in|net|org|us|info|co)\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(apniisp|pakheaven|papuyaar|fmw11|songs\.pk|djluv)\b", "", s, flags=re.IGNORECASE)
    # Filter stray numbers unless part of genuine titles (e.g. Taxi No 9211, 1942, 420, U2)
    tokens = s.split()
    clean_tokens = []
    for tok in tokens:
        if tok.isdigit():
            if tok in ["9211", "1942", "420", "36", "84", "2", "3"]:
                clean_tokens.append(tok)
            # Drop random numbers like 072, 2011, 171106, 83624 etc.
        else:
            clean_tokens.append(tok)
    s = " ".join(clean_tokens)
    # Remove special characters except hyphens, ampersands, apostrophes
    s = re.sub(r"[^a-zA-Z0-9\s\-&\'\.]", " ", s)
    # Deduplicate repeated artist prefixes (e.g. "U2 - U2 - Song" -> "U2 - Song")
    s = re.sub(r"^([A-Za-z0-9\s&']+?)\s*-\s*\1\s*-\s*", r"\1 - ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip(" ._-\\/")
    return s.strip().title()

def is_valid_album(alb: str) -> bool:
    """Checks if an album tag contains genuine album text vs placeholder or domain junk."""
    if not alb or not alb.strip():
        return False
    lower = alb.strip().lower()
    if lower in ["<unknown>", "title", "album", "unknown album", "hindi", "new", "audio", "track", "evergreen classics", "modern soundtracks", "general", "various artists"]:
        return False
    if "unknown album" in lower or "evergreen classics" in lower or "modern soundtracks" in lower:
        return False
    if any(dom in lower for dom in [".com", ".pk", ".in", ".net", ".us", ".org", "www.", "http", "mp3", "fmw", "apniisp", "pakheaven", "papuyaar", "megablast"]):
        return False
    if re.match(r"^\d+$", lower) or "1/1/2001" in lower or len(lower) <= 2:
        return False
    return True

def detect_language_and_category(file_path: str, filename: str, artist: str = "") -> Tuple[str, str]:
    """
    Determines primary Language (Hindi, Marathi, English, Sanskrit, Pravachan)
    and initial Category based on folder structure, keywords, and path clues.
    """
    path_lower = file_path.lower()
    fn_lower = filename.lower()
    combined = f"{fn_lower} {artist.lower()} {path_lower}"

    # 1. SPECIAL CASE: OMKARA BOLLYWOOD FILM (NEVER CLASSIFY AS SANSKRIT)
    omkara_tracks = ["beedi", "naina", "namak", "omkara", "jag ja ri gudiya", "o saathi re", "laakad"]
    if "omkara" in combined:
        if any(t in combined for t in omkara_tracks) or any(a in combined for a in ["vishal", "bhardwaj", "sukhwinder", "sunidhi", "rekha", "rahat", "gulzar"]):
            return "Hindi", "Soundtracks\\Omkara"
        elif "beedi" in fn_lower or "namak" in fn_lower or "naina" in fn_lower:
            return "Hindi", "Soundtracks\\Omkara"

    # 2. SANSKRIT DISCRIMINATION
    # A. Vedic Suktas
    for pat, canon_name in SUKTA_PATTERNS:
        if re.search(pat, combined, re.IGNORECASE):
            return "Sanskrit", "Vedic Suktas"

    # B. Stotras & Ashtakams (Nirvana Shatakam matches here, preventing English band trap)
    for pat, canon_name in STOTRA_PATTERNS:
        if re.search(pat, combined, re.IGNORECASE):
            return "Sanskrit", "Stotras & Ashtakams"

    # C. Vedic Samhita & Parayanam
    if "atharva veda" in combined or "atharva-veda" in combined or re.search(r"\bkanda\s*\d+", combined, re.IGNORECASE):
        return "Sanskrit", "Vedic Samhita\\Atharva Veda"
    if "bh-samhita" in combined or "shrimad-bhagawat-samhita" in combined:
        return "Sanskrit", "Vedic Samhita\\Shrimad Bhagawat Samhita"

    # D. Upanishads
    if "chaakshushopnishad" in combined or "chakshushopanishad" in combined:
        return "Sanskrit", "Upanishads"

    # E. Generic Sanskrit path keywords if not caught above
    sanskrit_path_keys = ["vidik sukta", "vaidik sukta", "sanskrit", "bh-samhita", "bh-mahatmya", "sukta-sangraha"]
    sanskrit_fn_markers = ["bh-samhita", "bh-mahatmya", "suktam", "sukta", "stotram", "stotra", "ashtakam", "ashtak", "atharvashirsha"]
    if any(k in path_lower for k in sanskrit_path_keys) or any(k in fn_lower for k in sanskrit_fn_markers) or any(k in combined for k in SANSKRIT_KEYWORDS):
        return "Sanskrit", "Vedic Suktas"

    # 3. PRAVACHAN & KATHA MARKERS
    is_pravachan_path = any(p in path_lower for p in [r"\pravachan", "discourse", "katha-ghaisasi", "shankar abhyankar"])
    has_pravachan_kw = any(k in combined for k in PRAVACHAN_KEYWORDS)
    if (is_pravachan_path or has_pravachan_kw) and not any(m in combined for m in ["talaash", "bollywood", "soundtrack"]):
        if "ghaisasi" in combined:
            return "Pravachan", "Bhagwat Katha\\Ghaisasi Guruji"
        elif "kavishwar" in combined:
            return "Pravachan", "Bhagwat Katha\\Kavishwar Maharaj"
        elif "abhyankar" in combined or "purushottam" in combined or "gita" in combined:
            spk = "Aparna Abhyankar" if "aparna" in combined else "Shankar Abhyankar"
            return "Pravachan", f"Bhagavad Gita\\{spk}"
        return "Pravachan", "Discourses & Katha"

    # 4. WESTERN ROCK / METAL / POP MARKERS (STRICT WORD BOUNDARIES)
    english_keys = [
        "nirvana", "coldplay", "u2", "green day", "iron maiden", "metallica",
        "audioslave", "bob marley", "pitbull", "opeth", "chainsmokers", "beatles",
        "dream theater", "pink floyd", "linkin park", "switchfoot", "rammstein",
        "nickelback", "eminem", "yellowcard", "system of a down", "red hot chili peppers",
        "avril lavigne", "enrique iglesias", "rihanna", "akon", "shakira", "lady gaga",
        "katy perry", "madonna", "bon jovi", "bryan adams", "scorpions", "aerosmith",
        "david guetta", "tiesto", "guns n roses", "guns and roses", "sum 41", "pantera",
        "disturbed", "boyzone", "infected mushroom", "westlife", "savage garden"
    ]
    art_canon = resolve_canonical_artist(artist)
    if art_canon and not any(h_ind in art_canon.lower() for h_ind in ["classics", "ghazals", "hits", "rahman", "shete"]):
        return "English", "Rock & Pop"
    for eng in english_keys:
        if re.search(r"\b" + re.escape(eng) + r"\b", combined, re.IGNORECASE):
            return "English", eng.title()

    # 5. MARATHI INDICATORS
    if r"\marathi" in path_lower or any(k in combined for k in MARATHI_KEYWORDS):
        if "shete" in combined or "akhilam madhuram" in combined:
            return "Marathi", "Vaibhavi Shete\\Akhilam Madhuram"
        elif "natyasangeet" in combined or "naman natwara" in combined:
            return "Marathi", "Natyasangeet"
        elif "abhang" in combined or "vitthal" in combined or "mauli" in combined:
            return "Marathi", "Abhang & Bhakti"
        return "Marathi", "Bhavgeet & Classics"

    # 6. EXISTING TOP-LEVEL FOLDER INDICATORS (Fallback only)
    if r"\english" in path_lower:
        return "English", "General"
    if r"\hindi" in path_lower:
        return "Hindi", "General"

    # 7. DEFAULT INDIAN FILM INDICATORS
    if "=" in filename or any(k in combined for k in ["lata", "rafi", "kishore", "mukesh", "arijit", "shreya"]):
        return "Hindi", "Bollywood Classics"

    return "Hindi", "General"

def extract_bollywood_movie_and_song(
    clean_stem: str,
    stem: str,
    file_path: str,
    tag_album: str,
    tag_artist: str,
    tag_title: str
) -> Tuple[str, str]:
    """
    Extracts the movie/album name and clean song title for Bollywood tracks
    to ensure consolidated 'Hindi / [Artist_or_Movie]' hierarchy.
    """
    movie = ""
    song = ""

    # 1. MOVIE = SONG TITLE (Highest Priority - exact encoding in Hindi/Old filenames)
    if "=" in clean_stem:
        parts = clean_stem.split("=", 1)
        movie = clean_name(parts[0])
        song = clean_name(parts[1])

    # 2. Triple or double underscore: MOVIE___SONG
    elif "___" in stem or "__" in stem:
        sep = "___" if "___" in stem else "__"
        parts = stem.split(sep, 1)
        movie = clean_name(parts[0])
        song = clean_name(parts[1])

    # 3. High-Confidence ID3 Album Tag if valid (anchors proper movie album name e.g. "Yeh Jawaani Hai Deewani", "Lootera")
    elif is_valid_album(tag_album):
        movie = clean_name(tag_album)

    # 3. Parentheses/braces: Song (Movie) or Song {Movie}
    elif re.search(r"^(.*?)\s*[\(\{]([^\)\}]+)[\)\}]\s*$", clean_stem):
        m_obj = re.search(r"^(.*?)\s*[\(\{]([^\)\}]+)[\)\}]\s*$", clean_stem)
        if m_obj:
            s_cand = clean_name(m_obj.group(1))
            m_cand = clean_name(m_obj.group(2))
            # If the text in parentheses is a featured artist (e.g. '& Busta Rhymes' or 'Feat. Akon')
            if m_cand.startswith("&") or m_cand.lower().startswith("feat") or m_cand.lower().startswith("ft."):
                feat_artist = re.sub(r"^(&|feat\.?|ft\.?)\s*", "", m_cand, flags=re.IGNORECASE).strip()
                canon_feat = resolve_canonical_artist(feat_artist)
                movie = clean_name(tag_album) if is_valid_album(tag_album) else (canon_feat or "Evergreen Classics")
                song = f"{s_cand} ({m_cand})"
            elif m_cand.lower() in ["rafi", "mukesh", "lata", "kishore", "asha", "remix", "sad"]:
                movie = clean_name(tag_album) if is_valid_album(tag_album) else "Evergreen Classics"
                song = s_cand
            else:
                movie = m_cand
                song = s_cand

    # 4. Spaced dash: 04 - Movie - Song or Movie - Song or Song - Artist/Movie
    elif " - " in clean_stem:
        parts = [p.strip() for p in clean_stem.split(" - ") if p.strip()]
        if len(parts) >= 3 and re.match(r"^\d+$", parts[0]):
            p1_canon = resolve_canonical_artist(parts[1])
            p2_canon = resolve_canonical_artist(parts[2])
            if movie:
                # If movie already anchored (e.g. from ID3 album), extract clean song title
                song = clean_name(parts[1]) if parts[2].lower() in ["downloadming.se", "mp3", "djluv"] else clean_name(parts[2])
            elif p2_canon and not p1_canon:
                movie = p2_canon
                song = clean_name(parts[1])
            else:
                movie = p1_canon or clean_name(parts[1])
                song = clean_name(parts[2])
        elif len(parts) >= 2:
            p0 = clean_name(parts[0])
            p1 = clean_name(parts[1])
            p0_canon = resolve_canonical_artist(p0)
            p1_canon = resolve_canonical_artist(p1)
            if movie:
                song = p0 if p1.lower() in ["downloadming.se", "mp3", "djluv"] else p1
            elif p1_canon and not p0_canon:
                movie = p1_canon
                song = p0
            else:
                movie = p0_canon or p0
                song = p1

    # 5. Double dash or tight dash: Movie--Song or Movie-Song or Song-Movie/Artist
    elif "--" in clean_stem:
        parts = clean_stem.split("--", 1)
        movie = clean_name(parts[0])
        song = clean_name(parts[1])
    elif "all-time" in clean_stem.lower():
        movie = "All-Time Hits Compilations"
        song = clean_name(clean_stem)
    elif "-" in clean_stem and not clean_stem.startswith("-"):
        parts = clean_stem.split("-", 1)
        p0 = clean_name(parts[0])
        p1 = clean_name(parts[1])
        p0_canon = resolve_canonical_artist(p0)
        p1_canon = resolve_canonical_artist(p1)
        if p1_canon and not p0_canon:
            # Inverted: e.g. "Aa Bhi Ja Aa Bhi Ja-Lucky ali" -> Lucky Ali Hits, Aa Bhi Ja Aa Bhi Ja
            movie = p1_canon
            song = p0
        elif parts[0].strip().lower() not in ["all", "part", "vol", "track"]:
            # Check if p0 is a known movie or if p1 is a single-word movie/artist (e.g. "Aane Wala Pal -Golmaal", "Aa bhi ja- Sur")
            if len(p1.split()) <= 2 and len(p0.split()) > len(p1.split()):
                movie = p1
                song = p0
            else:
                movie = p0
                song = p1

    # 6. ID3 Album Tag if valid
    if not movie and is_valid_album(tag_album):
        movie = clean_name(tag_album)
        song = clean_name(tag_title) if tag_title and not tag_title.lower().startswith("track") else clean_name(clean_stem)

    # 7. Directory clues
    if not movie or not movie.strip():
        if r"\mukesh" in file_path.lower():
            movie = "Mukesh Classics"
        elif r"\pankaj udas" in file_path.lower():
            movie = "Pankaj Udhas Ghazals"
        elif r"\youtube-playlists" in file_path.lower():
            movie = "Playlist Hits"
        elif r"\new" in file_path.lower():
            movie = "Modern Soundtracks"
        else:
            movie = "Evergreen Classics"

    if len(movie) <= 2 or movie.lower() in ["unknown", "title", "album", "audio", "various artists", "hindi"]:
        movie = "Modern Soundtracks" if r"\new" in file_path.lower() else "Evergreen Classics"

    if not song or not song.strip():
        song = clean_name(tag_title) if tag_title and not tag_title.lower().startswith("track") else clean_name(clean_stem)

    return movie, song

def parse_track_details(
    file_path: str,
    raw_filename: str,
    tag_artist: str = "",
    tag_title: str = "",
    tag_album: str = "",
    llm_classifier: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Parses raw filename and path into clean, structured metadata:
    Language, Category_or_Artist, Album, Title, CleanFilename.
    Preserves separation of same-named tracks inside specific movie/album folders.
    """
    stem, ext = os.path.splitext(raw_filename)
    clean_stem = clean_watermarks(stem)
    language, default_cat = detect_language_and_category(file_path, raw_filename, tag_artist)
    
    artist = tag_artist.strip() if tag_artist else ""
    title = tag_title.strip() if tag_title else ""
    album = tag_album.strip() if tag_album else ""
    is_generic = is_generic_track(raw_filename)

    # ----------------------------------------------------
    # Optional Local LLM Hook for Ambiguous/Unclassified Tracks
    # ----------------------------------------------------
    # Only invoke LLM fallback if language is Hindi and category is General without specific album/artist tags,
    # or if completely unresolved. Never override an already established language (e.g. English/Marathi/Sanskrit/Pravachan).
    if llm_classifier and hasattr(llm_classifier, "classify_ambiguous_track"):
        if (language == "Hindi" and default_cat == "General" and not album and not artist) or (is_generic and language == "Hindi" and default_cat == "General"):
            llm_res = llm_classifier.classify_ambiguous_track(raw_filename, artist, album, title)
            if llm_res:
                language = llm_res.get("language", language)
                album = llm_res.get("movie_or_album", album)
                title = llm_res.get("title", title)
                artist = llm_res.get("artist", artist)

    # ----------------------------------------------------
    # Hindi (Movie or Collection at consistent level 2)
    # ----------------------------------------------------
    if language == "Hindi":
        movie, clean_song = extract_bollywood_movie_and_song(
            clean_stem=clean_stem,
            stem=stem,
            file_path=file_path,
            tag_album=album,
            tag_artist=artist,
            tag_title=title
        )
        # Check canonical artist consolidation for Hindi artists (Mukesh, Lata, Kishore, Rafi, Jagjit, Pankaj Udhas, A.R. Rahman, etc.)
        canon_art = resolve_canonical_artist(artist) or resolve_canonical_artist(movie)
        if not canon_art:
            # Check if singer is mentioned in parentheses/filename or tags e.g. "01 dil jo na keh saka (rafi ) .mp3"
            hindi_singers = [
                "rafi", "mukesh", "lata", "kishore", "asha", "pankaj udhas", "pankaj udas", "jagjit",
                "rd burman", "r d burman", "r.d. burman", "burman", "manna dey", "talat", "hemant",
                "geeta dutt", "yesudas", "mahendra kapoor", "arijit", "shreya", "sonu nigam", "sonu",
                "shaan", "kk", "k.k.", "udit narayan", "udit", "kumar sanu", "alka yagnik", "alka",
                "kavita krishnamurthy", "kavita", "lucky ali", "kailash kher", "atif", "mohit chauhan",
                "sukhwinder", "mika singh", "mika", "sunidhi chauhan", "sunidhi", "neha kakkar",
                "himesh", "anuradha paudwal", "anuradha", "suresh wadkar", "bappi lahiri", "adnan sami"
            ]
            check_text = f"{clean_stem.lower()} {file_path.lower()} {artist.lower()} {title.lower()}"
            for cand in hindi_singers:
                if cand in check_text:
                    canon_art = resolve_canonical_artist(cand)
                    if canon_art:
                        break

        # Prioritize Movie over Artist for Hindi songs (user directive: Movie > Album > Artist)
        if movie and movie != "Evergreen Classics" and len(movie) > 2:
            clean_cat = movie
        elif canon_art:
            clean_cat = canon_art
        else:
            clean_cat = movie or "Evergreen Classics"
        category = clean_cat
        return {
            "language": "Hindi",
            "category": category,
            "album": movie,
            "artist": canon_art or artist or "Various Artists",
            "title": clean_song,
            "filename": f"{clean_song}{ext}",
            "is_generic": is_generic
        }

    # ----------------------------------------------------
    # Generic Filename in Other Languages (Track1.mp3, 001.wma)
    # Must preserve parent folder as album/context to avoid collision!
    # ----------------------------------------------------
    if is_generic:
        parent_dir = os.path.basename(os.path.dirname(file_path))
        category = parent_dir if parent_dir and parent_dir != language else default_cat
        clean_title = title if title and not is_generic_track(f"{title}.mp3") else clean_stem.title()
        return {
            "language": language,
            "category": category,
            "album": parent_dir,
            "artist": artist or parent_dir,
            "title": clean_title,
            "filename": f"{clean_title}{ext}",
            "is_generic": True
        }

    # ----------------------------------------------------
    # English / Western Music (Artist/Band at level 2)
    # ----------------------------------------------------
    if language == "English":
        dash_parts = [p.strip() for p in clean_stem.split(" - ") if p.strip()]
        parent_dir = os.path.basename(os.path.dirname(file_path))
        
        # Check if parent folder or tag is an explicit canonical artist
        parent_canon = resolve_canonical_artist(parent_dir)
        tag_canon = resolve_canonical_artist(artist)

        if len(dash_parts) >= 3:
            if re.match(r"^\d+$", dash_parts[0]):
                # TrackNum - Band - Song
                band = clean_name(dash_parts[1])
                song = clean_name(dash_parts[2])
            elif re.match(r"^\d+$", dash_parts[1]):
                # Band - TrackNum - Song (e.g. Coldplay - 03 - Lost!)
                band = clean_name(dash_parts[0])
                song = clean_name(dash_parts[2])
            else:
                band = clean_name(dash_parts[0])
                song = clean_name(dash_parts[-1])
        elif len(dash_parts) >= 2:
            if re.match(r"^\d+$", dash_parts[0]):
                song = clean_name(dash_parts[1])
                band = tag_canon or (clean_name(artist) if artist else (parent_canon or (parent_dir if parent_dir != "English" else "Various Artists")))
            else:
                p0 = clean_name(dash_parts[0])
                p1 = clean_name(dash_parts[1])
                # Check for inverted pattern: "Song - Artist" vs "Artist - Song"
                p0_canon = resolve_canonical_artist(p0)
                p1_canon = resolve_canonical_artist(p1)
                if p1_canon and not p0_canon:
                    # Inverted: e.g. "Fix You - Coldplay"
                    band = p1_canon
                    song = p0
                else:
                    band = p0_canon or p0
                    song = p1
        else:
            band = tag_canon or (clean_name(artist) if artist else (parent_canon or (parent_dir if parent_dir != "English" else "Various Artists")))
            song = clean_name(clean_stem)
            
        if not song:
            song = clean_name(title) if title else clean_name(clean_stem)
            
        # Canonical alias resolution
        canon = resolve_canonical_artist(band)
        if canon:
            band_clean = canon
        elif band and band.lower() not in ["english", "incoming_chunk_f", "incoming chunk f", "unorganized", "organized", "bmw-music", "new"]:
            band_clean = clean_name(band)
        else:
            band_clean = "Rock & Pop"
        category = band_clean
        return {
            "language": "English",
            "category": category,
            "album": album or band_clean,
            "artist": band_clean,
            "title": song,
            "filename": f"{song}{ext}",
            "is_generic": False
        }

    # ----------------------------------------------------
    # Marathi Music (Natya Sangeet & Devotional Album at level 2)
    # ----------------------------------------------------
    if language == "Marathi":
        parent_dir = os.path.basename(os.path.dirname(file_path))
        title_cleaned = re.sub(r"^\d+[\s\.\-_]+", "", clean_stem).strip().title()
        canon_m = resolve_canonical_artist(parent_dir) or resolve_canonical_artist(artist)
        if canon_m:
            category = canon_m
        elif parent_dir and parent_dir.lower() not in ["marathi", "incoming_chunk_f", "incoming chunk f", "unorganized", "organized", "bmw-music"]:
            category = clean_name(parent_dir)
        else:
            category = "Bhavgeet & Devotional"
            
        return {
            "language": "Marathi",
            "category": category,
            "album": album or category,
            "artist": canon_m or artist or category,
            "title": title_cleaned or clean_stem.title(),
            "filename": f"{title_cleaned or clean_stem.title()}{ext}",
            "is_generic": False
        }

    # ----------------------------------------------------
    # Sanskrit & Pravachan (Series/Collection at level 2)
    # ----------------------------------------------------
    if language == "Sanskrit":
        category = default_cat if default_cat and default_cat != "General" else "Vedic Suktas"
        canon_title = None
        for pat, cname in SUKTA_PATTERNS:
            if re.search(pat, f"{raw_filename} {clean_stem}", re.IGNORECASE):
                canon_title = cname
                category = "Vedic Suktas"
                break
        if not canon_title:
            for pat, cname in STOTRA_PATTERNS:
                if re.search(pat, f"{raw_filename} {clean_stem}", re.IGNORECASE):
                    canon_title = cname
                    category = "Stotras & Ashtakams"
                    break
        title_cleaned = canon_title or re.sub(r"^\d+[\s\.\-_]+", "", clean_stem).strip().title()
        art = "Traditional Vedic Chants" if "Sukta" in category or "Samhita" in category else "Traditional Sanskrit Chants"
        return {
            "language": "Sanskrit",
            "category": category,
            "album": album or category,
            "artist": artist or art,
            "title": title_cleaned,
            "filename": f"{title_cleaned}{ext}",
            "is_generic": False
        }
    elif language == "Pravachan":
        parent_dir = os.path.basename(os.path.dirname(file_path))
        grandparent_dir = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        raw_series = grandparent_dir if grandparent_dir not in ["Pravachan", "BMW-Music", "Hindi", "unorganized", "organized"] else parent_dir
        if raw_series in ["Pravachan", "BMW-Music", "Hindi", "unorganized", "organized"] or not raw_series:
            series = "Bhagwat Katha & Discourses"
        else:
            series = clean_name(raw_series)
        category = series
        title_cleaned = clean_stem.strip().title()
        return {
            "language": "Pravachan",
            "category": category,
            "album": series,
            "artist": series,
            "title": title_cleaned,
            "filename": f"{title_cleaned}{ext}",
            "is_generic": False
        }
    else:
        category = default_cat
        title_cleaned = re.sub(r"^\d+[\s\.\-_]+", "", clean_stem).strip().title()
        return {
            "language": language,
            "category": category,
            "album": album or category,
            "artist": artist or category,
            "title": title_cleaned or clean_stem.title(),
            "filename": f"{title_cleaned or clean_stem.title()}{ext}",
            "is_generic": False
        }
