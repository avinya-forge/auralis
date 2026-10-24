r"""
Auralis Staging Manager & Multi-Algorithm Deduplicator
Creates a clean, shallow, unique working library on high-speed NVMe SSD (D:\)
with 0 duplicates based on filename + size, complete audit tracking,
and 100% reversible rollback capability.
"""

import os
import sys
import sqlite3
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.engine.fast_consolidator import FastConsolidator

class StagingManager:
    """Manages the creation of a non-destructive unique staging library with rollback safety."""

    def __init__(
        self,
        db_path: str = r"D:\Code\avinya-forge\auralis\auralis_inventory.db",
        staging_root: str = r"D:\Songs\staging_unique_unorganized",
        duplicates_root: str = r"D:\Songs\staging_duplicates_backup",
        corrupt_root: str = r"D:\Songs\staging_corrupted_backup"
    ):
        self.db_path = db_path
        self.staging_root = staging_root
        self.duplicates_root = duplicates_root
        self.corrupt_root = corrupt_root
        self.consolidator = FastConsolidator(db_path=self.db_path)

    def init_transaction_db(self) -> None:
        """Initializes the transaction table for 100% reversible rollbacks."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS staging_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT NOT NULL,
            staged_path TEXT,
            filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_trans_status ON staging_transactions(status)")
        conn.commit()
        conn.close()

    def build_staging_plan(self) -> Dict[str, Any]:
        """
        Builds the complete multi-algorithm plan:
          - Alg 0: Isolates 0-byte and corrupted files (<1KB or 0s duration)
          - Alg 1: Isolates exact filename + file size duplicates
          - Unique tracks routed to shallow staging (max depth 2: Staging / [Language] / [filename])
        """
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

        # 3. All files in inventory
        cur.execute("""
        SELECT id, file_path, filename, file_size, duration, detected_language
        FROM audio_inventory
        """)
        all_files = cur.fetchall()
        conn.close()

        plan_items = []
        unique_count = 0
        duplicate_count = 0
        corrupt_count = 0

        for row_id, fpath, fname, fsize, dur, lang in all_files:
            if fpath in corrupt_paths:
                corrupt_count += 1
                cat = "CORRUPT_OR_ZERO_BYTE"
                staged = os.path.join(self.corrupt_root, fname)
            elif fpath in redundant_map:
                duplicate_count += 1
                cat = "TIER0_DUPLICATE"
                staged = os.path.join(self.duplicates_root, fname)
            else:
                unique_count += 1
                cat = "UNIQUE_TRACK"
                lang_dir = lang if lang and lang != "Unknown" else "General"
                from src.engine.fast_consolidator import is_generic_filename
                if is_generic_filename(fname):
                    parent_context = os.path.basename(os.path.dirname(fpath))
                    staged = os.path.join(self.staging_root, lang_dir, parent_context, fname)
                else:
                    staged = os.path.join(self.staging_root, lang_dir, fname)

            plan_items.append({
                "id": row_id,
                "original_path": fpath,
                "staged_path": staged,
                "filename": fname,
                "file_size": fsize,
                "category": cat
            })

        return {
            "total_files": len(all_files),
            "unique_tracks": unique_count,
            "duplicate_copies": duplicate_count,
            "corrupt_files": corrupt_count,
            "plan_items": plan_items
        }

    def execute_staging(self, use_copy: bool = True, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes the non-destructive staging operation.
        Copies files safely while logging every transaction in SQLite.
        """
        self.init_transaction_db()
        plan = self.build_staging_plan()
        items = plan["plan_items"]
        if limit:
            items = items[:limit]

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        copied_count = 0
        skipped_count = 0
        start_time = time.time()

        for item in items:
            orig = item["original_path"]
            dest = item["staged_path"]
            cat = item["category"]

            if not os.path.exists(orig):
                continue

            # Ensure unique destination filename if collision in staging
            dest_dir = os.path.dirname(dest)
            os.makedirs(dest_dir, exist_ok=True)

            target = dest
            counter = 1
            stem, ext = os.path.splitext(dest)
            while os.path.exists(target):
                # If target already exists with identical size, it's already staged
                if os.path.getsize(target) == os.path.getsize(orig):
                    break
                target = f"{stem}_dup{counter}{ext}"
                counter += 1

            if not os.path.exists(target):
                try:
                    shutil.copy2(orig, target)
                    copied_count += 1
                except Exception as e:
                    print(f"[!] Error copying {orig} -> {target}: {e}")
                    continue
            else:
                skipped_count += 1

            cur.execute("""
            INSERT INTO staging_transactions 
            (original_path, staged_path, filename, file_size, category, status)
            VALUES (?, ?, ?, ?, ?, 'STAGED')
            """, (orig, target, item["filename"], item["file_size"], cat))

        conn.commit()
        conn.close()
        elapsed = round(time.time() - start_time, 2)

        # Generate automated rollback script
        self.generate_rollback_script()

        return {
            "total_processed": len(items),
            "files_copied": copied_count,
            "already_present_skipped": skipped_count,
            "elapsed_seconds": elapsed,
            "staging_root": self.staging_root,
            "duplicates_root": self.duplicates_root,
            "rollback_script": r"D:\Code\avinya-forge\auralis\scripts\restore_to_original.py"
        }

    def generate_rollback_script(self) -> str:
        """Generates an automated rollback script to revert all changes if ever needed."""
        script_path = r"D:\Code\avinya-forge\auralis\scripts\restore_to_original.py"
        content = f'''"""
Auralis - 1-Click Rollback Script
Restores the original messy structure and removes the staging area.
Generated automatically for 100% data safety.
"""

import os
import sqlite3
import shutil

DB_PATH = r"{self.db_path}"
STAGING_DIRS = [
    r"{self.staging_root}",
    r"{self.duplicates_root}",
    r"{self.corrupt_root}"
]

def rollback():
    print("[*] Reversing staging operations...")
    for s_dir in STAGING_DIRS:
        if os.path.exists(s_dir):
            print(f"[*] Removing staged directory: {{s_dir}}")
            shutil.rmtree(s_dir, ignore_errors=True)
            
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM staging_transactions")
    conn.commit()
    conn.close()
    print("[*] Rollback complete. Original directories remain completely untouched.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to rollback all staging files? (yes/no): ")
    if confirm.lower() == "yes":
        rollback()
    else:
        print("Rollback cancelled.")
'''
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content)
        return script_path

if __name__ == "__main__":
    manager = StagingManager()
    print("[*] Staging Plan Overview:")
    plan = manager.build_staging_plan()
    print(f"    Total files evaluated: {plan['total_files']}")
    print(f"    Unique tracks to stage on NVMe SSD: {plan['unique_tracks']}")
    print(f"    Exact filename+size duplicates to isolate: {plan['duplicate_copies']}")
    print(f"    Zero-byte / corrupted files to quarantine: {plan['corrupt_files']}")
