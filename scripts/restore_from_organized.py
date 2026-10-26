"""
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
