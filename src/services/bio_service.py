"""
Auralis - Bio Service Module

Handles fetching artist biographies from online sources.
"""

import abc
import os
import re
from typing import Any, List, Optional
from urllib.parse import quote

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

try:
    import pylast  # type: ignore

    HAS_LASTFM = True
except ImportError:
    HAS_LASTFM = False


class BioProvider(abc.ABC):
    """Abstract base class for bio providers."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass

    @abc.abstractmethod
    def get_bio(self, artist_name: str) -> Optional[str]:
        """
        Fetch biography for the given artist.

        Args:
            artist_name (str): Name of the artist.

        Returns:
            Optional[str]: The biography text if found, None otherwise.
        """
        pass


class WikipediaBioProvider(BioProvider):
    """Fetches artist biographies from Wikipedia."""

    def __init__(self) -> None:
        """Initialize Wikipedia provider."""
        self.base_url = "https://en.wikipedia.org/wiki/"

    @property
    def name(self) -> str:
        """Return the name of the provider."""
        return "Wikipedia"

    def get_bio(self, artist_name: str) -> Optional[str]:
        """
        Fetch biography from Wikipedia.

        Args:
            artist_name (str): Name of the artist.

        Returns:
            Optional[str]: The biography text if found, None otherwise.
        """
        if not artist_name:
            return None

        try:
            response = self._fetch_page(artist_name)
            if not response:
                return None

            return self._parse_bio(response.content)

        except Exception as e:
            print(f"Error fetching Wikipedia bio for {artist_name}: {str(e)}")
            return None

    def _fetch_page(self, artist_name: str) -> Optional[requests.Response]:
        """Fetch the Wikipedia page for the artist."""
        # Clean up artist name for URL
        # Replace spaces with underscores and quote other special characters
        formatted_name = quote(artist_name.replace(" ", "_"))
        url = f"{self.base_url}{formatted_name}"

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response

        # Try adding "(band)" or "(musician)" if direct lookup fails
        for suffix in ["_(band)", "_(musician)", "_(singer)"]:
            url_suffix = f"{formatted_name}{suffix}"
            response = requests.get(f"{self.base_url}{url_suffix}", timeout=10)
            if response.status_code == 200:
                return response

        return None

    def _parse_bio(self, content: bytes) -> Optional[str]:
        """Parse biography text from page content."""
        soup = BeautifulSoup(content, "html.parser")

        # Find the main content div
        content_div = soup.find(id="mw-content-text")
        if not content_div:
            return None

        # Find all paragraphs
        paragraphs = content_div.find_all("p", recursive=True)

        for p in paragraphs:
            # skip empty paragraphs
            text = p.get_text().strip()
            if not text:
                continue

            # Check if it's a valid paragraph (usually the first substantial one)
            # Wikipedia often has empty p tags or p tags with just coordinates/images
            if len(text) > 50:
                bio_text = text
                # Remove citation numbers like [1][2]
                bio_text = re.sub(r"\[\d+\]", "", bio_text)
                return bio_text

        return None


class LastFmBioProvider(BioProvider):
    """Fetches artist biographies from Last.fm."""

    def __init__(self) -> None:
        """Initialize Last.fm provider."""
        self.available = HAS_LASTFM
        self.network: Optional[Any] = None
        self._init_network()

    def _init_network(self) -> None:
        """Initialize the Last.fm network with credentials from environment variables."""
        if not self.available:
            return

        api_key = os.environ.get("LASTFM_API_KEY")
        api_secret = os.environ.get("LASTFM_API_SECRET")

        if api_key and api_secret:
            try:
                self.network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)
            except Exception as e:
                print(f"Error initializing Last.fm network: {str(e)}")
                self.available = False
        else:
            self.available = False

    @property
    def name(self) -> str:
        """Return the name of the provider."""
        return "Last.fm"

    def get_bio(self, artist_name: str) -> Optional[str]:
        """
        Fetch biography from Last.fm.

        Args:
            artist_name (str): Name of the artist.

        Returns:
            Optional[str]: The biography text if found, None otherwise.
        """
        if not self.available or not self.network or not artist_name:
            return None

        try:
            artist = self.network.get_artist(artist_name)
            bio = artist.get_bio_summary()

            if bio:
                # Clean up HTML tags if present (Last.fm sometimes returns HTML)
                clean_bio = BeautifulSoup(bio, "html.parser").get_text()
                # Remove "Read more on Last.fm" suffix
                clean_bio = re.sub(
                    r"\s*Read more on Last\.fm.*$", "", clean_bio, flags=re.IGNORECASE
                ).strip()
                return clean_bio

            return None

        except Exception as e:
            print(f"Error fetching Last.fm bio for {artist_name}: {str(e)}")
            return None


class BioService:
    """Service to fetch artist biographies from multiple providers."""

    def __init__(self) -> None:
        """Initialize BioService with available providers."""
        self.providers: List[BioProvider] = []
        self._register_providers()

    def _register_providers(self) -> None:
        """Register bio providers."""
        # Add Last.fm first as it's usually more structured for music
        lastfm = LastFmBioProvider()
        if lastfm.available:
            self.providers.append(lastfm)
        else:
            # If Last.fm is not available, Wikipedia is a good primary
            pass

        # Add Wikipedia
        self.providers.append(WikipediaBioProvider())

    def get_artist_bio(self, artist_name: str) -> Optional[str]:
        """
        Get biography for an artist from the first available provider.

        Args:
            artist_name (str): Name of the artist.

        Returns:
            Optional[str]: Biography text if found, None otherwise.
        """
        for provider in self.providers:
            try:
                bio = provider.get_bio(artist_name)
                if bio:
                    return bio
            except Exception as e:
                print(f"Error getting bio from {provider.name}: {str(e)}")
                continue

        return None
