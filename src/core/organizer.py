"""
Auralis - Music Organizer Module
"""

import os
import shutil
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from src.utils.file_utils import ensure_dir_exists, format_filename, ensure_unique_filename, remove_empty_directories, sanitize_filename
# Import language detection service
from src.services.language_service import get_language_folder, is_available as is_language_detection_available
# Import audio similarity service
from src.services.audio_similarity_service import find_duplicates as find_similar_audio, get_best_quality_version, is_available as is_audio_similarity_available

class MusicOrganizer(QObject):
    """
    Organizes music files based on metadata and user preferences
    """
    
    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    file_organized = pyqtSignal(str, str)  # source path, destination path
    organization_completed = pyqtSignal()
    duplicate_found = pyqtSignal(str, str)  # best version, duplicate path
    
    def __init__(self, dry_run=False):
        super().__init__()
        self.dest_root = None
        self.options = {}
        self.dry_run = dry_run  # Whether this is a dry run (no actual file operations)
        self.processed_files = []  # List of source files that were processed
        # Check if language detection is available
        self.language_detection_available = is_language_detection_available()
        # Check if audio similarity detection is available
        self.audio_similarity_available = is_audio_similarity_available()
    
    def organize_files(self, music_files, dest_root, options):
        """
        Organize music files based on metadata and options
        
        Args:
            music_files (list): List of dictionaries containing file info
            dest_root (str): Root destination directory
            options (dict): Organization options
            
        Returns:
            dict: Summary of organization results
        """
        self.dest_root = dest_root
        self.options = options
        self.processed_files = []
        file_errors = {}  # Track errors by file path
        
        total_files = len(music_files)
        processed_files = 0
        
        # Create destination directories
        if not self.dry_run:
            self._create_destination_dirs()
        
        # Track duplicates
        duplicates = []
        audio_duplicates = []
        organized_files = []
        manual_review_files = []
        
        # Check for audio content similarity if enabled and available
        if self.options.get('detect_audio_similarity', False) and self.audio_similarity_available:
            self.progress_updated.emit(0, total_files)
            self.file_organized.emit("", "Analyzing audio content for similarities...")
            
            # Find duplicates based on audio content
            duplicate_groups = find_similar_audio(music_files)
            
            # Process each group
            for group in duplicate_groups:
                if len(group) > 1:
                    # Get the best quality version
                    best_version = get_best_quality_version(group)
                    
                    # Add other versions to audio duplicates
                    for duplicate in group:
                        if duplicate['path'] != best_version['path']:
                            audio_duplicates.append({
                                'original_path': best_version['path'],
                                'duplicate_path': duplicate['path'],
                                'reason': 'audio_similarity'
                            })
                            # Emit signal for duplicate found
                            self.duplicate_found.emit(best_version['path'], duplicate['path'])
            
            # Filter out audio duplicates from music_files to process
            if not options.get('keep_all_duplicates', False):
                duplicate_paths = set(d['duplicate_path'] for d in audio_duplicates)
                music_files = [f for f in music_files if f['path'] not in duplicate_paths]
                
                # Update total_files count
                total_files = len(music_files)
                
        # Process each file
        for file_info in music_files:
            try:
                # Check if this is a metadata duplicate (only if we're not checking audio similarity)
                if self.options.get('handle_duplicates', True) and not self.options.get('detect_audio_similarity', False):
                    duplicate = self._check_duplicate(file_info, organized_files)
                    
                    if duplicate:
                        # If we're handling duplicates, check quality
                        if not self._is_higher_quality(file_info, duplicate):
                            # Skip this file, it's lower quality
                            duplicates.append({
                                'original_path': file_info['path'],
                                'duplicate_path': duplicate['path'],
                                'reason': 'lower_quality'
                            })
                            processed_files += 1
                            self.progress_updated.emit(processed_files, total_files)
                            continue
                
                # Get destination path
                dest_path = self._get_destination_path(file_info)
                
                # Check if file needs manual review
                if self._needs_manual_review(file_info):
                    manual_review_path = os.path.join(self.dest_root, "Manual_Review")
                    
                    if not self.dry_run:
                        os.makedirs(manual_review_path, exist_ok=True)
                    
                    # Use original filename for manual review
                    dest_filename = file_info['filename']
                    dest_file_path = os.path.join(manual_review_path, dest_filename)
                    
                    # Ensure unique filename
                    dest_file_path = ensure_unique_filename(dest_file_path)
                    
                    # Move file
                    if not self.dry_run:
                        try:
                            shutil.copy2(file_info['path'], dest_file_path)
                        except Exception as e:
                            file_errors[file_info['path']] = f"Error copying to manual review: {str(e)}"
                    
                    manual_review_files.append({
                        'original_path': file_info['path'],
                        'review_path': dest_file_path
                    })
                    
                    # Track processed file
                    self.processed_files.append(file_info['path'])
                    
                    # Emit signal for dry run tracking
                    self.file_organized.emit(file_info['path'], dest_file_path)
                else:
                    # Create destination directory if it doesn't exist
                    if not self.dry_run:
                        try:
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        except Exception as e:
                            file_errors[file_info['path']] = f"Error creating directory: {str(e)}"
                            processed_files += 1
                            self.progress_updated.emit(processed_files, total_files)
                            continue
                    
                    # Move file
                    if not self.dry_run:
                        try:
                            shutil.copy2(file_info['path'], dest_path)
                        except Exception as e:
                            file_errors[file_info['path']] = f"Error copying file: {str(e)}"
                            processed_files += 1
                            self.progress_updated.emit(processed_files, total_files)
                            continue
                    
                    # Update organized files list
                    file_info['new_path'] = dest_path
                    organized_files.append(file_info)
                    
                    # Track processed file
                    self.processed_files.append(file_info['path'])
                    
                    # Emit signal for dry run tracking
                    self.file_organized.emit(file_info['path'], dest_path)
            except Exception as e:
                # Capture any errors that occur during processing this file
                file_errors[file_info['path']] = f"Error processing file: {str(e)}"
            
            processed_files += 1
            self.progress_updated.emit(processed_files, total_files)
        
        # Clean up by removing empty directories
        if not self.dry_run and options.get('remove_empty_dirs', True):
            try:
                removed_count = remove_empty_directories(self.dest_root)
                print(f"Removed {removed_count} empty directories")
            except Exception as e:
                file_errors["empty_dirs"] = f"Error removing empty directories: {str(e)}"
        
        self.organization_completed.emit()
        
        # Combine all duplicates
        all_duplicates = duplicates + audio_duplicates
        
        # Return summary
        return {
            'total_files': total_files + len(audio_duplicates),
            'organized_files': len(organized_files),
            'duplicates': len(all_duplicates),
            'audio_duplicates': len(audio_duplicates),
            'metadata_duplicates': len(duplicates),
            'manual_review': len(manual_review_files),
            'file_errors': file_errors
        }
    
    def _create_destination_dirs(self):
        """Create necessary destination directories"""
        # Base destination directory
        os.makedirs(self.dest_root, exist_ok=True)
        
        # Manual review directory
        os.makedirs(os.path.join(self.dest_root, "Manual_Review"), exist_ok=True)
        
        # For language-based organization, we'll create directories dynamically as needed
        # rather than pre-creating a fixed set of language folders
        if self.options.get('organize_by_language', True):
            # Create just the Unknown folder as a fallback
            os.makedirs(os.path.join(self.dest_root, "Unknown"), exist_ok=True)
    
    def _get_destination_path(self, file_info):
        """
        Determine the destination path for a file
        
        Args:
            file_info (dict): File information
            
        Returns:
            str: Destination path
        """
        metadata = file_info.get('metadata', {})
        
        # Use a flatter directory structure
        # If language organization is enabled, use language as the top-level directory
        if self.options.get('organize_by_language', True):
            # If language detection is available and enabled, use it to detect the language
            if self.language_detection_available and self.options.get('use_audio_language_detection', True):
                # Get the language folder based on audio content
                language_folder = get_language_folder(file_info['path'], default="Unknown")
            else:
                # Fallback to metadata-based language (usually not reliable)
                language = metadata.get('language', 'Unknown')
                # Ensure language folder names follow the strict naming conventions
                language_folder = sanitize_filename(language)
            
            # Create the language directory if it doesn't exist
            if not self.dry_run:
                lang_dir = os.path.join(self.dest_root, language_folder)
                os.makedirs(lang_dir, exist_ok=True)
                
            base_dir = os.path.join(self.dest_root, language_folder)
        else:
            base_dir = self.dest_root
        
        # Generate filename according to new pattern: "songname - artistname" or "songname - moviename"
        if self.options.get('rename_files', True):
            title = metadata.get('title', 'Unknown Title')
            artist = metadata.get('artist', None)
            album = metadata.get('album', None)  # Use album as potential "movie name"
            
            # Format filename using the new pattern
            filename = format_filename(
                title=title,
                artist=artist,
                movie=album,
                extension=file_info['extension']
            )
        else:
            filename = file_info['filename']
        
        # Full destination path
        dest_path = os.path.join(base_dir, filename)
        
        # Ensure unique filename
        return ensure_unique_filename(dest_path)
    
    def _check_duplicate(self, file_info, organized_files):
        """
        Check if a file is a duplicate of an already organized file
        
        Args:
            file_info (dict): File information
            organized_files (list): List of already organized files
            
        Returns:
            dict: Duplicate file info or None
        """
        # Check by hash (exact duplicate)
        for org_file in organized_files:
            if file_info['hash'] == org_file['hash']:
                return org_file
        
        # Check by metadata
        metadata = file_info.get('metadata', {})
        artist = metadata.get('artist')
        title = metadata.get('title')
        
        if artist and title:
            for org_file in organized_files:
                org_metadata = org_file.get('metadata', {})
                org_artist = org_metadata.get('artist')
                org_title = org_metadata.get('title')
                
                if artist == org_artist and title == org_title:
                    return org_file
        
        return None
    
    def _is_higher_quality(self, file_info, other_file):
        """
        Check if a file is higher quality than another
        
        Args:
            file_info (dict): File information
            other_file (dict): Other file information
            
        Returns:
            bool: True if file_info is higher quality
        """
        # Check format preference
        format_preference = {
            '.flac': 5,
            '.wav': 4,
            '.aiff': 3,
            '.m4a': 2,
            '.mp3': 1,
            '.ogg': 1,
            '.aac': 1,
            '.wma': 0
        }
        
        file_format = file_info['extension'].lower()
        other_format = other_file['extension'].lower()
        
        if format_preference.get(file_format, 0) > format_preference.get(other_format, 0):
            return True
        elif format_preference.get(file_format, 0) < format_preference.get(other_format, 0):
            return False
        
        # Check bitrate
        file_bitrate = file_info.get('metadata', {}).get('bitrate', 0)
        other_bitrate = other_file.get('metadata', {}).get('bitrate', 0)
        
        if file_bitrate > other_bitrate:
            return True
        elif file_bitrate < other_bitrate:
            return False
        
        # Check file size
        return file_info['size'] > other_file['size']
    
    def _needs_manual_review(self, file_info):
        """
        Check if a file needs manual review
        
        Args:
            file_info (dict): File information
            
        Returns:
            bool: True if file needs manual review
        """
        metadata = file_info.get('metadata', {})
        
        # Check if both artist and title are missing or unknown
        artist = metadata.get('artist', '').lower()
        title = metadata.get('title', '').lower()
        
        if not artist or artist == 'unknown artist' or not title or title == 'unknown title':
            return True
        
        return False
    
    def get_processed_files(self):
        """Get list of source files that were processed"""
        return self.processed_files 