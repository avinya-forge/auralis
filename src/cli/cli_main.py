"""
Auralis - CLI Main Module
"""

import argparse
import json
import logging
import os

from src.core.organizer import MusicOrganizer
from src.core.scanner import MusicScanner
from src.services.metadata_service import MetadataService


def setup_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description="Auralis - Music File Management CLI")

    # Global options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Path to configuration file")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan directories for music files")
    scan_parser.add_argument("directories", nargs="+", help="Directories to scan")
    scan_parser.add_argument(
        "--extensions", help="Comma-separated list of file extensions (e.g. mp3,flac)"
    )
    scan_parser.add_argument("--output-json", help="Save scan results to JSON file")

    # Organize command
    org_parser = subparsers.add_parser("organize", help="Organize music files")
    org_parser.add_argument("source", help="Source directory or JSON file from scan")
    org_parser.add_argument("destination", help="Destination directory")
    org_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate organization without moving files"
    )
    org_parser.add_argument(
        "--no-language", action="store_true", help="Disable organization by language"
    )
    org_parser.add_argument(
        "--no-similarity", action="store_true", help="Disable audio similarity detection"
    )

    # Metadata command
    meta_parser = subparsers.add_parser("metadata", help="Update metadata")
    meta_parser.add_argument("source", help="Source directory or JSON file")
    meta_parser.add_argument(
        "--musicbrainz", action="store_true", default=True, help="Use MusicBrainz (default)"
    )
    meta_parser.add_argument(
        "--discogs", action="store_true", default=True, help="Use Discogs (default)"
    )
    meta_parser.add_argument("--lyrics", action="store_true", help="Fetch lyrics")

    return parser


def run_cli():
    """Run the CLI application"""
    parser = setup_parser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.command:
        parser.print_help()
        return

    if args.command == "scan":
        run_scan(args)
    elif args.command == "organize":
        run_organize(args)
    elif args.command == "metadata":
        run_metadata(args)


def run_scan(args):
    """Execute scan command"""
    print(f"Scanning directories: {args.directories}")

    scanner = MusicScanner()

    # Configure options
    options = {}
    if args.extensions:
        options["file_extensions"] = args.extensions.split(",")

    # Run scan
    files = scanner.scan_directories(args.directories, options)
    print(f"Found {len(files)} music files.")

    if args.output_json:
        try:
            with open(args.output_json, "w") as f:
                json.dump(files, f, indent=2)
            print(f"Results saved to {args.output_json}")
        except Exception as e:
            print(f"Error saving results: {e}")


def run_organize(args):
    """Execute organize command"""
    print(f"Organizing from {args.source} to {args.destination}")

    # Load files
    files = _load_files(args.source)
    if not files:
        return

    organizer = MusicOrganizer(dry_run=args.dry_run)

    # Configure options
    options = {
        "organize_by_language": not args.no_language,
        "detect_audio_similarity": not args.no_similarity,
        "rename_files": True,  # Default
        "handle_duplicates": True,
        "remove_empty_dirs": True,
    }

    # Run organize
    result = organizer.organize_files(files, args.destination, options)

    print("\nOrganization Summary:")
    print(f"Total files: {result.get('total_files', 0)}")
    print(f"Organized: {result.get('organized_files', 0)}")
    print(f"Duplicates: {result.get('duplicates', 0)}")
    print(f"Errors: {len(result.get('file_errors', {}))}")

    if args.dry_run:
        print("\nNote: This was a dry run. No files were moved.")


def run_metadata(args):
    """Execute metadata command"""
    print(f"Updating metadata for {args.source}")

    # Load files
    files = _load_files(args.source)
    if not files:
        return

    service = MetadataService()

    # Configure options
    options = {
        "use_musicbrainz": args.musicbrainz,
        "use_discogs": args.discogs,
        "fetch_lyrics": args.lyrics,
    }

    # Run update
    updated_files = service.update_metadata(files, options)
    print(f"Updated metadata for {len(updated_files)} files.")


def _load_files(source):
    """Load files from directory scan or JSON file"""
    if source.endswith(".json"):
        try:
            with open(source, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return []
    elif os.path.isdir(source):
        print("Scanning source directory...")
        scanner = MusicScanner()
        return scanner.scan_directories([source])
    else:
        print(f"Invalid source: {source}")
        return []


if __name__ == "__main__":
    run_cli()
