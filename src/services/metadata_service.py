"""
Auralis - Metadata Service Module

Handles fetching and updating metadata from online sources
"""

import json
import os
import threading
import time
from pathlib import Path

import acoustid
import discogs_client
import musicbrainzngs
import mutagen
from PyQt6.QtCore import QObject, pyqtSignal

# Import lyrics service
from src.services.lyrics_service import embed_lyrics, fetch_lyrics

# Optional dependencies
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    HAS_SPOTIFY = True
except ImportError:
    HAS_SPOTIFY = False

try:
    import pylast

    HAS_LASTFM = True
except ImportError:
    HAS_LASTFM = False


class MetadataSource:
    """Base class for metadata sources"""

    def __init__(self, name):
        self.name = name
        self.success_count = 0
        self.failure_count = 0
        self.total_count = 0
        self.success_rate = 0.0
        self.avg_response_time = 0.0
        self.total_response_time = 0.0
        self.enabled = True

    def get_metadata(self, file_info):
        """Get metadata for a file"""
        raise NotImplementedError("Subclasses must implement get_metadata")

    def update_stats(self, success, response_time):
        """Update source statistics"""
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

    def get_stats(self):
        """Get source statistics"""
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
    """MusicBrainz/AcoustID metadata source"""

    def __init__(self):
        super().__init__("MusicBrainz/AcoustID")

        # Set up MusicBrainz client
        musicbrainzngs.set_useragent("Auralis", "0.1", "https://github.com/patternseekers/auralis")

        # AcoustID API key (should be configurable)
        self.acoustid_api_key = "1vOwZtEn"  # Example API key, register at https://acoustid.org/
        self.fingerprinting_available = self._check_fingerprinting()

    def _check_fingerprinting(self):
        """Check if audio fingerprinting is available"""
        try:
            import subprocess

            result = subprocess.run(
                ["fpcalc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            return result.returncode == 0
        except BaseException:
            return False

    def get_metadata(self, file_info):
        """
        Get metadata from MusicBrainz/AcoustID

        Args:
            file_info (dict): File information

        Returns:
            tuple: (metadata dict, success bool, response time)
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

    def _get_metadata_by_fingerprint(self, file_info):
        """Get metadata using audio fingerprinting"""
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

    def _fetch_musicbrainz_details(self, mb_id):
        """Fetch detailed metadata from MusicBrainz by ID"""
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

    def _get_metadata_by_search(self, file_info):
        """Get metadata using text search"""
        metadata = file_info.get("metadata", {})

        if "artist" in metadata and "title" in metadata:
            query = f'artist:"{metadata["artist"]}" AND recording:"{metadata["title"]}"'
            results = musicbrainzngs.search_recordings(query=query, limit=1)

            if results and "recording-list" in results and results["recording-list"]:
                recording = results["recording-list"][0]
                return self._parse_musicbrainz_response(recording)

        return None

    def _parse_musicbrainz_response(self, recording):
        """Parse MusicBrainz recording data into metadata dict"""
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
    """Discogs metadata source"""

    def __init__(self):
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

    def get_metadata(self, file_info):
        """
        Get metadata from Discogs

        Args:
            file_info (dict): File information

        Returns:
            tuple: (metadata dict, success bool, response time)
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

    def _get_metadata_by_search(self, file_info):
        """Get metadata from Discogs using text search"""
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

    def _parse_discogs_release(self, release, current_metadata):
        """Parse Discogs release into metadata dict"""
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
    """Spotify metadata source"""

    def __init__(self):
        super().__init__("Spotify")
        self.available = HAS_SPOTIFY
        self.client = None
        self._init_client()

    def _init_client(self):
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

    def get_metadata(self, file_info):
        """Get metadata from Spotify"""
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

    def _parse_spotify_track(self, track):
        """Parse Spotify track data"""
        new_metadata = {}

        if "name" in track:
            new_metadata["title"] = track["name"]

        if "artists" in track and track["artists"]:
            new_metadata["artist"] = track["artists"][0]["name"]

        if "album" in track:
            new_metadata["album"] = track["album"]["name"]
            if "release_date" in track["album"]:
                new_metadata["year"] = track["album"]["release_date"][:4]

        return new_metadata


class LastFmSource(MetadataSource):
    """Last.fm metadata source"""

    def __init__(self):
        super().__init__("Last.fm")
        self.available = HAS_LASTFM
        self.network = None
        self._init_network()

    def _init_network(self):
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

    def get_metadata(self, file_info):
        """Get metadata from Last.fm"""
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

            response_time = time.time() - start_time
            return new_metadata, True, response_time

        except Exception as e:
            print(f"Error getting Last.fm metadata: {str(e)}")
            response_time = time.time() - start_time
            return {}, False, response_time


class MetadataService(QObject):
    """
    Service for fetching and updating music metadata from online sources
    """

    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    metadata_updated = pyqtSignal(str, dict)  # file path, new metadata
    file_updated = pyqtSignal(str)  # file path currently being processed
    source_stats_updated = pyqtSignal(dict)  # source statistics
    lyrics_updated = pyqtSignal(str, bool)  # file path, success

    def __init__(self):
        super().__init__()
        self.sources = {}
        self.source_order = []
        self.learning_phase = True
        self.learning_count = 0
        self.learning_threshold = 100  # Number of files to process before finalizing source order
        self.stats_lock = threading.Lock()

        # Initialize sources
        self._init_sources()

        # Load saved statistics if available
        self._load_stats()

    def _init_sources(self):
        """Initialize metadata sources"""
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

    def _load_stats(self):
        """Load saved source statistics"""
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

    def _save_stats(self):
        """Save source statistics"""
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

    def _sort_sources(self):
        """Sort sources by success rate"""
        with self.stats_lock:
            # Sort by success rate (descending)
            self.source_order = sorted(
                self.sources.keys(), key=lambda x: self.sources[x].success_rate, reverse=True
            )

    def update_metadata(self, music_files, options, max_threads=4):
        """
        Update metadata for a list of music files

        Args:
            music_files (list): List of dictionaries containing file info
            options (dict): Metadata update options
            max_threads (int): Maximum number of threads to use

        Returns:
            list: Updated music files
        """
        # Use cache to avoid re-processing files
        cache_file = Path.home() / ".auralis" / "metadata_cache.json"
        metadata_cache = {}

        # Ensure cache directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)

        # Load cache if it exists
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    metadata_cache = json.load(f)
            except Exception as e:
                print(f"Error loading metadata cache: {str(e)}")

        # Update API keys if provided in options
        if "acoustid_api_key" in options and options["acoustid_api_key"]:
            for source_name, source in self.sources.items():
                if source_name == "MusicBrainz/AcoustID":
                    source.acoustid_api_key = options["acoustid_api_key"]

        if "discogs_token" in options and options["discogs_token"]:
            for source_name, source in self.sources.items():
                if source_name == "Discogs":
                    source.discogs_token = options["discogs_token"]
                    # Re-initialize Discogs client with new token
                    try:
                        source.client = discogs_client.Client(
                            "Auralis/0.1", user_token=source.discogs_token
                        )
                        source.available = True
                    except Exception as e:
                        print(f"Error initializing Discogs client: {str(e)}")
                        source.available = False

        total_files = len(music_files)
        processed_files = [0]

        # Filter files that need metadata update
        files_to_process = []
        for i, file_info in enumerate(music_files):
            # Check if file hash exists in cache and has sufficient metadata
            file_hash = file_info.get("hash")
            if file_hash and file_hash in metadata_cache and not options.get("force_update", False):
                cached_metadata = metadata_cache[file_hash]
                # Update file_info with cached metadata
                file_info["metadata"].update(cached_metadata)
                self.file_updated.emit(f"Using cached metadata for: {file_info['path']}")
                processed_files[0] += 1
                self.progress_updated.emit(processed_files[0], total_files)
            elif not self._has_sufficient_metadata(file_info) or options.get("force_update", False):
                # File needs metadata update
                files_to_process.append((i, file_info))
            else:
                # File has sufficient metadata
                processed_files[0] += 1
                self.progress_updated.emit(processed_files[0], total_files)

        # Create thread pool
        threads = []
        results = [None] * len(files_to_process)
        thread_semaphore = threading.Semaphore(max_threads)

        # Process each file
        for i, (orig_index, file_info) in enumerate(files_to_process):
            # Create thread for processing
            thread = threading.Thread(
                target=self._process_file_with_cache,
                args=(
                    file_info,
                    options,
                    i,
                    results,
                    thread_semaphore,
                    processed_files,
                    total_files,
                    orig_index,
                    metadata_cache,
                ),
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Update music files with results
        for i, result in enumerate(results):
            if result is not None:
                orig_index, updated_file_info = result
                music_files[orig_index] = updated_file_info

        # Save cache
        try:
            with open(cache_file, "w") as f:
                json.dump(metadata_cache, f)
        except Exception as e:
            print(f"Error saving metadata cache: {str(e)}")

        # Save source statistics
        self._save_stats()

        # Emit source statistics
        stats = {name: source.get_stats() for name, source in self.sources.items()}
        self.source_stats_updated.emit(stats)

        return music_files

    def _process_file_with_cache(
        self,
        file_info,
        options,
        index,
        results,
        semaphore,
        processed_files,
        total_files,
        orig_index,
        metadata_cache,
    ):
        """Process a file with caching support"""
        # Acquire semaphore
        semaphore.acquire()

        try:
            # Process the file
            updated_file_info = self._process_file_internal(
                file_info, options, processed_files, total_files
            )

            # Update cache with new metadata
            if updated_file_info and "hash" in updated_file_info:
                file_hash = updated_file_info["hash"]
                if file_hash and "metadata" in updated_file_info:
                    metadata_cache[file_hash] = updated_file_info["metadata"]

            # Store result
            results[index] = (orig_index, updated_file_info)

        except Exception as e:
            print(f"Error processing file {file_info['path']}: {str(e)}")
            results[index] = (orig_index, file_info)
            processed_files[0] += 1
            self.progress_updated.emit(processed_files[0], total_files)

        finally:
            # Release semaphore
            semaphore.release()

    def _process_file_internal(self, file_info, options, processed_files, total_files):
        """Internal method to process a single file"""
        # Emit signal to indicate which file is being processed
        self.file_updated.emit(file_info["path"])

        # Skip if file already has sufficient metadata
        if self._has_sufficient_metadata(file_info) and not options.get("force_update", False):
            processed_files[0] += 1
            self.progress_updated.emit(processed_files[0], total_files)
            return file_info

        # Get existing metadata
        metadata = file_info.get("metadata", {})

        # Determine which sources to use
        source_names = []
        if options.get("use_musicbrainz", True):
            source_names.append("MusicBrainz/AcoustID")
        if options.get("use_discogs", True):
            source_names.append("Discogs")

        # If in learning phase, use all sources
        if self.learning_phase:
            active_sources = [self.sources[name] for name in source_names if name in self.sources]
        else:
            # Use sources in order of success rate
            active_sources = [
                self.sources[name]
                for name in self.source_order
                if name in source_names and name in self.sources
            ]

        # Try each source until we get metadata
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
                if self._has_sufficient_metadata({"metadata": {**metadata, **new_metadata}}):
                    break

        # Update learning phase counter
        if self.learning_phase:
            with self.stats_lock:
                self.learning_count += 1
                if self.learning_count >= self.learning_threshold:
                    self.learning_phase = False
                    self._sort_sources()

        # Update file metadata
        if new_metadata:
            # Merge with existing metadata, prioritizing new data
            updated_metadata = {**metadata, **new_metadata}
            file_info["metadata"] = updated_metadata

            # Apply metadata to file
            self.file_updated.emit(f"{file_info['path']} (updating file)")
            self._apply_metadata_to_file(file_info["path"], updated_metadata)

            # Fetch and embed lyrics if enabled
            if options.get("fetch_lyrics", False):
                self.file_updated.emit(f"{file_info['path']} (fetching lyrics)")
                self._fetch_and_embed_lyrics(file_info["path"], updated_metadata)

            # Emit signal
            self.metadata_updated.emit(file_info["path"], updated_metadata)

        # Update progress
        processed_files[0] += 1
        self.progress_updated.emit(processed_files[0], total_files)

        return file_info

    def _has_sufficient_metadata(self, file_info):
        """
        Check if a file has sufficient metadata

        Args:
            file_info (dict): File information

        Returns:
            bool: True if file has sufficient metadata
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

    def _apply_metadata_to_file(self, file_path, metadata):
        """
        Apply metadata to a music file

        Args:
            file_path (str): Path to the music file
            metadata (dict): Metadata to apply

        Returns:
            bool: True if successful
        """
        try:
            audio = mutagen.File(file_path)

            if not audio:
                return False

            # Apply metadata based on file type
            if isinstance(audio, mutagen.mp3.MP3):
                # MP3 files (ID3 tags)
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

            elif isinstance(audio, mutagen.flac.FLAC):
                # FLAC files
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

            else:
                # Generic approach for other formats
                for key, value in metadata.items():
                    if key in ["artist", "title", "album", "year", "genre", "track"]:
                        audio[key] = value

            audio.save()
            return True

        except Exception as e:
            print(f"Error applying metadata to {file_path}: {str(e)}")
            return False

    def _fetch_and_embed_lyrics(self, file_path, metadata):
        """
        Fetch and embed lyrics for a file

        Args:
            file_path (str): Path to the music file
            metadata (dict): File metadata

        Returns:
            bool: True if successful
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
        success = embed_lyrics(file_path, lyrics)

        # Save lyrics to metadata
        if success:
            metadata["lyrics"] = lyrics

        self.lyrics_updated.emit(file_path, success)
        return success

    def detect_language(self, music_files):
        """
        Detect the language of music files

        Args:
            music_files (list): List of dictionaries containing file info

        Returns:
            list: Updated music files with language information
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
