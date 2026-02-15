"""
Auralis - Lyrics Service

This module provides functionality to fetch lyrics for audio files and
embed them in the file's metadata.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional

import requests

# Set up logging
logger = logging.getLogger("auralis.lyrics")


class LyricsService:
    """Service for fetching lyrics and embedding them in audio files"""

    def __init__(self):
        """Initialize the lyrics service"""
        self.available = True
        self.user_agent = "Auralis/1.0"
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch_lyrics(self, artist: str, title: str) -> Optional[str]:
        """
        Fetch lyrics for a song from various sources

        Args:
            artist (str): The artist name
            title (str): The song title

        Returns:
            str or None: The lyrics if found, None otherwise
        """
        # Clean up artist and title
        artist = self._clean_name(artist)
        title = self._clean_name(title)

        # Check cache first
        cache_key = f"{artist}|{title}".lower()
        if cache_key in self.cache:
            logger.info(f"Using cached lyrics for {artist} - {title}")
            return self.cache[cache_key]

        # Try different sources in order of reliability
        lyrics = None

        # Try Genius
        lyrics = self._fetch_from_genius(artist, title)
        if lyrics:
            self.cache[cache_key] = lyrics
            return lyrics

        # Try Musixmatch (limited without API key)
        lyrics = self._fetch_from_musixmatch(artist, title)
        if lyrics:
            self.cache[cache_key] = lyrics
            return lyrics

        logger.warning(f"Could not find lyrics for {artist} - {title}")
        return None

    def embed_lyrics(self, file_path: str, lyrics: str) -> bool:
        """
        Embed lyrics into an audio file's metadata

        Args:
            file_path (str): Path to the audio file
            lyrics (str): The lyrics to embed

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from mutagen import File
            from mutagen.id3 import ID3, USLT

            file_path = Path(file_path)
            extension = file_path.suffix.lower()

            if extension == ".mp3":
                # For MP3 files, use ID3 tags
                try:
                    tags = ID3(file_path)
                except BaseException:
                    tags = ID3()

                # Remove existing lyrics
                for key in list(tags.keys()):
                    if key.startswith("USLT"):
                        del tags[key]

                # Add new lyrics
                tags["USLT::eng"] = USLT(encoding=3, lang="eng", desc="", text=lyrics)

                tags.save(file_path)
                logger.info(f"Embedded lyrics in {file_path}")
                return True

            else:
                # For other formats like FLAC, M4A, etc.
                audio = File(file_path)

                if audio is None:
                    logger.error(f"Unsupported file format: {extension}")
                    return False

                # Different files have different tag names for lyrics
                if hasattr(audio, "tags"):
                    if extension == ".flac":
                        audio["lyrics"] = lyrics
                    elif extension == ".m4a" or extension == ".mp4":
                        audio["\xa9lyr"] = lyrics
                    elif extension in [".ogg", ".oga", ".opus"]:
                        audio["LYRICS"] = lyrics
                    else:
                        # Try a common approach for other formats
                        audio["lyrics"] = lyrics

                    audio.save()
                    logger.info(f"Embedded lyrics in {file_path}")
                    return True
                else:
                    logger.error(f"File does not support tags: {file_path}")
                    return False

        except ImportError:
            logger.error("Mutagen library is required for embedding lyrics")
            return False
        except Exception as e:
            logger.error(f"Error embedding lyrics: {str(e)}")
            return False

    def _clean_name(self, name: str) -> str:
        """Clean up artist or title name for better matching"""
        if not name:
            return ""

        # Remove featuring artists
        name = re.sub(r"\(feat\..*?\)", "", name)
        name = re.sub(r"\bft\..*?$", "", name)
        name = re.sub(r"\bfeat\..*?$", "", name)

        # Remove version info
        name = re.sub(r"\(.*?version\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\(.*?remix\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\(.*?edit\)", "", name, flags=re.IGNORECASE)

        # Remove other common suffixes in parentheses
        name = re.sub(r"\(.*?\)", "", name)
        name = re.sub(r"\[.*?\]", "", name)

        # Clean up whitespace
        name = re.sub(r"\s+", " ", name)
        name = name.strip()

        return name

    def _fetch_from_genius(self, artist: str, title: str) -> Optional[str]:
        """Fetch lyrics from Genius"""
        try:
            # Search for the song
            search_url = f"https://genius.com/api/search/multi?q={artist} {title}"
            search_url = search_url.replace(" ", "%20")

            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()

            # Find the first song hit
            sections = data.get("response", {}).get("sections", [])
            for section in sections:
                if section.get("type") == "song":
                    hits = section.get("hits", [])
                    if hits:
                        song_path = hits[0].get("result", {}).get("path")
                        if song_path:
                            # Get the lyrics page
                            lyrics_url = f"https://genius.com{song_path}"
                            lyrics_response = self.session.get(lyrics_url, timeout=10)

                            if lyrics_response.status_code == 200:
                                # Extract lyrics using regex
                                html = lyrics_response.text

                                # Look for the lyrics div
                                lyrics_match = re.search(
                                    r'<div class="lyrics">(.+?)</div>', html, re.DOTALL
                                )
                                if lyrics_match:
                                    lyrics = lyrics_match.group(1)
                                else:
                                    # Newer Genius format
                                    lyrics_json = re.search(
                                        r"__PRELOADED_STATE__ = JSON.parse\((.+?)\);</script>", html
                                    )
                                    if lyrics_json:
                                        json_str = lyrics_json.group(1).strip("'")
                                        try:
                                            json_data = json.loads(json_str)
                                            song_data = json_data.get("songPage", {}).get(
                                                "lyricsData", {}
                                            )
                                            lyrics = song_data.get("body", {}).get("html", "")
                                        except BaseException:
                                            return None
                                    else:
                                        # Try another approach
                                        lyrics_container = re.search(
                                            r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.+?)</div>\s*</div>',
                                            html,
                                            re.DOTALL,
                                        )
                                        if lyrics_container:
                                            lyrics = lyrics_container.group(1)
                                        else:
                                            return None

                                # Clean up HTML tags
                                lyrics = re.sub(r"<[^>]+>", "", lyrics)
                                # Remove [Verse], [Chorus], etc.
                                lyrics = re.sub(r"\[.*?\]", "", lyrics)

                                # Fix HTML entities
                                lyrics = lyrics.replace("&amp;", "&")
                                lyrics = lyrics.replace("&lt;", "<")
                                lyrics = lyrics.replace("&gt;", ">")
                                lyrics = lyrics.replace("&quot;", '"')

                                # Clean up whitespace
                                lyrics = re.sub(r"\n{3,}", "\n\n", lyrics)
                                lyrics = lyrics.strip()

                                return lyrics

            return None

        except Exception as e:
            logger.error(f"Error fetching lyrics from Genius: {str(e)}")
            return None

    def _fetch_from_musixmatch(self, artist: str, title: str) -> Optional[str]:
        """Fetch lyrics from Musixmatch (limited without API key)"""
        try:
            # Search for the song
            search_term = f"{artist} {title}".replace(" ", "%20")
            search_url = f"https://www.musixmatch.com/search/{search_term}"

            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None

            # Extract the first song URL
            html = response.text
            song_link_match = re.search(r'href="(/lyrics/[^"]+)"', html)

            if not song_link_match:
                return None

            # Get the lyrics page
            lyrics_path = song_link_match.group(1)
            lyrics_url = f"https://www.musixmatch.com{lyrics_path}"

            lyrics_response = self.session.get(lyrics_url, timeout=10)
            if lyrics_response.status_code != 200:
                return None

            # Extract lyrics using regex
            html = lyrics_response.text
            lyrics_match = re.search(
                r'<span class="lyrics__content__ok">(.+?)</span>', html, re.DOTALL
            )

            if not lyrics_match:
                # Try another pattern
                lyrics_match = re.search(
                    r'<div class="mxm-lyrics"><span class="lyrics__content__[^"]*">(.+?)</span></div>',
                    html,
                    re.DOTALL,
                )

            if lyrics_match:
                lyrics = lyrics_match.group(1)

                # Clean up HTML tags
                lyrics = re.sub(r"<[^>]+>", "\n", lyrics)

                # Fix HTML entities
                lyrics = lyrics.replace("&amp;", "&")
                lyrics = lyrics.replace("&lt;", "<")
                lyrics = lyrics.replace("&gt;", ">")
                lyrics = lyrics.replace("&quot;", '"')

                # Clean up whitespace
                lyrics = re.sub(r"\n{3,}", "\n\n", lyrics)
                lyrics = lyrics.strip()

                return lyrics

            return None

        except Exception as e:
            logger.error(f"Error fetching lyrics from Musixmatch: {str(e)}")
            return None


# Singleton instance
lyrics_service = LyricsService()


def fetch_lyrics(artist: str, title: str) -> Optional[str]:
    """Fetch lyrics for a song"""
    return lyrics_service.fetch_lyrics(artist, title)


def embed_lyrics(file_path: str, lyrics: str) -> bool:
    """Embed lyrics into an audio file"""
    return lyrics_service.embed_lyrics(file_path, lyrics)


def fetch_and_embed_lyrics(file_path: str, metadata: Dict) -> bool:
    """
    Fetch lyrics for a file based on its metadata and embed them

    Args:
        file_path (str): Path to the audio file
        metadata (dict): File metadata with at least 'artist' and 'title' keys

    Returns:
        bool: True if successful, False otherwise
    """
    artist = metadata.get("artist", "")
    title = metadata.get("title", "")

    if not artist or not title:
        logger.warning(f"Missing artist or title for lyrics lookup: {file_path}")
        return False

    lyrics = fetch_lyrics(artist, title)
    if not lyrics:
        return False

    return embed_lyrics(file_path, lyrics)
