"""
Unit tests for PatternClassifier and MasterOrganizer
"""

import os
import sqlite3
import tempfile
import pytest
from src.engine.pattern_classifier import parse_track_details, is_generic_track, clean_watermarks
from src.engine.master_organizer import MasterOrganizer

def test_pattern_classifier_bollywood():
    p = r"D:\Songs\unorganized\BMW-Music\Hindi\001 AAH = YE SHAAM KI TANHAIYAN.mp3"
    f = "001 AAH = YE SHAAM KI TANHAIYAN.mp3"
    res = parse_track_details(p, f)
    assert res["language"] == "Hindi"
    assert res["category"] == "Aah"
    assert res["title"] == "Ye Shaam Ki Tanhaiyan"
    assert res["filename"] == "Ye Shaam Ki Tanhaiyan.mp3"

def test_pattern_classifier_watermarked():
    p = r"D:\Songs\unorganized\BMW-Music\Hindi\04 - Murder 2 (2011) - Phir Mohabbat [www.DJLUV.in].mp3"
    f = "04 - Murder 2 (2011) - Phir Mohabbat [www.DJLUV.in].mp3"
    res = parse_track_details(p, f)
    assert res["language"] == "Hindi"
    assert "Murder 2" in res["category"]
    assert res["title"] == "Phir Mohabbat"

def test_pattern_classifier_english_rock():
    p = r"D:\Songs\unorganized\BMW-Music\English\001 - Nirvana - Smells Like Teen Spirit (1991).mp3"
    f = "001 - Nirvana - Smells Like Teen Spirit (1991).mp3"
    res = parse_track_details(p, f)
    assert res["language"] == "English"
    assert res["category"] == "Nirvana"
    assert "Smells Like Teen Spirit" in res["title"]

def test_pattern_classifier_generic_natyasangeet():
    p = r"D:\Songs\unorganized\BMW-Music\Marathi\Natya Sangeet\01 naman natwara-1\Track1.mp3"
    f = "Track1.mp3"
    res = parse_track_details(p, f)
    assert res["language"] == "Marathi"
    assert res["category"] == "01 naman natwara-1"
    assert res["is_generic"] is True

def test_pattern_classifier_sanskrit():
    p = r"D:\Songs\unorganized\BMW-Music\Morning\Sounds_Of_Isha_Daridraya_Dahana_Stotram.mp3"
    f = "Sounds_Of_Isha_Daridraya_Dahana_Stotram.mp3"
    res = parse_track_details(p, f)
    assert res["language"] == "Sanskrit"
    assert "Stotras" in res["category"]

def test_master_organizer_plan_and_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_inv.db")
        out_root = os.path.join(tmpdir, "organized")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE audio_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            filename TEXT,
            file_size INTEGER,
            duration REAL,
            artist TEXT,
            title TEXT,
            album TEXT,
            detected_language TEXT,
            file_hash TEXT
        )
        """)
        
        f1 = os.path.join(tmpdir, "001 AAH = YE SHAAM KI TANHAIYAN.mp3")
        with open(f1, "wb") as f:
            f.write(b"AUDIO_DATA" * 200) # > 1KB
            
        cur.execute("INSERT INTO audio_inventory VALUES (1, ?, '001 AAH = YE SHAAM KI TANHAIYAN.mp3', 2000, 150.0, '', '', '', 'Hindi', 'hash1')", (f1,))
        conn.commit()
        conn.close()
        
        organizer = MasterOrganizer(db_path=db_path, output_root=out_root, parallel_workers=1)
        plan = organizer.build_organization_plan()
        assert plan["total_evaluated"] == 1
        assert plan["unique_to_organize"] == 1
        
        res = organizer.execute(parallel=False)
        assert res["files_organized_and_copied"] == 1
        expected_file = os.path.join(out_root, "Hindi", "Aah", "Ye Shaam Ki Tanhaiyan.mp3")
        assert os.path.exists(expected_file)
