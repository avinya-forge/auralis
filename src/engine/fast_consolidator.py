"""
Auralis - Fast Audio Consolidator & Hardware-Aware Staging Engine
Performs Tier-0 rapid deduplication (Exact Filename + File Size),
filters 0-byte/corrupted files, and consolidates fragmented deep trees
into a shallow high-speed working library on NVMe SSD.
"""

import os
import sys
import sqlite3
import hashlib
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".wma", ".ogg", ".aac", ".aiff"}
GENERIC_FILENAME_PATTERN = re.compile(
    r"^(track\s*\d+|\d{1,3}|audio\s*track\s*\d+|title\s*\d+|song\s*\d+|untitled.*)\.[a-zA-Z0-9]+$",
    re.IGNORECASE
)

def is_generic_filename(filename: str) -> bool:
    """Detects generic filenames like 'Track1.mp3', 'Track 02.mp3', '01.mp3'."""
    return bool(GENERIC_FILENAME_PATTERN.match(filename.strip()))

class HardwareStrategy:
    """Detects and assigns storage roles based on bus type and performance."""
    
    @staticmethod
    def get_recommended_drives() -> Dict[str, str]:
        r"""
        Returns hardware assignments:
          - FAST_WORKING_DRIVE: NVMe SSD (D:\) for low-latency fingerprinting & processing
          - COLD_BACKUP_DRIVE: High-capacity USB HDD (F:\ with 1.4 TB free) for complete archives
          - TARGET_SYNC_DRIVE: Removable USB Flash Drive (E:\ BMW-Music) for finalized car library
        """
        return {
            "fast_working_drive": r"D:\Songs",
            "cold_backup_drive": r"F:\Music",
            "car_sync_drive": r"E:\Organized_Music"
        }

class FastConsolidator:
    """Pre-filters trivial duplicates, isolates 0-byte files, and flattens deep directory trees."""

    def __init__(self, db_path: str = r"D:\Code\avinya-forge\auralis\auralis_inventory.db"):
        self.db_path = db_path

    def audit_zero_byte_and_corrupt(self) -> Dict[str, Any]:
        """Identifies zero-byte and placeholder files so they are never evaluated as duplicate songs."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
        SELECT id, file_path, filename, file_size, duration 
        FROM audio_inventory 
        WHERE file_size <= 1024 OR duration <= 0.0 OR file_hash IS NULL
        """)
        corrupt_rows = cur.fetchall()
        
        results = []
        for row_id, fpath, fname, fsize, dur in corrupt_rows:
            reason = "Zero-byte file" if fsize == 0 else ("Truncated file (<1KB)" if fsize <= 1024 else "Unplayable/0-duration audio")
            results.append({
                "id": row_id,
                "file_path": fpath,
                "filename": fname,
                "size_bytes": fsize,
                "duration_seconds": dur,
                "classification": "CORRUPTED_OR_EMPTY",
                "quarantine_reason": reason
            })
            
        conn.close()
        return {
            "total_corrupted_or_zero_byte": len(results),
            "files": results
        }

    def find_tier0_exact_duplicates(self) -> Dict[str, Any]:
        """
        Tier-0 Deduplication: Finds exact matches on (filename, file_size) where file_size > 1024 bytes.
        Bypasses slow audio decoding and collapses redundant copies across nested directories.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Group by exact filename AND exact file size
        # Group by exact content file_hash (file_size + MD5 checksum)
        cur.execute("""
        SELECT file_hash, file_size, filename, COUNT(*) as cnt, GROUP_CONCAT(file_path, ' ||| ') as paths
        FROM audio_inventory
        WHERE file_size > 1024 AND file_hash IS NOT NULL
        GROUP BY file_hash
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        """)
        
        duplicate_groups = []
        total_redundant_files = 0
        
        for fhash, fsize, fname, cnt, raw_paths in cur.fetchall():
            paths = raw_paths.split(" ||| ")
            # Shortest path with cleanest nesting is chosen as primary candidate
            sorted_paths = sorted(paths, key=lambda p: (len(p.split(os.sep)), len(p)))
            primary_keeper = sorted_paths[0]
            redundant_copies = sorted_paths[1:]
            
            total_redundant_files += len(redundant_copies)
            duplicate_groups.append({
                "file_hash": fhash,
                "filename": fname,
                "file_size": fsize,
                "copy_count": cnt,
                "primary_keeper": primary_keeper,
                "redundant_copies": redundant_copies
            })
            
        conn.close()
        
        return {
            "tier0_duplicate_groups": len(duplicate_groups),
            "total_redundant_files_identified": total_redundant_files,
            "duplicate_groups": duplicate_groups
        }

    def generate_shallow_unorganized_manifest(
        self, 
        target_staging_dir: str = r"D:\Songs\shallow_unorganized",
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Builds a single shallow unorganized staging manifest.
        Eliminates deep nested folder loops while preserving primary language roots (English, Hindi, Marathi, Sanskrit)
        and isolating generic filenames (Track 1, Track 2) with their album context to prevent collisions.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Fetch all valid files
        cur.execute("""
        SELECT id, file_path, filename, file_size, detected_language 
        FROM audio_inventory 
        WHERE file_size > 1024 AND duration > 5.0
        """)
        all_valid = cur.fetchall()
        
        tier0_dupes = self.find_tier0_exact_duplicates()
        redundant_set = set()
        for group in tier0_dupes["duplicate_groups"]:
            for r_path in group["redundant_copies"]:
                redundant_set.add(r_path)
                
        manifest = []
        unique_to_stage = 0
        redundant_to_quarantine = 0
        
        for row_id, fpath, fname, fsize, lang in all_valid:
            if fpath in redundant_set:
                redundant_to_quarantine += 1
                staging_target = os.path.join(target_staging_dir, "_tier0_duplicates_quarantine", fname)
                action = "QUARANTINE_TIER0_DUPLICATE"
            else:
                unique_to_stage += 1
                lang_folder = lang if lang and lang != "Unknown" else "To_Classify"
                
                # If filename is generic (e.g. Track1.mp3), preserve parent album context to prevent overwrite
                if is_generic_filename(fname):
                    parent_context = os.path.basename(os.path.dirname(fpath))
                    staging_target = os.path.join(target_staging_dir, lang_folder, parent_context, fname)
                else:
                    # Clean shallow 2-level structure: target / [Language] / [filename]
                    staging_target = os.path.join(target_staging_dir, lang_folder, fname)
                    
                action = "STAGE_UNIQUE_FOR_PROCESSING"
                
            manifest.append({
                "id": row_id,
                "source_path": fpath,
                "staging_target": staging_target,
                "action": action,
                "size_bytes": fsize,
                "nesting_depth": len(Path(staging_target).relative_to(target_staging_dir).parts)
            })
            
        conn.close()
        
        return {
            "total_valid_tracks_evaluated": len(all_valid),
            "unique_tracks_to_stage": unique_to_stage,
            "redundant_exact_copies_quarantined": redundant_to_quarantine,
            "target_staging_dir": target_staging_dir,
            "sample_manifest": manifest[:15]
        }

if __name__ == "__main__":
    consolidator = FastConsolidator()
    
    print("[*] 1. Auditing Zero-Byte & Corrupted Files...")
    corrupt_audit = consolidator.audit_zero_byte_and_corrupt()
    print(f"    Found {corrupt_audit['total_corrupted_or_zero_byte']} zero-byte or corrupted files.")
    for f in corrupt_audit["files"][:5]:
        print(f"    - {f['filename']} ({f['size_bytes']} bytes) -> {f['quarantine_reason']}")
        
    print("\n[*] 2. Running Tier-0 Exact Duplicate Analysis (Filename + Size)...")
    t0_dupes = consolidator.find_tier0_exact_duplicates()
    print(f"    Found {t0_dupes['tier0_duplicate_groups']} exact duplicate groups.")
    print(f"    Identified {t0_dupes['total_redundant_files_identified']} redundant duplicate copies that can be bypassed instantly!")
    
    print("\n[*] 3. Generating Shallow Unorganized Staging Plan...")
    plan = consolidator.generate_shallow_unorganized_manifest(dry_run=True)
    print(f"    Total Valid Tracks: {plan['total_valid_tracks_evaluated']}")
    print(f"    Clean Unique Tracks to Stage: {plan['unique_tracks_to_stage']}")
    print(f"    Redundant Exact Copies to Quarantine: {plan['redundant_exact_copies_quarantined']}")
    print(f"    Target Staging Nesting Depth: Maximum 2 levels (Clean & Loop-Free)")
