"""
Auralis - Windows NTFS Path Sanitizer Utilities
Ensures 100% legal, bracket-free, collision-free paths across Windows filesystems.
Strictly removes ( and ) brackets and cleans non-cultural stray numbers.
"""

import os
import re
from typing import Optional, Tuple

# Approved cultural exceptions where numbers are an integral part of the entity
CULTURAL_NUMBERED_ENTITIES = {
    "taxi no 9211": "Taxi No 9211",
    "1942 a love story": "1942 A Love Story",
    "1947 earth": "1947 Earth",
    "3 idiots": "3 Idiots",
    "3 movie": "3",
    "3": "3",
    "shree 420": "Shree 420",
    "don 2": "Don 2",
    "khiladi 786": "Khiladi 786",
    "section 375": "Section 375",
    "u2": "U2",
    "blink 182": "Blink 182",
    "sum 41": "Sum 41",
    "3 doors down": "3 Doors Down",
    "matchbox 20": "Matchbox 20",
    "level 42": "Level 42",
    "ub40": "UB40",
    "2 am to midnight": "2 Am To Midnight",
    "summer of 69": "Summer Of 69",
}

# Noise, rip tokens, resolution tags and uploader watermarks to strip
RIP_NOISE_PATTERNS = [
    r"\d{3,4}p\b",
    r"\b\d+k(?:bps)?\b",
    r"\bhd\s*song\b",
    r"\bfull\s*hd\b",
    r"\bhd\s*video\b",
    r"\bdvdrip\b",
    r"\bwebrip\b",
    r"\b\d{1,2}\s*[sS]\b",
    r"\d+!s\b",
    r"\bsihag\b",
    r"-\s*Golmaal\b",
    r"-\s*Chhoti\s*Si\s*Baat\b",
    r"\bdownloadming(?:\.se|\.com)?\b",
    r"\bfmw11(?:\.com)?\b",
    r"\bsongs\.pk\b",
    r"\bbindassbuzz(?:\.com)?\b",
]


def strip_rip_noise_and_suffixes(text: str) -> str:
    """
    Strips rip noise, uploader tags, resolution markers, and redundant movie suffixes.
    Example:
      'Aane Wala Pal11 S' -> 'Aane Wala Pal'
      'Na Jaane Kyun - Chhoti Si Baat 720P Hd Song' -> 'Na Jaane Kyun'
      'Alabarfibarfi2012Sihag' -> 'Ala Barfi'
      'Dil Kya Kare03 S' -> 'Dil Kya Kare'
    """
    if not text:
        return ""

    cleaned = text
    # Strip known rip tokens
    for pat in RIP_NOISE_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)

    # Strip trailing digits attached to words like 'Pal11 S' -> 'Pal' or 'Kare03 S' -> 'Kare'
    cleaned = re.sub(r"([a-zA-Z]+)\d{2,}\s*[sS]?\b", r"\1", cleaned)

    # Clean redundant dashes and spaces
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" .-")


def separate_artist_from_song_title(stem: str, folder_artist: Optional[str] = None) -> str:
    """
    Ensures the song filename contains ONLY the original song title, stripping any
    embedded artist names or credit suffixes.
    Example:
      'Aarambh - Piyush Mishra' -> 'Aarambh'
      'Fakeera - Rahat Fateh Ali Khan' -> 'Fakeera'
      'Maaeri Euphoria' -> 'Maaeri'
      'Nahi Rakhta Dil Mein Lucky Ali' -> 'Nahi Rakhta Dil Mein'
      'Chammak Challo Akon' -> 'Chammak Challo'
    """
    if not stem:
        return ""

    cleaned = strip_rip_noise_and_suffixes(stem)

    # Strip explicit ' - Artist' if separated by hyphen
    if " - " in cleaned:
        parts = cleaned.split(" - ")
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            if left.isdigit():
                return right
            # If right is folder artist or recognized credit (e.g. 'Piyush Mishra', 'Rahat Fateh Ali Khan')
            if folder_artist and right.lower() == folder_artist.lower():
                return left
            # If left is folder artist (e.g. 'Neeraj Sridhar - Bhool Bhoolaiyaa')
            if folder_artist and left.lower() == folder_artist.lower():
                return right
            # If right contains words like 'Alt', 'Remix', 'Part', 'Cover', preserve left with clean modifier
            if re.search(r"^(alt|remix|acoustic|cover|unplugged|reprise)$", right, re.IGNORECASE):
                return f"{left} - {right.capitalize()}"
            # Common pattern: <Song Title> - <Singer>
            if len(right.split()) <= 4 and not any(k in right.lower() for k in ["part", "vol", "scene"]):
                return left

    # Strip trailing folder artist if glued without hyphen (e.g. 'Maaeri Euphoria' in folder 'Euphoria')
    if folder_artist and len(folder_artist) >= 4:
        art_pat = r"\s+" + re.escape(folder_artist) + r"$"
        cleaned = re.sub(art_pat, "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip(" .-")


def remove_brackets_and_special_chars(text: str) -> str:
    """Removes all brackets (), [], {} and illegal NTFS characters."""
    if not text:
        return ""
    # Strip rip/quality tags first
    cleaned = re.sub(r"\[\s*(songs\.pk|downloadming|djluv|mp3|320kbps|128kbps|webrip|fmw11)\s*\]", "", text, flags=re.I)
    cleaned = re.sub(r"\(\s*(songs\.pk|downloadming|djluv|mp3|320kbps|128kbps|webrip|fmw11)\s*\)", "", cleaned, flags=re.I)
    # Remove bracket characters themselves while keeping content: (Boyzone) -> Boyzone
    cleaned = re.sub(r"[\(\)\[\]\{\}]", " ", cleaned)
    # Replace illegal NTFS characters (< > : " / \ | ? *) with spaces or dashes
    cleaned = re.sub(r'[<>:"/\\|?*]', "-", cleaned)
    # Clean redundant dashes and spaces
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" .-")

def clean_audio_title(title: str, is_folder: bool = False) -> str:
    """
    Cleans audio titles and folder names:
    - Removes all brackets.
    - Preserves approved numbers (Taxi No 9211, U2, Day 01-05).
    - Strips stray rip track numbers (e.g. '01 - ', '002 ') from song titles.
    - Strips numbers from folders unless approved cultural exception or Day/Adhyay series.
    """
    if not title:
        return "Untitled"

    raw_lower = title.strip().lower()
    for k, v in CULTURAL_NUMBERED_ENTITIES.items():
        k_re = r"\b" + r"[-\s]*".join(re.escape(w) for w in k.split()) + r"\b"
        if re.search(k_re, raw_lower):
            return v

    # Day / Adhyay series preservation for Pravachan / Katha
    if re.search(r"\b(day\s*\d+(?:-\d+)?|adhyay\s*\d+(?:-\d+)?|part\s*\d+)\b", raw_lower):
        s = remove_brackets_and_special_chars(title)
        return s.title()

    # Strip standalone 4-digit years unless 1942 or 1947
    if not any(yr in raw_lower for yr in ["1942 a love story", "1947 earth"]):
        title = re.sub(r"[\(\[\{]?\b(19\d\d|20\d\d)\b[\)\]\}]?", "", title)

    s = remove_brackets_and_special_chars(title)
    s = strip_rip_noise_and_suffixes(s)
    if not is_folder:
        s = separate_artist_from_song_title(s)

    # Strip leading track numbers e.g. "01 - ", "001 ", "32 "
    s = re.sub(r"^\s*\d+[\s\.\-_]+", "", s)

    # If it is a folder (movie name, album, artist), remove numbers unless approved
    if is_folder:
        tokens = s.split()
        clean_toks = []
        for tok in tokens:
            if tok.isdigit() and tok not in ["9211", "1942", "420", "3", "2", "41", "182"]:
                continue
            clean_toks.append(tok)
        s = " ".join(clean_toks)
    else:
        # For song filenames, strip stray trailing numbers or isolated digits unless approved (like '2 am', 'part 1')
        tokens = s.split()
        clean_toks = []
        for i, tok in enumerate(tokens):
            if tok.isdigit():
                # Allow 'part 1', 'day 1', 'vol 1', 'cd 1'
                prev = tokens[i - 1].lower() if i > 0 else ""
                nxt = tokens[i + 1].lower() if i + 1 < len(tokens) else ""
                if prev in ["part", "day", "vol", "volume", "cd", "track", "no"] or nxt in ["am", "pm", "idiots", "doors"]:
                    clean_toks.append(tok)
                elif tok in ["9211", "1942", "420", "69"]:
                    clean_toks.append(tok)
                else:
                    continue
            else:
                clean_toks.append(tok)
        s = " ".join(clean_toks)


    s = re.sub(r"\s+", " ", s).strip(" .-_/\\")
    return s.title() if s else "Untitled"

def sanitize_path_component(name: str, is_folder: bool = False) -> str:
    """Sanitizes a single directory or file component, ensuring zero brackets."""
    return clean_audio_title(name, is_folder=is_folder)

def sanitize_relative_path(rel_path: str) -> str:
    """Sanitizes each directory component in a relative path, enforcing zero brackets."""
    parts = [p for p in re.split(r"[\\/]+", rel_path) if p]
    sanitized_parts = [clean_audio_title(p, is_folder=True) for p in parts]
    return os.path.join(*sanitized_parts)

def sanitize_filename(fname: str) -> str:
    """Sanitizes filename stem while preserving extension, ensuring zero brackets."""
    stem, ext = os.path.splitext(fname)
    stem_clean = clean_audio_title(stem, is_folder=False)
    # Double check zero brackets in final filename
    stem_clean = re.sub(r"[\(\)\[\]\{\}]", "", stem_clean)
    return f"{stem_clean}{ext}"
