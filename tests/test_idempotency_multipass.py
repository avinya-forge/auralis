"""
Test Idempotent Multi-Pass Behavior and Self-Reorganizing Stability
"""

import os
import sqlite3
import tempfile
from src.engine.master_organizer import MasterOrganizer
from scripts.discovery_inventory import run_inventory_scan

def test_idempotent_multipass_organization():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "my_music")
        out_dir = os.path.join(tmpdir, "organized")
        db_path = os.path.join(tmpdir, "inv.db")
        os.makedirs(os.path.join(src_dir, "Coldplay"), exist_ok=True)
        
        t1 = os.path.join(src_dir, "Coldplay", "01 - Coldplay - Fix You.mp3")
        with open(t1, "wb") as f:
            f.write(b"\xff\xfb\x90\x00" + b"\x00" * 5000)
            
        run_inventory_scan([src_dir], db_path)
        conn = sqlite3.connect(db_path)
        conn.cursor().execute(
            "UPDATE audio_inventory SET duration=240.0, file_size=5004, artist=?, album=?, title=?",
            ("Coldplay", "XY", "Fix You")
        )
        conn.commit()
        conn.close()
        
        org1 = MasterOrganizer(db_path=db_path, output_root=out_dir, parallel_workers=1)
        res1 = org1.execute(parallel=False)
        assert res1["files_organized_and_copied"] == 1
        
        pass1_file = os.path.join(out_dir, "English", "Coldplay", "Fix You.mp3")
        assert os.path.exists(pass1_file)
        
        # Pass 2: Re-scan and re-organize the ALREADY organized folder
        db_pass2 = os.path.join(tmpdir, "pass2.db")
        out_dir_pass2 = os.path.join(tmpdir, "organized_pass2")
        run_inventory_scan([out_dir], db_pass2)
        
        conn2 = sqlite3.connect(db_pass2)
        conn2.cursor().execute("UPDATE audio_inventory SET duration=240.0, file_size=5004")
        conn2.commit()
        conn2.close()
        
        org2 = MasterOrganizer(db_path=db_pass2, output_root=out_dir_pass2, parallel_workers=1)
        res2 = org2.execute(parallel=False)
        assert res2["files_organized_and_copied"] == 1
        
        pass2_file = os.path.join(out_dir_pass2, "English", "Coldplay", "Fix You.mp3")
        assert os.path.exists(pass2_file)
        print("Idempotent multi-pass organization verified.")

if __name__ == "__main__":
    test_idempotent_multipass_organization()
