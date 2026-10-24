import pytest
from src.engine.pravachan_resolver import resolve_pravachan_track, GITA_ADHYAY_MAP

def test_ghaisasi_guruji_day_and_artya():
    res1 = resolve_pravachan_track(
        filename="Day 1 1 A.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Bhagwat Katha\\Ghaisasi Guruji\\Day 1 1 A.mp3"
    )
    assert res1 is not None
    assert res1["language"] == "Pravachan"
    assert res1["category"] == "Bhagwat Katha\\Ghaisasi Guruji\\Day 01-05"
    assert res1["artist"] == "Ghaisasi Guruji"
    assert res1["album"] == "Bhagwat Katha - Ghaisasi Guruji - Day 01-05"
    assert res1["title"] == "Day 01 - Session 1A"

    res_art = resolve_pravachan_track(
        filename="Song 03.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Bhagwat Katha\\Ghaisasi Guruji\\Artya\\Song 03.mp3"
    )
    assert res_art is not None
    assert res_art["category"] == "Bhagwat Katha\\Ghaisasi Guruji\\Artya"
    assert res_art["title"] == "Arti - Song 03"

def test_kavishwar_maharaj():
    res = resolve_pravachan_track(
        filename="Kshwar 02B.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Bhagwat Katha\\Kavishwar Maharaj\\Kshwar 02B.mp3"
    )
    assert res is not None
    assert res["language"] == "Pravachan"
    assert res["category"] == "Bhagwat Katha\\Kavishwar Maharaj"
    assert res["artist"] == "Kavishwar Maharaj"
    assert res["title"] == "Kavishwar Maharaj - Session 02B"

def test_shankar_abhyankar_gita_nirupan():
    res = resolve_pravachan_track(
        filename="Aatmsanyamyog 01.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Shankar Abhyankar\\Bhagavad Gita\\Aatmsanyamyog 01.mp3"
    )
    assert res is not None
    assert res["language"] == "Pravachan"
    assert res["category"] == "Shankar Abhyankar\\Bhagavad Gita - Nirupan"
    assert res["artist"] == "Dr. Shankar Abhyankar"
    assert res["album"] == "Bhagavad Gita - Nirupan"
    assert res["title"] == "Adhyay 06 - Aatmsanyamyog Part 1"

    res2 = resolve_pravachan_track(
        filename="Aatmsanyamyog 02.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Shankar Abhyankar\\Bhagavad Gita\\Aatmsanyamyog 02.mp3"
    )
    assert res2 is not None
    assert res2["title"] == "Adhyay 06 - Aatmsanyamyog Part 2"

def test_aparna_abhyankar_gita_pathan():
    res = resolve_pravachan_track(
        filename="Aparna Abhyankar - 01 - Track 1.mp3",
        source_path="D:\\Songs\\unorganized\\Pravachan\\Aparna Abhyankar\\Aparna Abhyankar - 01 - Track 1.mp3"
    )
    assert res is not None
    assert res["language"] == "Pravachan"
    assert res["category"] == "Gita Pathan\\Aparna Abhyankar"
    assert res["artist"] == "Aparna Abhyankar"
    assert res["title"] == "Bhagavad Gita - Adhyay 01"

def test_marathi_katha_song_exclusions():
    res_ragh = resolve_pravachan_track(
        filename="Raghavachi Katha.mp3",
        source_path="D:\\Songs\\unorganized\\Marathi\\Raghavachi Katha.mp3"
    )
    assert res_ragh is not None
    assert res_ragh["language"] == "Marathi"
    assert res_ragh["category"] == "Geet Ramayan"
    assert res_ragh["title"] == "Raghavachi Katha"

    res_swar = resolve_pravachan_track(
        filename="Swar Gangechya Kathawarati.mp3",
        source_path="D:\\Songs\\unorganized\\Marathi\\Swar Gangechya Kathawarati.mp3"
    )
    assert res_swar is not None
    assert res_swar["language"] == "Marathi"
    assert res_swar["category"] == "Arun Date"
    assert res_swar["title"] == "Swar Gangechya Kathavarti"
