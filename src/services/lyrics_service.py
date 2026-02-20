"""
Auralis - Lyrics Service

This module provides functionality to fetch lyrics for audio files and
embed them in the file's metadata.
"""

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Set up logging
logger = logging.getLogger("auralis.lyrics")


class LyricsProvider(ABC):
    """Abstract base class for lyrics providers"""

    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.name = "Base"

    @abstractmethod
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """
        Fetch lyrics for a song

        Args:
            artist (str): The artist name
            title (str): The song title

        Returns:
            str or None: The lyrics if found, None otherwise
        """
        pass

    def _clean_name(self, name: str) -> str:
        """Clean up artist or title name for better matching"""
        if not name:
            return ""

        # Remove featuring artists
        name = re.sub(r"\(feat\..*?\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\bft\..*?$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\bfeat\..*?$", "", name, flags=re.IGNORECASE)

        # Remove version info
        name = re.sub(r"\(.*?version\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\(.*?remix\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\(.*?edit\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s-\s.*remix.*", "", name, flags=re.IGNORECASE)

        # Remove other common suffixes in parentheses
        name = re.sub(r"\(.*?\)", "", name)
        name = re.sub(r"\[.*?\]", "", name)

        # Clean up whitespace
        name = re.sub(r"\s+", " ", name)
        name = name.strip()

        return name


class GeniusProvider(LyricsProvider):
    """Lyrics provider for Genius.com"""

    def __init__(self, session: requests.Session) -> None:
        super().__init__(session)
        self.name = "Genius"

    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Fetch lyrics from Genius"""
        try:
            # Clean names
            artist = self._clean_name(artist)
            title = self._clean_name(title)

            # Search for the song
            response = self.session.get(
                "https://genius.com/api/search/multi",
                params={"q": f"{artist} {title}"},  # type: ignore
                timeout=10,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            # Find the first song hit
            sections = data.get("response", {}).get("sections", [])
            for section in sections:
                if section.get("type") == "song":
                    hits = section.get("hits", [])
                    if hits:
                        # Try to match artist name to avoid bad covers
                        for hit in hits:
                            result = hit.get("result", {})
                            hit_artist = result.get("primary_artist", {}).get("name", "")

                            # Simple containment check (case insensitive)
                            if (
                                artist.lower() in hit_artist.lower()
                                or hit_artist.lower() in artist.lower()
                            ):
                                song_path = result.get("path")
                                if song_path:
                                    return self._fetch_lyrics_from_path(song_path)
            return None

        except Exception as e:
            logger.error(f"Error fetching from Genius: {str(e)}")
            return None

    def _fetch_lyrics_from_path(self, song_path: str) -> Optional[str]:
        """Fetch lyrics from a Genius song path"""
        try:
            lyrics_url = f"https://genius.com{song_path}"
            response = self.session.get(lyrics_url, timeout=10)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Genius has multiple formats for lyrics containers
            # 1. <div class="lyrics">...</div> (Old)
            # 2. <div data-lyrics-container="true">...</div> (New)

            lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})

            if lyrics_divs:
                lyrics_parts = []
                for div in lyrics_divs:
                    # Replace <br> with newlines
                    for br in div.find_all("br"):
                        br.replace_with("\n")
                    lyrics_parts.append(div.get_text())

                lyrics = "\n\n".join(lyrics_parts)
            else:
                # Fallback to old format
                lyrics_div = soup.find("div", class_="lyrics")
                if lyrics_div:
                    lyrics = lyrics_div.get_text()
                else:
                    return None

            # Clean up
            lyrics = lyrics.strip()
            # Remove [Verse], [Chorus] headers if desired, but many users like them.
            # We keep them but ensure clean spacing.

            return lyrics

        except Exception as e:
            logger.error(f"Error parsing Genius lyrics: {str(e)}")
            return None


class AZLyricsProvider(LyricsProvider):
    """Lyrics provider for AZLyrics.com"""

    def __init__(self, session: requests.Session) -> None:
        super().__init__(session)
        self.name = "AZLyrics"

    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Fetch lyrics from AZLyrics"""
        try:
            # Clean names for URL
            artist_clean = self._clean_for_url(artist)
            title_clean = self._clean_for_url(title)

            if not artist_clean or not title_clean:
                return None

            url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{title_clean}.html"

            # AZLyrics blocks aggressive scraping, so we rely on session headers
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # AZLyrics lyrics are in a div with no class, usually after the ringtone div
            # We look for the div containing the disclaimer comment
            divs = soup.find_all("div", class_=False)
            for div in divs:
                if "Usage of azlyrics.com" in str(div):
                    # Found it
                    # Remove the comment and other non-lyrics text if present
                    # The usage comment is in a Comment object, get_text might skip it
                    return str(div.get_text().strip())

            return None

        except Exception as e:
            logger.error(f"Error fetching from AZLyrics: {str(e)}")
            return None

    def _clean_for_url(self, name: str) -> str:
        """Clean string for AZLyrics URL"""
        # Remove special chars and spaces, lowercase
        name = self._clean_name(name)  # Base clean first
        name = name.lower()
        # Remove starting "the" for band names if it exists (simple heuristic)
        if name.startswith("the "):
            name = name[4:]

        name = re.sub(r"[^a-z0-9]", "", name)
        return name


class TekstowoProvider(LyricsProvider):
    """Lyrics provider for Tekstowo.pl"""

    def __init__(self, session: requests.Session) -> None:
        super().__init__(session)
        self.name = "Tekstowo"

    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Fetch lyrics from Tekstowo"""
        try:
            # Clean names
            artist = self._clean_name(artist)
            title = self._clean_name(title)

            # Search
            search_url = "https://www.tekstowo.pl/szukaj,wykonawca,tytul.html"
            params = {"search-artist": artist, "search-title": title}  # type: ignore

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Find results
            # Results are usually in a div with class "content" -> "box-przeboje" or similar
            # Tekstowo search results structure changes often, but usually lists links to songs.

            # Look for links that look like /piosenka,artist,title.html
            results = soup.find_all("a", class_="title")

            for result in results:
                # result text is usually "Artist - Title"
                text = result.get_text().strip()
                if " - " in text:
                    res_artist, res_title = text.split(" - ", 1)

                    # Basic check
                    if (
                        artist.lower() in res_artist.lower() or res_artist.lower() in artist.lower()
                    ) and (
                        title.lower() in res_title.lower() or res_title.lower() in title.lower()
                    ):

                        link = result.get("href")
                        if link:
                            return self._fetch_lyrics_from_path(str(link))

            return None

        except Exception as e:
            logger.error(f"Error fetching from Tekstowo: {str(e)}")
            return None

    def _fetch_lyrics_from_path(self, path: str) -> Optional[str]:
        """Fetch lyrics from Tekstowo path"""
        try:
            if not path.startswith("http"):
                url = f"https://www.tekstowo.pl{path}"
            else:
                url = path

            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Lyrics are in div class="song-text"
            lyrics_div = soup.find("div", class_="song-text")

            if lyrics_div:
                # Remove script tags if any
                for script in lyrics_div.find_all("script"):
                    script.decompose()

                # Remove "Poznaj historię zmian tego tekstu" link usually at bottom
                for a in lyrics_div.find_all("a"):
                    if "historię zmian" in a.get_text():
                        a.decompose()

                # Get text with separators
                lyrics = lyrics_div.get_text(separator="\n").strip()

                # Tekstowo often puts "Tekst piosenki:" at top
                if lyrics.startswith("Tekst piosenki:"):
                    lyrics = lyrics.replace("Tekst piosenki:", "", 1).strip()

                # Remove translation header if present (Tekstowo often has translation side by side or below)
                # But typically main lyrics are in song-text.

                return str(lyrics)

            return None

        except Exception as e:
            logger.error(f"Error parsing Tekstowo lyrics: {str(e)}")
            return None


class LyricsService:
    """Service for fetching lyrics and embedding them in audio files"""

    def __init__(self) -> None:
        """Initialize the lyrics service"""
        self.available = True
        self.user_agent = "Auralis/1.0"
        self.cache: Dict[str, str] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

        self.providers: List[LyricsProvider] = []
        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize default providers"""
        self.register_provider(GeniusProvider(self.session))
        self.register_provider(AZLyricsProvider(self.session))
        self.register_provider(TekstowoProvider(self.session))

    def register_provider(self, provider: LyricsProvider) -> None:
        """Register a lyrics provider"""
        self.providers.append(provider)

    def fetch_lyrics(self, artist: str, title: str) -> Optional[str]:
        """
        Fetch lyrics for a song from various sources

        Args:
            artist (str): The artist name
            title (str): The song title

        Returns:
            str or None: The lyrics if found, None otherwise
        """
        # Check cache first
        cache_key = f"{artist}|{title}".lower()
        if cache_key in self.cache:
            logger.info(f"Using cached lyrics for {artist} - {title}")
            return str(self.cache[cache_key])

        # Try each provider
        for provider in self.providers:
            try:
                logger.info(f"Fetching lyrics from {provider.name} for {artist} - {title}")
                lyrics = provider.get_lyrics(artist, title)
                if lyrics:
                    logger.info(f"Found lyrics via {provider.name}")
                    self.cache[cache_key] = lyrics
                    return lyrics
            except Exception as e:
                logger.error(f"Error fetching from {provider.name}: {str(e)}")
                continue

        logger.warning(f"Could not find lyrics for {artist} - {title}")
        return None

    def save_lrc(self, file_path: str, lyrics: str) -> bool:
        """
        Save lyrics to an LRC file

        Args:
            file_path (str): Path to the audio file
            lyrics (str): The lyrics content

        Returns:
            bool: True if successful
        """
        try:
            path_obj = Path(file_path)
            lrc_path = path_obj.with_suffix(".lrc")

            with open(lrc_path, "w", encoding="utf-8") as f:
                f.write(lyrics)

            logger.info(f"Saved lyrics to {lrc_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving LRC file: {str(e)}")
            return False

    def embed_lyrics(self, file_path: str, lyrics: str, save_lrc_file: bool = False) -> bool:
        """
        Embed lyrics into an audio file's metadata

        Args:
            file_path (str): Path to the audio file
            lyrics (str): The lyrics to embed
            save_lrc_file (bool): Whether to also save an .lrc file

        Returns:
            bool: True if successful, False otherwise
        """
        if save_lrc_file:
            self.save_lrc(file_path, lyrics)

        try:
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower()

            if extension == ".mp3":
                return self._embed_mp3_lyrics(file_path, path_obj, lyrics)
            else:
                return self._embed_generic_lyrics(file_path, extension, lyrics)

        except ImportError:
            logger.error("Mutagen library is required for embedding lyrics")
            return False
        except Exception as e:
            logger.error(f"Error embedding lyrics: {str(e)}")
            return False

    def _embed_mp3_lyrics(self, file_path: str, path_obj: Path, lyrics: str) -> bool:
        from mutagen.id3 import ID3, USLT

        try:
            tags = ID3(file_path)
        except BaseException:
            tags = ID3()

        for key in list(tags.keys()):
            if key.startswith("USLT"):
                del tags[key]

        tags["USLT::eng"] = USLT(encoding=3, lang="eng", desc="", text=lyrics)
        tags.save(path_obj)
        logger.info(f"Embedded lyrics in {file_path}")
        return True

    def _embed_generic_lyrics(self, file_path: str, extension: str, lyrics: str) -> bool:
        from mutagen import File

        audio = File(file_path)

        if audio is None:
            logger.error(f"Unsupported file format: {extension}")
            return False

        if hasattr(audio, "tags"):
            if extension == ".flac":
                audio["lyrics"] = lyrics
            elif extension == ".m4a" or extension == ".mp4":
                audio["\xa9lyr"] = lyrics
            elif extension in [".ogg", ".oga", ".opus"]:
                audio["LYRICS"] = lyrics
            else:
                audio["lyrics"] = lyrics

            audio.save()
            logger.info(f"Embedded lyrics in {file_path}")
            return True
        else:
            logger.error(f"File does not support tags: {file_path}")
            return False


# Singleton instance
lyrics_service = LyricsService()


def fetch_lyrics(artist: str, title: str) -> Optional[str]:
    """Fetch lyrics for a song"""
    return lyrics_service.fetch_lyrics(artist, title)


def embed_lyrics(file_path: str, lyrics: str, save_lrc_file: bool = False) -> bool:
    """Embed lyrics into an audio file"""
    return lyrics_service.embed_lyrics(file_path, lyrics, save_lrc_file)


def save_lrc(file_path: str, lyrics: str) -> bool:
    """Save lyrics to an LRC file"""
    return lyrics_service.save_lrc(file_path, lyrics)


def fetch_and_embed_lyrics(
    file_path: str, metadata: Dict[str, Any], save_lrc_file: bool = False
) -> bool:
    """
    Fetch lyrics for a file based on its metadata and embed them

    Args:
        file_path (str): Path to the audio file
        metadata (dict): File metadata with at least 'artist' and 'title' keys
        save_lrc_file (bool): Whether to also save an .lrc file

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

    return embed_lyrics(file_path, lyrics, save_lrc_file)
