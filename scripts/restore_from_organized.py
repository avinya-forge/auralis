r"""
Auralis - 1-Click Rollback Script for Master Organized Library
Removes D:\Songs\organized and resets transactions.
Original music files remain 100% untouched.
"""

import os
import sqlite3
import shutil

ORGANIZED_ROOT = r"C:\Users\kaush\AppData\Local\Temp\tmp7la1u1qe\organized"
DB_PATH = r"C:\Users\kaush\AppData\Local\Temp\tmp7la1u1qe\test_inv.db"

def rollback():
    print(f"[*] Removing organized library: {ORGANIZED_ROOT}...")
    if os.path.exists(ORGANIZED_ROOT):
        shutil.rmtree(ORGANIZED_ROOT)
        print("[+] Removed organized library.")

    print(f"[*] Resetting database: {DB_PATH}...")
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM transactions")
        c.execute("UPDATE files SET organized_path = NULL")
        conn.commit()
        conn.close()
        print("[+] Database transactions rolled back.")

if __name__ == "__main__":
    rollback()
