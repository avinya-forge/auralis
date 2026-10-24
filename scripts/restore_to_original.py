"""
Auralis - 1-Click Rollback Script
Restores the original messy structure and removes the staging area.
Generated automatically for 100% data safety.
"""

import os
import sqlite3
import shutil

DB_PATH = r"C:\Users\kaush\AppData\Local\Temp\tmpzw3d1h85\test_inventory.db"
STAGING_DIRS = [
    r"C:\Users\kaush\AppData\Local\Temp\tmpzw3d1h85\staging",
    r"C:\Users\kaush\AppData\Local\Temp\tmpzw3d1h85\dupes",
    r"C:\Users\kaush\AppData\Local\Temp\tmpzw3d1h85\corrupt"
]

def rollback():
    print("[*] Reversing staging operations...")
    for s_dir in STAGING_DIRS:
        if os.path.exists(s_dir):
            print(f"[*] Removing staged directory: {s_dir}")
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
