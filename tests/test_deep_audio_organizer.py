"""
Tests for DeepAudioOrganizer and enhanced classification logic.
Verifies Sanskrit Vedic Suktas vs Stotras, Bollywood Omkara disambiguation,
and AirLLM device adaptation.
"""

import os
import pytest
from src.engine.deep_audio_organizer import DeepAudioOrganizer, compute_audio_hash
from src.engine.embedded_intelligence import EmbeddedLanguageIntelligence
from src.engine.pattern_classifier import parse_track_details

def test_omkara_bollywood_classification():
    organizer = DeepAudioOrganizer()
    
    # Verify Omkara movie tracks are recognized as Hindi Soundtracks
    omkara_tracks = [
        ("Omkara - Beedi.mp3", "Beedi"),
        ("Omkara - Naina.mp3", "Naina"),
        ("Omkara - Namak.mp3", "Namak"),
        ("Omkara - Omkara.mp3", "Omkara")
    ]
    
    for fn, expected_title in omkara_tracks:
        res = organizer.classify_audio_track(
            file_path=f"D:\\Songs\\unorganized\\{fn}",
            filename=fn,
            tag_album="Omkara",
            tag_artist="Vishal Bhardwaj"
        )
        assert res["language"] == "Hindi"
        assert "Omkara" in res["category"]
        assert res["title"] == expected_title

def test_sanskrit_vedic_suktas_classification():
    organizer = DeepAudioOrganizer()
    
    sukta_files = [
        ("Purush-sukt.wma", "Purusha Suktam"),
        ("Shreesukt.wma", "Shree Suktam"),
        ("Rudra.mp3", "Shri Rudram"),
        ("Pavaman 1.mp3", "Pavamana Suktam"),
        ("Shri Ganapati Aatharvasheersham.mp3", "Ganapati Atharvashirsha"),
        ("Saur.wma", "Saura Suktam"),
        ("Trisuparna.wma", "Trisuparna Suktam"),
        ("11ratrisuktam-saptashati-pauranik.mp3", "Ratri Suktam")
    ]
    
    for fn, expected_title in sukta_files:
        res = organizer.classify_audio_track(
            file_path=f"D:\\Songs\\Morning\\{fn}",
            filename=fn
        )
        assert res["language"] == "Sanskrit", f"Failed for {fn}"
        assert res["category"] == "Vedic Suktas", f"Failed for {fn}"
        assert res["title"] == expected_title, f"Failed for {fn}"

def test_sanskrit_stotras_and_ashtakams():
    organizer = DeepAudioOrganizer()
    
    stotra_files = [
        ("09nirvanashatakam-shri aadi shankaracharya.mp3", "Nirvana Shatakam"),
        ("MahishasurmardiniStotra.mp3", "Mahishasuramardini Stotram"),
        ("Shri shivatandav stotram.mp3", "Shiva Tandava Stotram"),
        ("Vishnu sahastranam.wma", "Vishnu Sahasranama Stotram"),
        ("Annapoorna Stotram.mp3", "Annapoorna Stotram"),
        ("05bhavanyashtakam-shri aadi shankaracharya.mp3", "Bhavani Ashtakam"),
        ("Sounds Of Isha - Bilvashtakam Trigun Shiva Mantra.mp3", "Bilvashtakam")
    ]
    
    for fn, expected_title in stotra_files:
        res = organizer.classify_audio_track(
            file_path=f"D:\\Songs\\Morning\\{fn}",
            filename=fn
        )
        assert res["language"] == "Sanskrit", f"Failed for {fn}"
        assert res["category"] == "Stotras & Ashtakams", f"Failed for {fn}"
        assert res["title"] == expected_title, f"Failed for {fn}"

def test_nirvana_band_vs_nirvana_shatakam():
    organizer = DeepAudioOrganizer()
    
    # Nirvana Shatakam -> Sanskrit Stotra
    res_shatakam = organizer.classify_audio_track(
        file_path=r"D:\Songs\Morning\Nirvanashatakam.mp3",
        filename="Nirvanashatakam.mp3"
    )
    assert res_shatakam["language"] == "Sanskrit"
    assert res_shatakam["category"] == "Stotras & Ashtakams"
    
    # Nirvana Grunge Band -> English
    res_band = organizer.classify_audio_track(
        file_path=r"D:\Songs\English\001 - Nirvana - Smells Like Teen Spirit.mp3",
        filename="001 - Nirvana - Smells Like Teen Spirit.mp3",
        tag_artist="Nirvana"
    )
    assert res_band["language"] == "English"
    assert res_band["category"] == "Nirvana"

def test_airllm_device_adaptation():
    intelligence = EmbeddedLanguageIntelligence(enable_airllm=False)
    # Confirm fallback operates cleanly on CPU
    res = intelligence.classify_ambiguous_track("TestSong.mp3")
    assert res is not None
    assert "language" in res
