"""
Tests for AcousticDeduplicationEngine and Path Sanitizer Noise Stripping.
"""

from src.engine.path_sanitizer import (
    strip_rip_noise_and_suffixes,
    separate_artist_from_song_title,
    clean_audio_title,
    remove_brackets_and_special_chars,
)
from src.engine.embedded_intelligence import (
    AcousticDeduplicationEngine,
)


def test_strip_rip_noise_and_suffixes():
    assert strip_rip_noise_and_suffixes("") == ""
    assert strip_rip_noise_and_suffixes("Aane Wala Pal11 S") == "Aane Wala Pal"
    assert strip_rip_noise_and_suffixes("Na Jaane Kyun720P Hd Song") == "Na Jaane Kyun"
    assert strip_rip_noise_and_suffixes("Dil Kya Kare03 S") == "Dil Kya Kare"
    assert strip_rip_noise_and_suffixes("Bachnaaehaseeno01") == "Bachnaaehaseeno"
    assert strip_rip_noise_and_suffixes("Aane Wala Pal -Golmaal") == "Aane Wala Pal"


def test_separate_artist_from_song_title():
    assert separate_artist_from_song_title("") == ""

    # Song - Artist format
    title1 = separate_artist_from_song_title("Aarambh - Piyush Mishra")
    assert title1 == "Aarambh"

    # Track number prefix: 01 - Song Title
    title_num = separate_artist_from_song_title("01 - Stray Number Track")
    assert title_num == "Stray Number Track"

    # With matching folder artist on right
    title_r = separate_artist_from_song_title("Aarambh - Piyush Mishra", folder_artist="Piyush Mishra")
    assert title_r == "Aarambh"

    # With matching folder artist on left
    title_l = separate_artist_from_song_title("Neeraj Sridhar - Bhool Bhulaiyaa", folder_artist="Neeraj Sridhar")
    assert title_l == "Bhool Bhulaiyaa"

    # Modifier on right (Alt, Remix)
    title_mod = separate_artist_from_song_title("Tum Jo Aaye - Alt")
    assert title_mod == "Tum Jo Aaye - Alt"

    # Known artist suffix
    title2 = separate_artist_from_song_title("Maaeri Euphoria", folder_artist="Euphoria")
    assert title2 == "Maaeri"

    title3 = separate_artist_from_song_title("Chammak Challo Akon", folder_artist="Akon")
    assert title3 == "Chammak Challo"


def test_clean_audio_title_and_folders():
    assert clean_audio_title("") == "Untitled"
    assert clean_audio_title("Taxi No 9211") == "Taxi No 9211"
    assert clean_audio_title("Day 01 Ram Katha") == "Day 01 Ram Katha"
    assert clean_audio_title("Aane Wala Pal11 S") == "Aane Wala Pal"
    assert clean_audio_title("Na Jaane Kyun720P Hd Song") == "Na Jaane Kyun"
    assert clean_audio_title("Aarambh - Piyush Mishra") == "Aarambh"
    assert clean_audio_title("Summer of 69") == "Summer Of 69"

    # Preserving authorized numbers in song titles
    assert clean_audio_title("Song Part 1") == "Song Part 1"
    assert clean_audio_title("Track 9211") == "Track 9211"
    assert clean_audio_title("01 - Stray Number Track 12") == "Stray Number Track 12"

    # Folder mode with numbers
    assert clean_audio_title("Album 01", is_folder=True) == "Album"
    assert clean_audio_title("1942 A Love Story", is_folder=True) == "1942 A Love Story"
    assert clean_audio_title("3 Idiots", is_folder=True) == "3 Idiots"


def test_remove_brackets_and_special_chars():
    assert remove_brackets_and_special_chars("") == ""
    assert remove_brackets_and_special_chars("[songs.pk] Track Name") == "Track Name"
    assert remove_brackets_and_special_chars("Track (Boyzone)") == "Track Boyzone"
    assert remove_brackets_and_special_chars("Illegal: chars") == "Illegal- chars"


def test_acoustic_deduplication_engine():
    engine = AcousticDeduplicationEngine()

    assert engine.normalize_title("") == ""
    assert engine.normalize_title("Aanewala Pal Jaane Waala Hai") == "aanewalapaljaanewaalahai"
    assert engine.normalize_title("Aane Wala Pal11 S") == "aanewalapal"

    # Test duplicate comparison
    assert engine.are_tracks_duplicate(
        "Aane Wala Pal -Golmaal", "Aanewala Pal Jaane Waala Hai",
        dur1=280.0, dur2=281.5
    )
    assert not engine.are_tracks_duplicate(
        "Aane Wala Pal", "Golmaal Hai",
        dur1=280.0, dur2=280.0
    )
    assert not engine.are_tracks_duplicate("", "Golmaal", dur1=0, dur2=0)


def test_select_best_master_track():
    engine = AcousticDeduplicationEngine()

    cand1 = {
        "path": "path1.mp3",
        "filename": "Aane Wala Pal11 S.mp3",
        "bitrate": 128000,
        "duration": 280.0,
    }
    cand2 = {
        "path": "path2.mp3",
        "filename": "Aanewala Pal Jaane Waala Hai.mp3",
        "bitrate": 256000,
        "duration": 282.0,
    }

    best, duplicates = engine.select_best_master_track([cand1, cand2])
    assert best["path"] == "path2.mp3"
    assert len(duplicates) == 1
    assert duplicates[0]["path"] == "path1.mp3"

    # Single track or empty
    assert engine.select_best_master_track([]) == (None, [])
    assert engine.select_best_master_track([cand1]) == (cand1, [])
