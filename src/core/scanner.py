"""
Auralis - Music Scanner Module
"""

import hashlib
import os
import time

import mutagen
from PyQt6.QtCore import QObject, pyqtSignal


class MusicScanner(QObject):
    """
    Scans directories for music files and extracts basic metadata
    """

    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    file_found = pyqtSignal(dict)  # file info dictionary
    file_scanned = pyqtSignal(str)  # file path currently being processed
    scan_completed = pyqtSignal(list)  # list of music files

    # Default supported music file extensions
    DEFAULT_EXTENSIONS = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma", ".aiff"}

    # Default directory exclusion patterns
    DEFAULT_EXCLUDE_PATTERNS = [
        "$RECYCLE.BIN",
        "System Volume Information",
        "Windows",
        ".git",
        ".vscode",
        "node_modules",
        ".idea",
        "tmp",
        "temp",
    ]

    def __init__(self):
        super().__init__()
        self.files = []
        self.supported_extensions = self.DEFAULT_EXTENSIONS.copy()
        self.exclude_patterns = self.DEFAULT_EXCLUDE_PATTERNS.copy()
        self.max_scan_depth = 10  # Default max directory depth

    def scan_directories(self, directories, options=None):
        """
        Scan a list of directories for music files

        Args:
            directories (list): List of directory paths to scan
            options (dict, optional): Scan options including:
                - file_extensions (list): List of file extensions to include
                - exclude_patterns (list): Directory patterns to exclude
                - max_scan_depth (int): Maximum directory depth to scan

        Returns:
            list: List of dictionaries containing file info
        """
        self.files = []
        total_files = 0
        processed_files = 0

        # Update scanner options if provided
        self._update_options(options)

        # First pass: count total files (with optimization)
        for directory in directories:
            total_files += self._count_music_files(directory)

        # If no files found, return empty list
        if total_files == 0:
            return []

        # Second pass: process files
        for directory in directories:
            for file_info in self._process_directory(directory, processed_files, total_files):
                self.files.append(file_info)
                processed_files += 1
                self.progress_updated.emit(processed_files, total_files)

        self.scan_completed.emit(self.files)
        return self.files

    def _update_options(self, options):
        """Update scanner configuration from options dictionary"""
        if not options:
            return

        # Set supported extensions
        if "file_extensions" in options:
            exts = options["file_extensions"]
            if isinstance(exts, str):
                # Convert comma-separated string to list
                exts = [ext.strip() for ext in exts.split(",")]

            # Ensure extensions start with a dot
            self.supported_extensions = {f".{ext.lstrip('.')}" for ext in exts}

        # Set exclude patterns
        if "exclude_patterns" in options:
            patterns = options["exclude_patterns"]
            if isinstance(patterns, str):
                # Convert comma-separated string to list
                patterns = [p.strip() for p in patterns.split(",")]

            self.exclude_patterns = patterns

        # Set max scan depth
        if "max_scan_depth" in options:
            self.max_scan_depth = int(options["max_scan_depth"])

    def _count_music_files(self, directory):
        """
        Count the number of music files in a directory tree

        Args:
            directory (str): Directory to scan

        Returns:
            int: Number of music files found
        """
        count = 0
        try:
            for root, dirs, files in os.walk(directory):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_dir(d)]

                # Check scan depth
                rel_path = os.path.relpath(root, directory)
                depth = len(rel_path.split(os.sep)) if rel_path != "." else 0
                if depth > self.max_scan_depth:
                    dirs[:] = []  # Stop descending
                    continue

                # Count music files
                for file in files:
                    if self._is_music_file(file):
                        count += 1
        except Exception as e:
            print(f"Error counting files in {directory}: {str(e)}")

        return count

    def _process_directory(self, directory, processed_files, total_files):
        """
        Process all music files in a directory tree

        Args:
            directory (str): Directory to scan
            processed_files (int): Number of files processed so far
            total_files (int): Total number of files to process

        Yields:
            dict: File information for each music file
        """
        try:
            for root, dirs, files in os.walk(directory):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_dir(d)]

                # Check scan depth
                rel_path = os.path.relpath(root, directory)
                depth = len(rel_path.split(os.sep)) if rel_path != "." else 0
                if depth > self.max_scan_depth:
                    dirs[:] = []  # Stop descending
                    continue

                # Process music files
                for file in files:
                    if self._is_music_file(file):
                        file_path = os.path.join(root, file)

                        # Emit signal for file being processed
                        self.file_scanned.emit(file_path)

                        # Extract file info
                        file_info = self._extract_file_info(file_path)
                        if file_info:
                            # Add file modification date
                            file_info["modified_date"] = self._get_modification_time(file_path)

                            # Add initial processing history
                            file_info["processing_history"] = [
                                {
                                    "stage": "Scan",
                                    "action": "File discovered",
                                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            ]

                            # Emit signal for file discovery with the complete file info
                            self.file_found.emit(file_info)

                            yield file_info

        except Exception as e:
            print(f"Error processing directory {directory}: {str(e)}")

    def _should_exclude_dir(self, dirname):
        """
        Check if a directory should be excluded

        Args:
            dirname (str): Directory name

        Returns:
            bool: True if directory should be excluded
        """
        # Check if directory starts with a dot (hidden)
        if dirname.startswith("."):
            return True

        # Check against exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.lower() in dirname.lower():
                return True

        return False

    def _is_music_file(self, filename):
        """Check if a file is a supported music file"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.supported_extensions

    def _get_modification_time(self, file_path):
        """Get the modification time of a file in human-readable format"""
        try:
            mtime = os.path.getmtime(file_path)
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        except Exception:
            return "Unknown"

    def _extract_file_info(self, file_path):
        """
        Extract basic information from a music file

        Args:
            file_path (str): Path to the music file

        Returns:
            dict: Dictionary containing file information
        """
        try:
            file_info = {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "extension": os.path.splitext(file_path)[1].lower(),
                "size": os.path.getsize(file_path),
                "hash": self._calculate_file_hash(file_path),
                "metadata": {},
            }

            self._extract_metadata(file_path, file_info)
            return file_info

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def _extract_metadata(self, file_path, file_info):
        """Helper to extract metadata and update file_info"""
        try:
            audio = mutagen.File(file_path)
            if audio:
                metadata = {}
                self._parse_audio_tags(audio, metadata)

                file_info["metadata"] = metadata

                # Try to extract artist and title from filename if not in metadata
                if "artist" not in metadata or "title" not in metadata:
                    artist, title = self._parse_filename(file_info["filename"])
                    if artist and "artist" not in metadata:
                        metadata["artist"] = artist
                    if title and "title" not in metadata:
                        metadata["title"] = title

        except Exception:
            # If metadata extraction fails, try to parse from filename
            artist, title = self._parse_filename(file_info["filename"])
            if artist or title:
                file_info["metadata"] = {
                    "artist": artist if artist else "Unknown Artist",
                    "title": title if title else "Unknown Title",
                }

    def _parse_audio_tags(self, audio, metadata):
        """Parse tags from mutagen audio object"""
        # MP3 files (ID3 tags)
        if isinstance(audio, mutagen.mp3.MP3):
            if "TPE1" in audio:  # Artist
                metadata["artist"] = str(audio["TPE1"])
            if "TIT2" in audio:  # Title
                metadata["title"] = str(audio["TIT2"])
            if "TALB" in audio:  # Album
                metadata["album"] = str(audio["TALB"])
            if "TDRC" in audio:  # Year
                metadata["year"] = str(audio["TDRC"])
            if "TCON" in audio:  # Genre
                metadata["genre"] = str(audio["TCON"])
            if "TRCK" in audio:  # Track number
                metadata["track"] = str(audio["TRCK"])

            # Get bitrate
            if audio.info:
                metadata["bitrate"] = audio.info.bitrate

        # FLAC files
        elif isinstance(audio, mutagen.flac.FLAC):
            if "artist" in audio:
                metadata["artist"] = str(audio["artist"][0])
            if "title" in audio:
                metadata["title"] = str(audio["title"][0])
            if "album" in audio:
                metadata["album"] = str(audio["album"][0])
            if "date" in audio:
                metadata["year"] = str(audio["date"][0])
            if "genre" in audio:
                metadata["genre"] = str(audio["genre"][0])
            if "tracknumber" in audio:
                metadata["track"] = str(audio["tracknumber"][0])

            # Get bitrate (approximate for FLAC)
            if audio.info:
                metadata["bitrate"] = audio.info.bits_per_sample * audio.info.sample_rate

        # Generic approach for other formats
        else:
            # Try to get common tag fields
            for key in ["artist", "title", "album", "date", "genre", "tracknumber"]:
                if key in audio:
                    metadata[key] = str(audio[key][0])

            # Try to get bitrate info
            if hasattr(audio.info, "bitrate"):
                metadata["bitrate"] = audio.info.bitrate

    def _calculate_file_hash(self, file_path, block_size=65536):
        """
        Calculate MD5 hash of a file

        Args:
            file_path (str): Path to the file
            block_size (int): Size of blocks to read

        Returns:
            str: MD5 hash of the file
        """
        try:
            hasher = hashlib.md5()
            with open(file_path, "rb") as f:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)
            return hasher.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {str(e)}")
            return None

    def _parse_filename(self, filename):
        """
        Try to parse artist and title from filename

        Args:
            filename (str): Filename to parse

        Returns:
            tuple: (artist, title) or (None, None) if parsing fails
        """
        # Remove extension
        name_without_ext = os.path.splitext(filename)[0]

        # Common patterns: "Artist - Title" or "Artist_-_Title"
        if " - " in name_without_ext:
            parts = name_without_ext.split(" - ", 1)
            return parts[0].strip(), parts[1].strip()
        elif "_-_" in name_without_ext:
            parts = name_without_ext.split("_-_", 1)
            return (parts[0].replace("_", " ").strip(), parts[1].replace("_", " ").strip())

        # No pattern match
        return None, None
