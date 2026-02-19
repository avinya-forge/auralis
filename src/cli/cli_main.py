"""
Auralis - CLI Main Module
"""

import argparse
import json
import logging
import os
import sys

from src.utils.dependency_checker import DependencyChecker

# Optional tqdm import
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    tqdm = None

# Optional PyQt6 import to allow 'check' command to run without dependencies
try:
    from PyQt6.QtCore import QCoreApplication, QObject

    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False

    class QObject:  # type: ignore
        """Dummy QObject"""

        pass

    QCoreApplication = None  # type: ignore


class ConsoleHandler(QObject):
    """Handles console output and progress bars"""

    def __init__(self):
        super().__init__()
        self.progress_bar = None

    def on_progress_updated(self, current, total):
        """Handle progress updates"""
        if tqdm is None:
            # Fallback if tqdm is missing
            if current % 10 == 0 or current == total:
                print(f"Progress: {current}/{total}")
            return

        if self.progress_bar is None:
            self.progress_bar = tqdm(total=total, unit="files", leave=True)

        if self.progress_bar.total != total:
            self.progress_bar.total = total
            self.progress_bar.refresh()

        self.progress_bar.n = current
        self.progress_bar.refresh()

        if current >= total and total > 0:
            self.progress_bar.close()
            self.progress_bar = None

    def on_file_scanned(self, file_path):
        """Handle file scanned event"""
        if self.progress_bar:
            filename = os.path.basename(file_path)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            self.progress_bar.set_description(f"Scanning: {filename}")

    def on_file_organized(self, src, dest):
        """Handle file organized event"""
        if self.progress_bar:
            filename = os.path.basename(src)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            self.progress_bar.set_description(f"Organizing: {filename}")

    def on_file_updated(self, path):
        """Handle file updated event (metadata)"""
        if self.progress_bar:
            filename = os.path.basename(path)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            self.progress_bar.set_description(f"Processing: {filename}")

    def close(self):
        """Close progress bar if open"""
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None


def setup_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description="Auralis - Music File Management CLI")

    # Global options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )
    parser.add_argument("--config", help="Path to configuration file")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan directories for music files")
    scan_parser.add_argument("directories", nargs="+", help="Directories to scan")
    scan_parser.add_argument(
        "--extensions", help="Comma-separated list of file extensions (e.g. mp3,flac)"
    )
    scan_parser.add_argument("--exclude", help="Comma-separated list of patterns to exclude")
    scan_parser.add_argument(
        "--depth", type=int, default=10, help="Maximum directory depth to scan"
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
    org_parser.add_argument("--no-rename", action="store_true", help="Disable file renaming")
    org_parser.add_argument("--keep-duplicates", action="store_true", help="Keep duplicate files")
    org_parser.add_argument(
        "--keep-empty-dirs", action="store_true", help="Do not remove empty directories"
    )
    org_parser.add_argument(
        "--template",
        type=str,
        help="Custom directory structure template (e.g. {artist}/{album}/{title})",
    )

    # Metadata command
    meta_parser = subparsers.add_parser("metadata", help="Update metadata")
    meta_parser.add_argument("source", help="Source directory or JSON file")
    meta_parser.add_argument("--no-musicbrainz", action="store_true", help="Disable MusicBrainz")
    meta_parser.add_argument("--no-discogs", action="store_true", help="Disable Discogs")
    meta_parser.add_argument("--no-lyrics", action="store_true", help="Disable lyrics fetching")
    meta_parser.add_argument(
        "--fetch-cover-art",
        action="store_true",
        help="Fetch and embed cover art from online sources",
    )
    meta_parser.add_argument(
        "--force", action="store_true", help="Force update even if metadata exists"
    )

    # Check command
    subparsers.add_parser("check", help="Check system and Python dependencies")

    return parser


def run_cli():
    """Run the CLI application"""
    # Ensure headless mode for Qt
    if not os.environ.get("QT_QPA_PLATFORM"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    parser = setup_parser()
    args = parser.parse_args()

    # If check command, run it without requiring PyQt6 or other dependencies
    if args.command == "check":
        run_check(args)
        return

    # For other commands, ensure PyQt6 is available
    if not HAS_PYQT:
        print("Error: PyQt6 is required for this command but not installed.")
        print("Run 'python auralis.py check' to see missing dependencies.")
        sys.exit(1)

    # Initialize QCoreApplication
    # We need to assign it to a variable to keep it alive, even if not used directly
    _app = QCoreApplication(sys.argv)  # noqa: F841

    # Configure logging
    log_level = getattr(logging, args.log_level)
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

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
    try:
        from src.core.scanner import MusicScanner
    except ImportError as e:
        print(f"Error importing MusicScanner: {e}")
        return

    print(f"Scanning directories: {args.directories}")

    scanner = MusicScanner()
    handler = ConsoleHandler()

    # Connect signals
    scanner.progress_updated.connect(handler.on_progress_updated)
    scanner.file_scanned.connect(handler.on_file_scanned)

    # Configure options
    options = {}
    if args.extensions:
        options["file_extensions"] = args.extensions.split(",")
    if args.exclude:
        options["exclude_patterns"] = args.exclude.split(",")
    if args.depth:
        options["max_scan_depth"] = args.depth

    # Run scan
    try:
        files = scanner.scan_directories(args.directories, options)
        handler.close()
        print(f"Found {len(files)} music files.")

        if args.output_json:
            try:
                with open(args.output_json, "w") as f:
                    json.dump(files, f, indent=2)
                print(f"Results saved to {args.output_json}")
            except Exception as e:
                print(f"Error saving results: {e}")
    except Exception as e:
        handler.close()
        print(f"Error during scan: {e}")


def run_organize(args):
    """Execute organize command"""
    try:
        from src.core.organizer import MusicOrganizer
    except ImportError as e:
        print(f"Error importing MusicOrganizer: {e}")
        return

    print(f"Organizing from {args.source} to {args.destination}")

    # Load files
    files = _load_files(args.source)
    if not files:
        return

    organizer = MusicOrganizer(dry_run=args.dry_run)
    handler = ConsoleHandler()

    # Connect signals
    organizer.progress_updated.connect(handler.on_progress_updated)
    organizer.file_organized.connect(handler.on_file_organized)

    # Configure options
    options = {
        "organize_by_language": not args.no_language,
        "detect_audio_similarity": not args.no_similarity,
        "rename_files": not args.no_rename,
        "handle_duplicates": not args.keep_duplicates,
        "remove_empty_dirs": not args.keep_empty_dirs,
    }

    if args.template:
        options["directory_template"] = args.template

    # Run organize
    try:
        result = organizer.organize_files(files, args.destination, options)
        handler.close()

        print("\nOrganization Summary:")
        print(f"Total files: {result.get('total_files', 0)}")
        print(f"Organized: {result.get('organized_files', 0)}")
        print(f"Duplicates: {result.get('duplicates', 0)}")
        print(f"Errors: {len(result.get('file_errors', {}))}")

        if args.dry_run:
            print("\nNote: This was a dry run. No files were moved.")
    except Exception as e:
        handler.close()
        print(f"Error during organization: {e}")


def run_metadata(args):
    """Execute metadata command"""
    try:
        from src.services.metadata_service import MetadataService
    except ImportError as e:
        print(f"Error importing MetadataService: {e}")
        return

    print(f"Updating metadata for {args.source}")

    # Load files
    files = _load_files(args.source)
    if not files:
        return

    service = MetadataService()
    handler = ConsoleHandler()

    # Connect signals
    service.progress_updated.connect(handler.on_progress_updated)
    service.file_updated.connect(handler.on_file_updated)

    # Configure options
    options = {
        "use_musicbrainz": not args.no_musicbrainz,
        "use_discogs": not args.no_discogs,
        "fetch_lyrics": not args.no_lyrics,
        "fetch_cover_art": args.fetch_cover_art,
        "force_update": args.force,
    }

    # Run update
    try:
        updated_files = service.update_metadata(files, options)
        handler.close()
        print(f"Updated metadata for {len(updated_files)} files.")
    except Exception as e:
        handler.close()
        print(f"Error during metadata update: {e}")


def run_check(args):
    """Execute check command"""
    print("Checking dependencies...")
    checker = DependencyChecker()
    report = checker.check_all()

    print(f"\nSystem: {report['platform']}")
    print(f"Python: {report['python_version'].split()[0]}")

    print("\nCore Dependencies:")
    for mod, installed in report["core"].items():
        status = "✓" if installed else "✗"
        print(f"  {status} {mod}")

    print("\nAudio Similarity Dependencies:")
    for mod, installed in report["audio_similarity"].items():
        status = "✓" if installed else "✗"
        print(f"  {status} {mod}")

    print("\nLanguage Detection Dependencies:")
    for mod, installed in report["language_detection"].items():
        status = "✓" if installed else "✗"
        print(f"  {status} {mod}")

    print("\nSystem Tools:")
    for tool, info in report["system_tools"].items():
        status = "✓" if info["installed"] else "✗"
        path = f"({info['path']})" if info["path"] else ""
        print(f"  {status} {tool} {path}")

    if report.get("libraries"):
        print("\nLibraries:")
        for lib, info in report["libraries"].items():
            status = "✓" if info["installed"] else "✗"
            path = f"({info['path']})" if info["path"] else ""
            print(f"  {status} {lib} {path}")

    # Check audio capabilities
    print("\nChecking Audio Capabilities...")
    audio_report = checker.check_audio_capabilities()
    if audio_report["success"]:
        print(f"  ✓ {audio_report['message']}")
    else:
        print(f"  ✗ {audio_report['message']}")

    # Identify missing
    missing_modules = []
    missing_tools = []

    for section in ["core", "audio_similarity", "language_detection"]:
        for mod, installed in report[section].items():
            if not installed:
                missing_modules.append(mod)

    for tool, info in report["system_tools"].items():
        if not info["installed"]:
            missing_tools.append(tool)

    if missing_modules or missing_tools:
        print("\n" + "=" * 40)
        print("Missing Dependencies Instructions")
        print("=" * 40)
        print(checker.get_install_instructions(missing_modules, missing_tools))


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
        # Import MusicScanner locally to avoid top-level dependency
        try:
            from src.core.scanner import MusicScanner
        except ImportError:
            print("Error: MusicScanner not available (PyQt6 missing?)")
            return []

        scanner = MusicScanner()
        # We should probably use ConsoleHandler here too if we want progress
        handler = ConsoleHandler()
        scanner.progress_updated.connect(handler.on_progress_updated)
        scanner.file_scanned.connect(handler.on_file_scanned)

        files = scanner.scan_directories([source])
        handler.close()
        return files
    else:
        print(f"Invalid source: {source}")
        return []


if __name__ == "__main__":
    run_cli()
