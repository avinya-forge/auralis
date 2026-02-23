"""
Auralis - Metadata Service Module

Handles fetching and updating metadata from online sources
"""

import concurrent.futures
import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import acoustid
import discogs_client
import musicbrainzngs
import mutagen
import mutagen.flac
import mutagen.id3
import mutagen.mp3
from PyQt6.QtCore import QObject, pyqtSignal

from src.services.album_art_service import AlbumArtFetcher
from src.services.audio_analysis_service import AudioAnalyzer
from src.services.bio_service import BioService
from src.services.cache_service import CacheService

# Import lyrics service
from src.services.lyrics_service import embed_lyrics, fetch_lyrics

# Optional dependencies
try:
    import spotipy  # type: ignore
    from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore

    HAS_SPOTIFY = True
except ImportError:
    HAS_SPOTIFY = False

try:
    import pylast  # type: ignore

    HAS_LASTFM = True
except ImportError:
    HAS_LASTFM = False


class MetadataSource:
    """
    Base class for metadata sources.

    Attributes:
        name (str): The name of the metadata source.
        success_count (int): Number of successful queries.
        failure_count (int): Number of failed queries.
        total_count (int): Total number of queries.
        success_rate (float): Success rate (0.0 to 1.0).
        avg_response_time (float): Average response time in seconds.
        total_response_time (float): Total response time in seconds.
        enabled (bool): Whether the source is enabled.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the metadata source.

        Args:
            name (str): The name of the metadata source.
        """
        self.name = name
        self.success_count = 0
        self.failure_count = 0
        self.total_count = 0
        self.success_rate = 0.0
        self.avg_response_time = 0.0
        self.total_response_time = 0.0
        self.enabled = True

    def get_metadata(self, file_info: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, float]:
        """
        Get metadata for a file.

        Args:
            file_info (Dict[str, Any]): Dictionary containing file information.

        Returns:
            Tuple[Dict[str, Any], bool, float]: A tuple containing:
                - The retrieved metadata dictionary.
                - A boolean indicating success.
                - The response time in seconds.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement get_metadata")

    def update_stats(self, success: bool, response_time: float) -> None:
        """
        Update source statistics after a query.

        Args:
            success (bool): Whether the query was successful.
            response_time (float): The time taken for the query in seconds.
        """
        self.total_count += 1
        self.total_response_time += response_time

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Update success rate
        self.success_rate = self.success_count / self.total_count if self.total_count > 0 else 0.0

        # Update average response time
        self.avg_response_time = (
            self.total_response_time / self.total_count if self.total_count > 0 else 0.0
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get source statistics.

        Returns:
            Dict[str, Any]: A dictionary containing current statistics.
        """
        return {
            "name": self.name,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_count": self.total_count,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "enabled": self.enabled,
        }


class MusicBrainzSource(MetadataSource):
    """MusicBrainz/AcoustID metadata source."""

    def __init__(self) -> None:
        """Initialize the MusicBrainz source and AcoustID client."""
        super().__init__("MusicBrainz/AcoustID")

        # Set up MusicBrainz client
        musicbrainzngs.set_useragent("Auralis", "0.1", "https://github.com/patternseekers/auralis")

        # AcoustID API key (should be configurable)
        self.acoustid_api_key = "1vOwZtEn"  # Example API key, register at https://acoustid.org/
        self.fingerprinting_available = self._check_fingerprinting()

    def _check_fingerprinting(self) -> bool:
        """
        Check if audio fingerprinting is available via fpcalc.

        Returns:
            bool: True if fpcalc is available, False otherwise.
        """
        try:
            import subprocess

            result = subprocess.run(
                ["fpcalc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            return result.returncode == 0
        except BaseException:
            return False

    def get_metadata(self, file_info: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, float]:
        """
        Get metadata from MusicBrainz/AcoustID.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Tuple[Dict[str, Any], bool, float]: (metadata dict, success bool, response time).
        """
        start_time = time.time()

        try:
            # Check if fingerprinting is available
            if self.fingerprinting_available:
                try:
                    metadata = self._get_metadata_by_fingerprint(file_info)
                    if metadata:
                        response_time = time.time() - start_time
                        return metadata, True, response_time
                except Exception as e:
                    print(f"Fingerprinting error: {str(e)}")
                    # Continue with search-based approach

            # Fall back to basic search if fingerprinting fails
            metadata = self._get_metadata_by_search(file_info)
            if metadata:
                response_time = time.time() - start_time
                return metadata, True, response_time

            response_time = time.time() - start_time
            return {}, False, response_time

        except Exception as e:
            print(f"Error getting MusicBrainz metadata for {file_info['path']}: {str(e)}")
            response_time = time.time() - start_time
            return {}, False, response_time

    def _get_metadata_by_fingerprint(self, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get metadata using audio fingerprinting.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary if found, None otherwise.
        """
        # Try acoustic fingerprinting
        duration, fp_encoded = acoustid.fingerprint_file(file_info["path"])

        # Look up fingerprint
        results = acoustid.lookup(self.acoustid_api_key, fp_encoded, duration)

        for result in results:
            if result.get("recordings"):
                recording = result["recordings"][0]

                # Extract metadata
                metadata = {}

                # Basic info
                if "title" in recording:
                    metadata["title"] = recording["title"]

                if "artists" in recording and recording["artists"]:
                    metadata["artist"] = recording["artists"][0]["name"]

                # Try to get more detailed info from MusicBrainz
                if "id" in recording:
                    mb_id = recording["id"]
                    mb_metadata = self._fetch_musicbrainz_details(mb_id)
                    metadata.update(mb_metadata)

                return metadata
        return None

    def _fetch_musicbrainz_details(self, mb_id: str) -> Dict[str, Any]:
        """
        Fetch detailed metadata from MusicBrainz by ID.

        Args:
            mb_id (str): MusicBrainz recording ID.

        Returns:
            Dict[str, Any]: Detailed metadata.
        """
        metadata = {}
        try:
            mb_data = musicbrainzngs.get_recording_by_id(mb_id, includes=["releases", "artists"])

            if "recording" in mb_data:
                mb_recording = mb_data["recording"]
                metadata = self._parse_musicbrainz_response(mb_recording)

                # Add track info which depends on the release structure
                if "release-list" in mb_recording and mb_recording["release-list"]:
                    release = mb_recording["release-list"][0]
                    if "medium-list" in release and release["medium-list"]:
                        medium = release["medium-list"][0]
                        if "track-list" in medium:
                            for track in medium["track-list"]:
                                if track.get("recording", {}).get("id") == mb_id:
                                    metadata["track"] = str(track["position"])
                                    break
        except Exception as e:
            print(f"Error fetching MusicBrainz details: {str(e)}")

        return metadata

    def _get_metadata_by_search(self, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get metadata using text search.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary if found, None otherwise.
        """
        metadata = file_info.get("metadata", {})

        if "artist" in metadata and "title" in metadata:
            query = f'artist:"{metadata["artist"]}" AND recording:"{metadata["title"]}"'
            results = musicbrainzngs.search_recordings(query=query, limit=1)

            if results and "recording-list" in results and results["recording-list"]:
                recording = results["recording-list"][0]
                return self._parse_musicbrainz_response(recording)

        return None

    def _parse_musicbrainz_response(self, recording: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse MusicBrainz recording data into metadata dict.

        Args:
            recording (Dict[str, Any]): MusicBrainz recording data.

        Returns:
            Dict[str, Any]: Parsed metadata.
        """
        new_metadata = {}

        # Basic info
        if "title" in recording:
            new_metadata["title"] = recording["title"]

        if "artist-credit" in recording and recording["artist-credit"]:
            new_metadata["artist"] = recording["artist-credit"][0]["artist"]["name"]
        elif "artists" in recording and recording["artists"]:
            # Fallback for some response formats
            new_metadata["artist"] = recording["artists"][0]["name"]

        # Album and other info
        if "release-list" in recording and recording["release-list"]:
            release = recording["release-list"][0]

            if "title" in release:
                new_metadata["album"] = release["title"]

            if "date" in release:
                new_metadata["year"] = release["date"][:4]  # Extract year

        return new_metadata


class DiscogsSource(MetadataSource):
    """Discogs metadata source."""

    def __init__(self) -> None:
        """Initialize the Discogs source."""
        super().__init__("Discogs")

        # Discogs API token (should be configurable)
        # Note: Get your own token at https://www.discogs.com/settings/developers
        self.discogs_token = "ExampleDiscogsToken"  # Replace with your token

        # Set up Discogs client
        try:
            self.client = discogs_client.Client("Auralis/0.1", user_token=self.discogs_token)
            self.available = True
        except Exception as e:
            print(f"Error initializing Discogs client: {str(e)}")
            self.available = False

    def get_metadata(self, file_info: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, float]:
        """
        Get metadata from Discogs.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Tuple[Dict[str, Any], bool, float]: (metadata dict, success bool, response time).
        """
        start_time = time.time()

        try:
            if not self.available:
                response_time = time.time() - start_time
                return {}, False, response_time

            metadata = self._get_metadata_by_search(file_info)
            if metadata:
                response_time = time.time() - start_time
                return metadata, True, response_time

            response_time = time.time() - start_time
            return {}, False, response_time

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Invalid consumer token" in error_msg:
                print("Discogs authentication failed. Service disabled.")
                self.available = False
            else:
                print(f"Error getting Discogs metadata for {file_info['path']}: {error_msg}")

            response_time = time.time() - start_time
            return {}, False, response_time

    def _get_metadata_by_search(self, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get metadata from Discogs using text search.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary if found, None otherwise.
        """
        # Get metadata from file info
        metadata = file_info.get("metadata", {})

        # We need at least an artist or title to search
        if not metadata.get("artist") and not metadata.get("title"):
            return None

        # Prepare search query
        query = ""
        if metadata.get("artist"):
            query += metadata["artist"]
        if metadata.get("title"):
            if query:
                query += " - "
            query += metadata["title"]

        # Perform search
        try:
            results = self.client.search(query, type="release")

            if results and len(results) > 0:
                # Get the first result
                release = results[0]
                return self._parse_discogs_release(release, metadata)

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Invalid consumer token" in error_msg:
                print("Discogs authentication failed. Service disabled.")
                self.available = False
            else:
                print(f"Discogs search error: {error_msg}")

        return None

    def _parse_discogs_release(
        self, release: Any, current_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse Discogs release into metadata dict.

        Args:
            release (Any): Discogs release object.
            current_metadata (Dict[str, Any]): Current metadata for context.

        Returns:
            Dict[str, Any]: Parsed metadata.
        """
        new_metadata = {}

        # Basic info
        if hasattr(release, "title"):
            # Split title by delimiter if it contains artist and title
            title_parts = release.title.split(" - ", 1)
            if len(title_parts) > 1:
                if not current_metadata.get("artist"):
                    new_metadata["artist"] = title_parts[0]
                if not current_metadata.get("title"):
                    new_metadata["title"] = title_parts[1]
            else:
                # If only title is available, use it as is
                if not current_metadata.get("title"):
                    new_metadata["title"] = release.title

        # Artists
        if hasattr(release, "artists") and release.artists:
            if not current_metadata.get("artist") and not new_metadata.get("artist"):
                new_metadata["artist"] = release.artists[0].name

        # Additional info
        if hasattr(release, "year"):
            new_metadata["year"] = str(release.year)

        if hasattr(release, "genres") and release.genres:
            new_metadata["genre"] = release.genres[0]

        return new_metadata


class SpotifySource(MetadataSource):
    """Spotify metadata source."""

    def __init__(self) -> None:
        """Initialize the Spotify source."""
        super().__init__("Spotify")
        self.available = HAS_SPOTIFY
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the Spotify client with credentials from environment variables."""
        if not self.available:
            return

        # Check for credentials in env vars
        client_id = os.environ.get("SPOTIPY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")

        if client_id and client_secret:
            try:
                self.client = spotipy.Spotify(
                    auth_manager=SpotifyClientCredentials(
                        client_id=client_id, client_secret=client_secret
                    )
                )
            except Exception as e:
                print(f"Error initializing Spotify client: {str(e)}")
                self.available = False
        else:
            self.available = False

    def get_metadata(self, file_info: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, float]:
        """
        Get metadata from Spotify.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Tuple[Dict[str, Any], bool, float]: (metadata dict, success bool, response time).
        """
        start_time = time.time()

        if not self.available or not self.client:
            response_time = time.time() - start_time
            return {}, False, response_time

        try:
            metadata = file_info.get("metadata", {})
            query = ""
            if metadata.get("artist"):
                query += f"artist:{metadata['artist']} "
            if metadata.get("title"):
                query += f"track:{metadata['title']}"

            if not query.strip():
                response_time = time.time() - start_time
                return {}, False, response_time

            results = self.client.search(q=query, type="track", limit=1)

            if results and results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                new_metadata = self._parse_spotify_track(track)
                response_time = time.time() - start_time
                return new_metadata, True, response_time

            response_time = time.time() - start_time
            return {}, False, response_time

        except Exception as e:
            print(f"Error getting Spotify metadata: {str(e)}")
            response_time = time.time() - start_time
            return {}, False, response_time

    def _parse_spotify_track(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Spotify track data.

        Args:
            track (Dict[str, Any]): Spotify track data.

        Returns:
            Dict[str, Any]: Parsed metadata.
        """
        new_metadata = {}

        if "name" in track:
            new_metadata["title"] = track["name"]

        if "artists" in track and track["artists"]:
            new_metadata["artist"] = track["artists"][0]["name"]

        if "album" in track:
            new_metadata["album"] = track["album"]["name"]
            if "release_date" in track["album"]:
                new_metadata["year"] = track["album"]["release_date"][:4]

            # Get cover art URL
            if "images" in track["album"] and track["album"]["images"]:
                # Get the largest image (usually the first one)
                new_metadata["cover_art_url"] = track["album"]["images"][0]["url"]

        return new_metadata


class LastFmSource(MetadataSource):
    """Last.fm metadata source."""

    def __init__(self) -> None:
        """Initialize the Last.fm source."""
        super().__init__("Last.fm")
        self.available = HAS_LASTFM
        self.network = None
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

    def get_metadata(self, file_info: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, float]:
        """
        Get metadata from Last.fm.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            Tuple[Dict[str, Any], bool, float]: (metadata dict, success bool, response time).
        """
        start_time = time.time()

        if not self.available or not self.network:
            response_time = time.time() - start_time
            return {}, False, response_time

        try:
            metadata = file_info.get("metadata", {})
            artist_name = metadata.get("artist")
            title_name = metadata.get("title")

            if not artist_name or not title_name:
                response_time = time.time() - start_time
                return {}, False, response_time

            track = self.network.get_track(artist_name, title_name)

            # Verify track exists by getting duration (or other field)
            # pylast loads lazily, so we need to access a property to trigger request
            if not track.get_duration():
                response_time = time.time() - start_time
                return {}, False, response_time

            new_metadata = {}
            # Tags as Genre
            tags = track.get_top_tags(limit=1)
            if tags:
                new_metadata["genre"] = tags[0].item.get_name().title()

            # Album
            album = track.get_album()
            if album:
                new_metadata["album"] = album.get_name()
                # Get cover art URL
                image_url = album.get_cover_image(size=pylast.SIZE_EXTRA_LARGE)
                if image_url:
                    new_metadata["cover_art_url"] = image_url

            response_time = time.time() - start_time
            return new_metadata, True, response_time

        except Exception as e:
            print(f"Error getting Last.fm metadata: {str(e)}")
            response_time = time.time() - start_time
            return {}, False, response_time


class MetadataService(QObject):
    """
    Service for fetching and updating music metadata from online sources.

    This service coordinates multiple metadata sources (MusicBrainz, Discogs, Spotify, Last.fm)
    to find and update metadata for music files. It handles threading, caching, and statistics.
    """

    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    metadata_updated = pyqtSignal(str, dict)  # file path, new metadata
    file_updated = pyqtSignal(str)  # file path currently being processed
    source_stats_updated = pyqtSignal(dict)  # source statistics
    lyrics_updated = pyqtSignal(str, bool)  # file path, success

    def __init__(self) -> None:
        """Initialize the MetadataService."""
        super().__init__()
        self.sources: Dict[str, MetadataSource] = {}
        self.source_order: List[str] = []
        self.learning_phase = True
        self.learning_count = 0
        self.learning_threshold = 100  # Number of files to process before finalizing source order
        self.stats_lock = threading.Lock()

        # Initialize sources
        self._init_sources()

        # Initialize bio service
        self.bio_service = BioService()

        # Initialize audio analyzer
        self.audio_analyzer = AudioAnalyzer()

        # Initialize cache service
        self.cache_service = CacheService()

        # Load saved statistics if available
        self._load_stats()

    def _init_sources(self) -> None:
        """Initialize metadata sources and default order."""
        # Add MusicBrainz source
        mb_source = MusicBrainzSource()
        self.sources[mb_source.name] = mb_source
        self.source_order.append(mb_source.name)

        # Add Discogs source
        discogs_source = DiscogsSource()
        self.sources[discogs_source.name] = discogs_source
        self.source_order.append(discogs_source.name)

        # Add Spotify source
        spotify_source = SpotifySource()
        self.sources[spotify_source.name] = spotify_source
        self.source_order.append(spotify_source.name)

        # Add Last.fm source
        lastfm_source = LastFmSource()
        self.sources[lastfm_source.name] = lastfm_source
        self.source_order.append(lastfm_source.name)

    def _load_stats(self) -> None:
        """Load saved source statistics from local file."""
        try:
            stats_file = Path.home() / ".auralis" / "source_stats.json"

            if stats_file.exists():
                with open(stats_file, "r") as f:
                    stats = json.load(f)

                # Update source statistics
                for source_name, source_stats in stats.items():
                    if source_name in self.sources:
                        source = self.sources[source_name]
                        source.success_count = source_stats.get("success_count", 0)
                        source.failure_count = source_stats.get("failure_count", 0)
                        source.total_count = source_stats.get("total_count", 0)
                        source.success_rate = source_stats.get("success_rate", 0.0)
                        source.avg_response_time = source_stats.get("avg_response_time", 0.0)
                        source.total_response_time = source.avg_response_time * source.total_count
                        source.enabled = source_stats.get("enabled", True)

                # Sort sources by success rate
                self._sort_sources()

                # Disable learning phase if we have enough data
                if (
                    sum(source.total_count for source in self.sources.values())
                    >= self.learning_threshold
                ):
                    self.learning_phase = False

        except Exception as e:
            print(f"Error loading source statistics: {str(e)}")

    def _save_stats(self) -> None:
        """Save source statistics to local file."""
        try:
            # Create directory if it doesn't exist
            stats_dir = Path.home() / ".auralis"
            stats_dir.mkdir(exist_ok=True)

            # Save statistics
            stats_file = stats_dir / "source_stats.json"

            stats = {}
            for source_name, source in self.sources.items():
                stats[source_name] = source.get_stats()

            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2)

        except Exception as e:
            print(f"Error saving source statistics: {str(e)}")

    def _sort_sources(self) -> None:
        """Sort sources by success rate in descending order."""
        with self.stats_lock:
            # Sort by success rate (descending)
            self.source_order = sorted(
                self.sources.keys(), key=lambda x: self.sources[x].success_rate, reverse=True
            )

    def update_metadata(
        self,
        music_files: List[Dict[str, Any]],
        options: Dict[str, Any],
        max_threads: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Update metadata for a list of music files.

        Args:
            music_files (List[Dict[str, Any]]): List of dictionaries containing file info.
            options (Dict[str, Any]): Metadata update options.
            max_threads (int): Maximum number of threads to use.

        Returns:
            List[Dict[str, Any]]: Updated music files.
        """
        self._update_api_keys(options)

        total_files = len(music_files)
        files_to_process, processed_count = self._filter_files_for_update(
            music_files, options, total_files
        )

        # Process files
        self._execute_updates(
            files_to_process,
            music_files,
            options,
            max_threads,
            processed_count,
            total_files,
        )

        self._save_stats()

        stats = {name: source.get_stats() for name, source in self.sources.items()}
        self.source_stats_updated.emit(stats)

        return music_files

    def _update_api_keys(self, options: Dict[str, Any]) -> None:
        """Update API keys for sources from options."""
        if "acoustid_api_key" in options and options["acoustid_api_key"]:
            if "MusicBrainz/AcoustID" in self.sources:
                mb_source = cast(MusicBrainzSource, self.sources["MusicBrainz/AcoustID"])
                mb_source.acoustid_api_key = options["acoustid_api_key"]

        if "discogs_token" in options and options["discogs_token"]:
            if "Discogs" in self.sources:
                discogs_source = cast(DiscogsSource, self.sources["Discogs"])
                discogs_source.discogs_token = options["discogs_token"]
                try:
                    discogs_source.client = discogs_client.Client(
                        "Auralis/0.1", user_token=discogs_source.discogs_token
                    )
                    discogs_source.available = True
                except Exception as e:
                    print(f"Error initializing Discogs client: {str(e)}")
                    discogs_source.available = False

    def _filter_files_for_update(
        self,
        music_files: List[Dict[str, Any]],
        options: Dict[str, Any],
        total_files: int,
    ) -> Tuple[List[Tuple[int, Dict[str, Any]]], int]:
        """Filter files that need metadata updates."""
        files_to_process = []
        processed_count = 0

        for i, file_info in enumerate(music_files):
            file_hash = file_info.get("hash")
            cached_metadata = None
            if file_hash and not options.get("force_update", False):
                cached_metadata = self.cache_service.get_metadata(file_hash)

            if cached_metadata:
                file_info["metadata"].update(cached_metadata)
                self.file_updated.emit(f"Using cached metadata for: {file_info['path']}")
                processed_count += 1
                self.progress_updated.emit(processed_count, total_files)

            elif not self._has_sufficient_metadata(file_info) or options.get("force_update", False):
                files_to_process.append((i, file_info))

            else:
                processed_count += 1
                self.progress_updated.emit(processed_count, total_files)

        return files_to_process, processed_count

    def _execute_updates(
        self,
        files_to_process: List[Tuple[int, Dict[str, Any]]],
        music_files: List[Dict[str, Any]],
        options: Dict[str, Any],
        max_threads: int,
        start_processed_count: int,
        total_files: int,
    ) -> None:
        """Execute metadata updates in parallel threads."""
        processed_container = [start_processed_count]

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {
                executor.submit(
                    self._process_file_with_cache,
                    file_info,
                    options,
                ): orig_index
                for orig_index, file_info in files_to_process
            }

            for future in concurrent.futures.as_completed(futures):
                orig_index = futures[future]
                try:
                    updated_file_info = future.result()
                    if updated_file_info:
                        music_files[orig_index] = updated_file_info
                except Exception as e:
                    print(f"Error processing file index {orig_index}: {str(e)}")
                finally:
                    processed_container[0] += 1
                    self.progress_updated.emit(processed_container[0], total_files)

    def _process_file_with_cache(
        self,
        file_info: Dict[str, Any],
        options: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Process a file with caching support."""
        try:
            # Process the file
            updated_file_info = self._process_file_internal(file_info, options)

            # Update cache with new metadata
            if updated_file_info and "hash" in updated_file_info:
                file_hash = updated_file_info["hash"]
                if file_hash and "metadata" in updated_file_info:
                    self.cache_service.save_metadata(
                        file_hash, updated_file_info["metadata"]
                    )

            return updated_file_info

        except Exception as e:
            print(f"Error processing file {file_info['path']}: {str(e)}")
            return file_info

    def _process_file_internal(
        self, file_info: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Internal method to process a single file."""
        # Emit signal to indicate which file is being processed
        self.file_updated.emit(file_info["path"])

        # Skip if file already has sufficient metadata
        if self._has_sufficient_metadata(file_info) and not options.get("force_update", False):
            return file_info

        metadata = file_info.get("metadata", {})
        active_sources = self._get_active_sources(options)

        new_metadata = self._query_sources(active_sources, file_info, metadata)

        if self.learning_phase:
            self._update_learning_phase()

        # Update file metadata
        if new_metadata:
            updated_metadata = {**metadata, **new_metadata}
            file_info["metadata"] = updated_metadata
            self._finalize_file_update(file_info, updated_metadata, options)

        return file_info

    def _get_active_sources(self, options: Dict[str, Any]) -> List[MetadataSource]:
        """Get list of active metadata sources based on options and learning phase."""
        source_names = []
        if options.get("use_musicbrainz", True):
            source_names.append("MusicBrainz/AcoustID")
        if options.get("use_discogs", True):
            source_names.append("Discogs")

        if self.learning_phase:
            return [self.sources[name] for name in source_names if name in self.sources]

        return [
            self.sources[name]
            for name in self.source_order
            if name in source_names and name in self.sources
        ]

    def _query_sources(
        self,
        active_sources: List[MetadataSource],
        file_info: Dict[str, Any],
        current_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Query active sources for metadata."""
        new_metadata = {}
        for source in active_sources:
            if not source.enabled:
                continue

            # Update signal with current source
            self.file_updated.emit(f"{file_info['path']} (querying {source.name})")

            source_metadata, success, response_time = source.get_metadata(file_info)

            # Update source statistics
            with self.stats_lock:
                source.update_stats(success, response_time)

            if success and source_metadata:
                new_metadata.update(source_metadata)

                # If we have sufficient metadata, stop trying other sources
                if self._has_sufficient_metadata(
                    {"metadata": {**current_metadata, **new_metadata}}
                ):
                    break
        return new_metadata

    def _update_learning_phase(self) -> None:
        """Update learning phase progress."""
        with self.stats_lock:
            self.learning_count += 1
            if self.learning_count >= self.learning_threshold:
                self.learning_phase = False
                self._sort_sources()

    def _finalize_file_update(
        self, file_info: Dict[str, Any], metadata: Dict[str, Any], options: Dict[str, Any]
    ) -> None:
        """Finalize file update by downloading cover art, embedding lyrics, and applying tags."""
        # Fetch cover art
        if options.get("fetch_cover_art", False) and "cover_art_url" in metadata:
            self._download_cover_art(file_info, metadata, options)

        # Apply metadata to file
        self.file_updated.emit(f"{file_info['path']} (updating file)")
        self._apply_metadata_to_file(file_info["path"], metadata)

        # Fetch and embed lyrics if enabled
        if options.get("fetch_lyrics", False):
            self.file_updated.emit(f"{file_info['path']} (fetching lyrics)")
            self._fetch_and_embed_lyrics(
                file_info["path"], metadata, options.get("save_lrc", False)
            )

        # Fetch bio if enabled
        if options.get("fetch_bio", False) and "artist" in metadata:
            self.file_updated.emit(f"{file_info['path']} (fetching artist bio)")
            bio = self.bio_service.get_artist_bio(metadata["artist"])
            if bio:
                metadata["bio"] = bio

        # Analyze audio if enabled
        if options.get("analyze_audio", False):
            self.file_updated.emit(f"{file_info['path']} (analyzing audio)")
            self._analyze_audio(file_info, metadata)

        # Emit signal
        self.metadata_updated.emit(file_info["path"], metadata)

    def _analyze_audio(self, file_info: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Analyze audio for BPM, Key, and Mood.

        Args:
            file_info (Dict[str, Any]): File information.
            metadata (Dict[str, Any]): Metadata dictionary to update.
        """
        path = file_info["path"]

        bpm = self._parse_bpm(metadata.get("bpm"))
        key = metadata.get("key")
        mood = metadata.get("mood")

        bpm, key, mood, changed = self._perform_analysis(path, bpm, key, mood)

        if changed:
            metadata["bpm"] = bpm
            metadata["key"] = key
            metadata["mood"] = mood
            self.audio_analyzer.save_analysis_tags(path, bpm, key, mood)

    def _parse_bpm(self, bpm_value: Any) -> Optional[float]:
        """Parse BPM value to float."""
        if bpm_value:
            try:
                return float(bpm_value)
            except (ValueError, TypeError):
                pass
        return None

    def _perform_analysis(
        self, path: str, bpm: Optional[float], key: Optional[str], mood: Optional[str]
    ) -> Tuple[Optional[float], Optional[str], Optional[str], bool]:
        """Perform analysis if values are missing."""
        changed = False

        if not bpm:
            bpm = self.audio_analyzer.get_bpm(path)
            if bpm:
                changed = True

        if not key:
            key = self.audio_analyzer.get_key(path)
            if key:
                changed = True

        if not mood and bpm and key:
            mood = self.audio_analyzer.get_mood(bpm, key)
            if mood:
                changed = True

        return bpm, key, mood, changed

    def _download_cover_art(
        self, file_info: Dict[str, Any], metadata: Dict[str, Any], options: Dict[str, Any]
    ) -> None:
        """Download cover art from URL."""
        self.file_updated.emit(f"{file_info['path']} (downloading cover art)")
        try:
            min_size = options.get("min_cover_art_size", (500, 500))
            # Ensure tuple if list passed from JSON config
            if isinstance(min_size, list):
                min_size = tuple(min_size)

            result = AlbumArtFetcher.fetch_art(metadata["cover_art_url"], min_size=min_size)

            if result:
                image_data, mime_type = result
                metadata["cover_art"] = image_data
                metadata["cover_art_mime"] = mime_type
            else:
                print(
                    f"Cover art fetch failed or skipped (size/error): {metadata['cover_art_url']}"
                )

        except Exception as e:
            print(f"Error downloading cover art: {str(e)}")

    def _has_sufficient_metadata(self, file_info: Dict[str, Any]) -> bool:
        """
        Check if a file has sufficient metadata.

        Args:
            file_info (Dict[str, Any]): File information.

        Returns:
            bool: True if file has sufficient metadata.
        """
        metadata = file_info.get("metadata", {})

        # Check for essential fields
        essential_fields = ["artist", "title", "album"]
        for field in essential_fields:
            if (
                field not in metadata
                or not metadata[field]
                or metadata[field].lower() == f"unknown {field}"
            ):
                return False

        return True

    def _apply_metadata_to_file(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Apply metadata to a music file.

        Args:
            file_path (str): Path to the music file.
            metadata (Dict[str, Any]): Metadata to apply.

        Returns:
            bool: True if successful.
        """
        try:
            audio = mutagen.File(file_path)

            if not audio:
                return False

            if isinstance(audio, mutagen.mp3.MP3):
                self._apply_id3_tags(audio, metadata)
            elif isinstance(audio, mutagen.flac.FLAC):
                self._apply_vorbis_tags(audio, metadata)
            else:
                self._apply_generic_tags(audio, metadata)

            audio.save()
            return True

        except Exception as e:
            print(f"Error applying metadata to {file_path}: {str(e)}")
            return False

    def _apply_id3_tags(self, audio: Any, metadata: Dict[str, Any]) -> None:
        """Apply ID3 tags to MP3 file."""
        if "artist" in metadata:
            audio["TPE1"] = mutagen.id3.TPE1(encoding=3, text=metadata["artist"])
        if "title" in metadata:
            audio["TIT2"] = mutagen.id3.TIT2(encoding=3, text=metadata["title"])
        if "album" in metadata:
            audio["TALB"] = mutagen.id3.TALB(encoding=3, text=metadata["album"])
        if "year" in metadata:
            audio["TDRC"] = mutagen.id3.TDRC(encoding=3, text=metadata["year"])
        if "genre" in metadata:
            audio["TCON"] = mutagen.id3.TCON(encoding=3, text=metadata["genre"])
        if "track" in metadata:
            audio["TRCK"] = mutagen.id3.TRCK(encoding=3, text=metadata["track"])

        if "bio" in metadata:
            # Add bio as comment (eng)
            audio["COMM::eng"] = mutagen.id3.COMM(
                encoding=3, lang="eng", desc="Bio", text=metadata["bio"]
            )

        if "cover_art" in metadata:
            mime = metadata.get("cover_art_mime", "image/jpeg")
            audio["APIC"] = mutagen.id3.APIC(
                encoding=3,
                mime=mime,
                type=3,  # Cover (front)
                desc="Cover",
                data=metadata["cover_art"],
            )

    def _apply_vorbis_tags(self, audio: Any, metadata: Dict[str, Any]) -> None:
        """Apply Vorbis tags to FLAC file."""
        if "artist" in metadata:
            audio["artist"] = metadata["artist"]
        if "title" in metadata:
            audio["title"] = metadata["title"]
        if "album" in metadata:
            audio["album"] = metadata["album"]
        if "year" in metadata:
            audio["date"] = metadata["year"]
        if "genre" in metadata:
            audio["genre"] = metadata["genre"]
        if "track" in metadata:
            audio["tracknumber"] = metadata["track"]

        if "bio" in metadata:
            audio["DESCRIPTION"] = metadata["bio"]

        if "cover_art" in metadata:
            picture = mutagen.flac.Picture()
            picture.data = metadata["cover_art"]
            picture.mime = metadata.get("cover_art_mime", "image/jpeg")
            picture.type = 3  # Cover (front)
            picture.desc = "Cover"
            audio.add_picture(picture)

    def _apply_generic_tags(self, audio: Any, metadata: Dict[str, Any]) -> None:
        """Apply generic tags to supported file types."""
        for key, value in metadata.items():
            if key in ["artist", "title", "album", "year", "genre", "track"]:
                audio[key] = value
            elif key == "bio":
                audio["comment"] = value

    def _fetch_and_embed_lyrics(
        self, file_path: str, metadata: Dict[str, Any], save_lrc: bool = False
    ) -> bool:
        """
        Fetch and embed lyrics for a file.

        Args:
            file_path (str): Path to the music file.
            metadata (Dict[str, Any]): File metadata.
            save_lrc (bool): Whether to save lyrics to an .lrc file.

        Returns:
            bool: True if successful.
        """
        artist = metadata.get("artist", "")
        title = metadata.get("title", "")

        if not artist or not title:
            self.lyrics_updated.emit(file_path, False)
            return False

        # Fetch lyrics
        lyrics = fetch_lyrics(artist, title)
        if not lyrics:
            self.lyrics_updated.emit(file_path, False)
            return False

        # Embed lyrics
        success = embed_lyrics(file_path, lyrics, save_lrc_file=save_lrc)

        # Save lyrics to metadata
        if success:
            metadata["lyrics"] = lyrics

        self.lyrics_updated.emit(file_path, success)
        return success

    def detect_language(self, music_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect the language of music files based on genre and metadata.

        Args:
            music_files (List[Dict[str, Any]]): List of dictionaries containing file info.

        Returns:
            List[Dict[str, Any]]: Updated music files with language information.
        """
        # Keyword to language mapping
        genre_language_map = {
            "Japanese": ["j-pop", "j-rock", "jpop", "japanese"],
            "Korean": ["k-pop", "k-rock", "kpop", "korean"],
            "Chinese": ["mandopop", "c-pop", "chinese"],
            "Hindi": ["bollywood", "bhangra", "hindi"],
            "Spanish": ["latin", "salsa", "reggaeton", "spanish"],
            "French": ["chanson", "french"],
            "German": ["schlager", "german"],
            "Instrumental": ["instrumental"],
        }

        for file_info in music_files:
            metadata = file_info.get("metadata", {})

            # Check if language is already set
            if "language" in metadata:
                continue

            # Try to detect language based on metadata
            language = "English"  # Default to English for most Western music

            genre = metadata.get("genre", "").lower()
            if genre:
                # Check for exact match for instrumental first to match legacy behavior preference if strictly needed
                # or just rely on map. The map approach "instrumental" in genre covers "instrumental"

                for lang, keywords in genre_language_map.items():
                    if any(kw in genre for kw in keywords):
                        language = lang
                        break

                # Special handling for exact "instrumental" if not caught by map (though it should be)
                # or if we want to ensure "instrumental rock" -> English but "instrumental" -> Instrumental
                # The previous code had `elif genre == "instrumental":` which implies exact match.
                # But "instrumental" in map covers it.

                if language == "English" and genre == "instrumental":
                    language = "Instrumental"

            # Update metadata
            metadata["language"] = language
            file_info["metadata"] = metadata

        return music_files
