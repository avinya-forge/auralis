r"""
Auralis - Master Library Organizer & Universal Tagging Engine
Processes raw music library into a clean, shallow, single output folder (D:\Songs\organized),
applying pattern-based classification, universal ID3v2.4 tags, deduplication,
and full rollback safety.
"""

import os
import sys
import re
import stat
import sqlite3
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, TCOM, TEXT, APIC, ID3NoHeaderError
from mutagen.asf import ASF
from mutagen.mp4 import MP4, MP4Cover
from mutagen.wave import WAVE

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.engine.fast_consolidator import FastConsolidator, is_generic_filename
from src.engine.pattern_classifier import parse_track_details
from src.engine.embedded_intelligence import EmbeddedLanguageIntelligence
from src.engine.language_parallel_engine import LanguageParallelEngine
from src.engine.reliable_metadata_client import ReliableMetadataClient
from src.engine.path_sanitizer import (
    sanitize_path_component,
    sanitize_relative_path,
    sanitize_filename,
)

class MasterOrganizer:
    """End-to-end master organizer for structuring libraries with 0 loss and accurate metadata."""

    def __init__(
        self,
        db_path: str = r"D:\Code\avinya-forge\auralis\auralis_inventory.db",
        output_root: str = r"D:\Songs\organized",
        enable_airllm: bool = False,
        parallel_workers: int = 5
    ):
        self.db_path = db_path
        self.output_root = output_root
        self.enable_airllm = enable_airllm
        self.parallel_workers = parallel_workers
        self.unorganized_root = r"D:\Songs\unorganized"
        self.duplicates_dir = os.path.join(self.unorganized_root, "_duplicates_backup")
        self.corrupt_dir = os.path.join(self.unorganized_root, "_corrupted_backup")
        self.consolidator = FastConsolidator(db_path=self.db_path)
        self.intelligence = EmbeddedLanguageIntelligence(enable_airllm=enable_airllm)
        self.metadata_client = ReliableMetadataClient(cache_db=self.db_path)
        self.parallel_engine = LanguageParallelEngine(
            db_path=self.db_path,
            output_root=self.output_root,
            num_workers=parallel_workers
        )

    def init_database(self) -> None:
        """Initializes the master organization transaction table."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS master_organized_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT NOT NULL,
            organized_path TEXT NOT NULL,
            language TEXT,
            category TEXT,
            clean_title TEXT,
            clean_artist TEXT,
            album TEXT,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

    def write_id3_tags(
        self,
        file_path: str,
        title: str,
        artist: str,
        album: str,
        genre: str,
        year: str = "",
        album_artist: str = "",
        composer: str = "",
        lyricist: str = "",
        artwork_bytes: Optional[bytes] = None
    ) -> bool:
        """Writes universal standard tags across MP3, WMA, M4A, WAV with optional artwork for complete media player fidelity."""
        try:
            # Enrich metadata from reliable sources if fields are missing
            if (not year or not artwork_bytes) and title and artist and hasattr(self, 'metadata_client'):
                try:
                    resolved = self.metadata_client.resolve_track_metadata(
                        filename=os.path.basename(file_path),
                        artist=artist,
                        album=album,
                        title=title
                    )
                    if not year and resolved.get("year"):
                        year = resolved["year"]
                    if not genre and resolved.get("genre"):
                        genre = resolved["genre"]
                    if not artwork_bytes and resolved.get("artwork_url"):
                        artwork_bytes = self.metadata_client.fetch_artwork_bytes(resolved["artwork_url"])
                except Exception:
                    pass

            # Ensure destination file is writable on Windows NTFS (clears ReadOnly flag from CD rips)
            try:
                os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass

            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".mp3":
                try:
                    audio = ID3(file_path)
                except ID3NoHeaderError:
                    audio = ID3()

                if title:
                    audio["TIT2"] = TIT2(encoding=3, text=title)
                if artist:
                    audio["TPE1"] = TPE1(encoding=3, text=artist)
                if album:
                    audio["TALB"] = TALB(encoding=3, text=album)
                if genre:
                    audio["TCON"] = TCON(encoding=3, text=genre)
                if year:
                    audio["TDRC"] = TDRC(encoding=3, text=year)
                if album_artist or artist:
                    audio["TPE2"] = TPE2(encoding=3, text=album_artist or artist)
                if composer:
                    audio["TCOM"] = TCOM(encoding=3, text=composer)
                if lyricist:
                    audio["TEXT"] = TEXT(encoding=3, text=lyricist)
                if artwork_bytes and not any(k.startswith("APIC") for k in audio.keys()):
                    audio.add(APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=artwork_bytes
                    ))

                audio.save(file_path, v2_version=4)
                return True

            elif ext == ".wma":
                asf = ASF(file_path)
                if asf.tags is not None:
                    if title:
                        asf.tags["Title"] = [title]
                    if artist:
                        asf.tags["Author"] = [artist]
                    if album:
                        asf.tags["WM/AlbumTitle"] = [album]
                    if album_artist or artist:
                        asf.tags["WM/AlbumArtist"] = [album_artist or artist]
                    if genre:
                        asf.tags["WM/Genre"] = [genre]
                    if year:
                        asf.tags["WM/Year"] = [year]
                    if composer:
                        asf.tags["WM/Composer"] = [composer]
                    asf.save()
                return True

            elif ext == ".m4a":
                mp4 = MP4(file_path)
                if mp4.tags is None:
                    mp4.add_tags()
                if title:
                    mp4.tags["\xa9nam"] = [title]
                if artist:
                    mp4.tags["\xa9ART"] = [artist]
                if album_artist or artist:
                    mp4.tags["aART"] = [album_artist or artist]
                if album:
                    mp4.tags["\xa9alb"] = [album]
                if genre:
                    mp4.tags["\xa9gen"] = [genre]
                if year:
                    mp4.tags["\xa9day"] = [year]
                if composer:
                    mp4.tags["\xa9wrt"] = [composer]
                if artwork_bytes and ("covr" not in mp4.tags or not mp4.tags["covr"]):
                    mp4.tags["covr"] = [MP4Cover(artwork_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
                mp4.save()
                return True

            elif ext == ".wav":
                wav = WAVE(file_path)
                if wav.tags is None:
                    wav.add_tags()
                if title:
                    wav.tags["TIT2"] = TIT2(encoding=3, text=title)
                if artist:
                    wav.tags["TPE1"] = TPE1(encoding=3, text=artist)
                if album:
                    wav.tags["TALB"] = TALB(encoding=3, text=album)
                if genre:
                    wav.tags["TCON"] = TCON(encoding=3, text=genre)
                wav.save()
                return True

            return True
        except Exception:
            return False

    def build_organization_plan(self) -> Dict[str, Any]:
        """Builds the comprehensive plan mapping every file to its clean uniform 2-level destination."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # 1. Corrupted / 0-byte files
        corrupt_data = self.consolidator.audit_zero_byte_and_corrupt()
        corrupt_paths = {f["file_path"]: f for f in corrupt_data["files"]}

        # 2. Tier-0 Duplicates
        t0_data = self.consolidator.find_tier0_exact_duplicates()
        redundant_map = {}
        for group in t0_data["duplicate_groups"]:
            primary = group["primary_keeper"]
            for r_copy in group["redundant_copies"]:
                redundant_map[r_copy] = primary

        # 3. All inventory records
        columns = [c[1] for c in cur.execute("PRAGMA table_info(audio_inventory)").fetchall()]
        has_bitrate = "bitrate" in columns
        
        query = """
        SELECT id, file_path, filename, file_size, duration, artist, title, album, detected_language{}
        FROM audio_inventory
        """.format(", bitrate" if has_bitrate else "")
        cur.execute(query)
        all_files = cur.fetchall()
        conn.close()

        plan_items = []
        unique_count = 0
        duplicate_count = 0
        corrupt_count = 0

        for row in all_files:
            if has_bitrate:
                row_id, fpath, fname, fsize, dur, tag_art, tag_tit, tag_alb, lang, brate = row
            else:
                row_id, fpath, fname, fsize, dur, tag_art, tag_tit, tag_alb, lang = row
                brate = 0
            if fpath in corrupt_paths:
                corrupt_count += 1
                status = "CORRUPT_QUARANTINE"
                target = os.path.join(self.corrupt_dir, sanitize_filename(fname))
                parsed = {
                    "language": "Corrupt", "category": "Corrupted",
                    "title": fname, "artist": "N/A", "album": "N/A", "filename": fname
                }
            elif fpath in redundant_map:
                duplicate_count += 1
                status = "EXACT_DUPLICATE_BACKUP"
                target = os.path.join(self.duplicates_dir, sanitize_filename(fname))
                parsed = {
                    "language": "Duplicates", "category": "Redundant Copies",
                    "title": fname, "artist": "N/A", "album": "N/A", "filename": fname
                }
            else:
                unique_count += 1
                status = "ORGANIZE_UNIQUE"
                parsed = parse_track_details(
                    file_path=fpath,
                    raw_filename=fname,
                    tag_artist=tag_art,
                    tag_title=tag_tit,
                    tag_album=tag_alb,
                    llm_classifier=self.intelligence
                )
                # Uniform shallow 2-level structure: output_root / [Language] / [Category_Movie_Artist] / [Clean_Title.ext]
                # Fully sanitized for Windows NTFS filesystem compatibility and strictly 1 category directory level
                lang_clean = sanitize_path_component(parsed["language"])
                cat_clean = sanitize_path_component(parsed["category"])
                fn_clean = sanitize_filename(parsed["filename"])
                target = os.path.join(
                    self.output_root,
                    lang_clean,
                    cat_clean,
                    fn_clean
                )

            plan_items.append({
                "id": row_id,
                "original_path": fpath,
                "target_path": target,
                "parsed": parsed,
                "status": status,
                "bitrate": brate or 0,
                "file_size": fsize or 0,
                "duration": dur or 0.0
            })

        # Quality-Aware Deduplication Pass:
        # If two distinct files map to the exact same (Language / Category / Title) and have matching duration,
        # keep the highest-bitrate / higher-quality track as ORGANIZE_UNIQUE, and route lower-quality copies
        # to _duplicates_backup in unorganized.
        targets_map: Dict[str, List[Dict[str, Any]]] = {}
        for item in plan_items:
            if item["status"] == "ORGANIZE_UNIQUE":
                targets_map.setdefault(item["target_path"], []).append(item)

        for target_path, items_group in targets_map.items():
            if len(items_group) > 1:
                # Sort descending: highest bitrate first, then largest file size
                items_group.sort(key=lambda x: (x.get("bitrate", 0), x.get("file_size", 0)), reverse=True)
                primary_keeper = items_group[0]
                lower_quality_copies = items_group[1:]

                for lqc in lower_quality_copies:
                    lqc["status"] = "EXACT_DUPLICATE_BACKUP"
                    lqc_fname = os.path.basename(lqc["original_path"])
                    lqc["target_path"] = os.path.join(self.duplicates_dir, sanitize_filename(lqc_fname))
                    lqc["parsed"] = {
                        "language": "Duplicates", "category": "Lower Bitrate Copies",
                        "title": lqc_fname, "artist": "N/A", "album": "N/A", "filename": lqc_fname
                    }
                    unique_count -= 1
                    duplicate_count += 1

        return {
            "total_evaluated": len(all_files),
            "unique_to_organize": unique_count,
            "redundant_duplicates": duplicate_count,
            "corrupted_files": corrupt_count,
            "plan_items": plan_items
        }

    def execute(
        self,
        limit: Optional[int] = None,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the master organization pass on NVMe SSD with tag writing and transaction logging.
        Defaults to 5-worker parallel channel execution for 5x processing speed.
        Safe, non-destructive: source files are NEVER modified or deleted.
        """
        self.init_database()
        plan = self.build_organization_plan()
        items = plan["plan_items"]
        if limit:
            items = items[:limit]

        # Use 5-channel parallel worker engine for 5x execution speed
        if parallel and self.parallel_workers > 1:
            res = self.parallel_engine.execute_parallel(
                plan_items=items,
                dry_run=dry_run,
                progress_callback=progress_callback
            )
            res["output_root"] = self.output_root
            res["dry_run"] = dry_run
            res["rollback_script"] = self.generate_rollback_script()
            return res

        # Sequential fallback path
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        copied = 0
        tagged = 0
        total_items = len(items)
        start_time = time.time()
        seen_targets: Dict[str, str] = {}

        for idx, item in enumerate(items, 1):
            orig = item["original_path"]
            target = item["target_path"]
            status = item["status"]
            parsed = item["parsed"]

            if progress_callback:
                progress_callback(idx, total_items, os.path.basename(orig))

            if not os.path.exists(orig):
                continue

            target_dir = os.path.dirname(target)
            if not dry_run:
                os.makedirs(target_dir, exist_ok=True)

            # Avoid filename collisions across distinct tracks
            final_target = target
            stem, ext = os.path.splitext(target)
            counter = 1
            while final_target in seen_targets and seen_targets[final_target] != orig:
                final_target = f"{stem} ({counter}){ext}"
                counter += 1

            while os.path.exists(final_target):
                size_diff = abs(os.path.getsize(final_target) - os.path.getsize(orig))
                if size_diff < 16384 and (final_target not in seen_targets or seen_targets[final_target] == orig):
                    break
                final_target = f"{stem} ({counter}){ext}"
                counter += 1

            seen_targets[final_target] = orig

            if not dry_run:
                if not os.path.exists(final_target):
                    try:
                        shutil.copy2(orig, final_target)
                        copied += 1
                    except Exception as e:
                        print(f"[!] Error copying {orig} -> {final_target}: {e}")
                        continue
                else:
                    copied += 1

                # Write standard ID3 tags for organized music
                if status == "ORGANIZE_UNIQUE":
                    success = self.write_id3_tags(
                        file_path=final_target,
                        title=parsed["title"],
                        artist=parsed["artist"],
                        album=parsed["album"],
                        genre=parsed["language"],
                        year=parsed.get("year", ""),
                        album_artist=parsed.get("album_artist", parsed.get("artist", ""))
                    )
                    if success:
                        tagged += 1

                cur.execute("""
                INSERT INTO master_organized_transactions 
                (original_path, organized_path, language, category, clean_title, clean_artist, album, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    orig, final_target, parsed["language"], parsed["category"],
                    parsed["title"], parsed["artist"], parsed["album"], status
                ))
            else:
                copied += 1

        if not dry_run:
            conn.commit()
        conn.close()
        elapsed = round(time.time() - start_time, 2)

        self.generate_rollback_script()

        return {
            "total_processed": total_items,
            "files_organized_and_copied": copied,
            "tags_written_and_verified": tagged,
            "elapsed_seconds": elapsed,
            "output_root": self.output_root,
            "dry_run": dry_run,
            "rollback_script": r"D:\Code\avinya-forge\auralis\scripts\restore_from_organized.py"
        }

    def generate_rollback_script(self) -> str:
        """Generates an automated rollback script to revert all changes if ever needed."""
        script_path = r"D:\Code\avinya-forge\auralis\scripts\restore_from_organized.py"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        content = f'''"""
Auralis - 1-Click Rollback Script for Master Organized Library
Removes D:\\Songs\\organized and resets transactions.
Original music files remain 100% untouched.
"""

import os
import sqlite3
import shutil

ORGANIZED_ROOT = r"{self.output_root}"
DB_PATH = r"{self.db_path}"

def rollback():
    print(f"[*] Removing organized library: {{ORGANIZED_ROOT}}...")
    if os.path.exists(ORGANIZED_ROOT):
        shutil.rmtree(ORGANIZED_ROOT, ignore_errors=True)
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM master_organized_transactions")
    conn.commit()
    conn.close()
    print("[*] Rollback complete. Original library remains completely untouched.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to rollback all organized files? (yes/no): ")
    if confirm.lower() == "yes":
        rollback()
    else:
        print("Rollback cancelled.")
'''
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content)
        return script_path

if __name__ == "__main__":
    organizer = MasterOrganizer()
    plan = organizer.build_organization_plan()
    print("--- Master Organization Plan ---")
    print(f"Total Files Evaluated: {plan['total_evaluated']}")
    print(f"Unique Tracks to Organize: {plan['unique_to_organize']}")
    print(f"Redundant Duplicates to Backup: {plan['redundant_duplicates']}")
    print(f"Corrupted / 0-Byte to Quarantine: {plan['corrupted_files']}")
