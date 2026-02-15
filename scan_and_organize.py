import sys
import os
import argparse
from typing import List, Dict

from PyQt6.QtCore import QCoreApplication, QObject, pyqtSlot

# Adjust python path to include src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.metadata_service import MetadataService
from src.services.organization_service import OrganizationService

class ConsoleOrganizer(QObject):
    def __init__(self):
        super().__init__()
        self.metadata_service = MetadataService()
        self.organization_service = OrganizationService()
        
        # Connect signals
        # Note: Signals might not be delivered if main thread is blocked by update_metadata
        # and we don't run an event loop. But we still get the final result.
        try:
            self.metadata_service.progress_updated.connect(self.on_progress)
            self.metadata_service.metadata_updated.connect(self.on_metadata_updated)
            self.metadata_service.file_updated.connect(self.on_file_updated)
        except Exception as e:
            print(f"Warning: Could not connect signals: {e}")
        
    @pyqtSlot(int, int)
    def on_progress(self, current, total):
        print(f"Progress: {current}/{total} files processed.")

    @pyqtSlot(str, dict)
    def on_metadata_updated(self, path, metadata):
        print(f"Metadata updated for: {path}")
        print(f"  Artist: {metadata.get('artist', 'Unknown')}")
        print(f"  Title: {metadata.get('title', 'Unknown')}")

    @pyqtSlot(str)
    def on_file_updated(self, message):
        print(f"Status: {message}")

    def run(self, source_dir, target_dir, move=False):
        print(f"Scanning directory: {source_dir}")
        if not os.path.exists(source_dir):
            print(f"Error: Source directory {source_dir} not found.")
            return

        files = self.organization_service.scan_directory(source_dir)
        print(f"Found {len(files)} music files.")
        
        if not files:
            print("No music files found.")
            return

        # Convert to format expected by MetadataService
        # List of dicts with 'path' and 'metadata' keys
        music_files = []
        for f in files:
            # We can try to read existing metadata first using mutagen if we want
            # But MetadataService might do it?
            # MetadataService.update_metadata expects 'metadata' dict in file_info
            music_files.append({'path': f, 'metadata': {}})
        
        print("Fetching metadata from online sources...")
        # options: use_musicbrainz=True, use_discogs=True, force_update=True
        options = {
            'use_musicbrainz': True,
            'use_discogs': True,
            'force_update': False, # Only update if missing
            'fetch_lyrics': False
        }
        
        # This is synchronous in the service (it waits for threads)
        updated_files = self.metadata_service.update_metadata(music_files, options)
        
        print("Organizing files...")
        success_count = 0
        for file_info in updated_files:
            original_path = file_info['path']
            metadata = file_info.get('metadata', {})
            
            new_path = self.organization_service.organize_file(
                original_path, 
                metadata, 
                target_dir, 
                move=move
            )
            
            if new_path:
                print(f"Organized: {os.path.basename(original_path)} -> {new_path}")
                success_count += 1
            else:
                print(f"Failed to organize: {original_path}")

        print(f"Done! Organized {success_count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auralis Music Organizer")
    parser.add_argument("source", help="Source directory containing music files")
    parser.add_argument("target", help="Target directory for organized library")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    
    args = parser.parse_args()
    
    app = QCoreApplication(sys.argv)
    organizer = ConsoleOrganizer()
    organizer.run(args.source, args.target, args.move)
    # We exit directly, no app.exec() needed as run() is synchronous
