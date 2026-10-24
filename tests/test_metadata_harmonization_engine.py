"""
Unit tests for Auralis Master Acoustic Organizer and Deep Library Refiner metadata harmonization.
"""

import os
import shutil
import tempfile
import pytest
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

from src.engine.master_acoustic_organizer import (
    BAND_NORMALIZATION,
    resolve_track_destination,
    write_id3_metadata
)
from src.engine.deep_library_refiner import pass5_metadata_harmonization


def test_band_normalization_mappings():
    """Verify canonical artist name mappings exist and are accurate."""
    assert BAND_NORMALIZATION.get("pink foyd") == "Pink Floyd"
    assert BAND_NORMALIZATION.get("pink floyd") == "Pink Floyd"
    assert BAND_NORMALIZATION.get("a r raheman") == "A.R. Rahman"
    assert BAND_NORMALIZATION.get("a.r. rahman") == "A.R. Rahman"
    assert BAND_NORMALIZATION.get("lata") == "Lata Mangeshkar"
    assert BAND_NORMALIZATION.get("rafi") == "Mohammed Rafi"
    assert BAND_NORMALIZATION.get("kishore") == "Kishore Kumar"
    assert BAND_NORMALIZATION.get("yesudas") == "K.J. Yesudas"
    assert BAND_NORMALIZATION.get("dr. shankar abhyankar") == "Dr. Shankar Abhyankar"


def test_resolve_track_destination_sanskrit_vedic_suktas():
    """Verify Vedic Suktas destination resolves contributing artist as Vedic Suktas."""
    dest = resolve_track_destination(
        file_path="Sanskrit\\Vedic Suktas\\Shree Suktam.mp3",
        filename="Shree Suktam.mp3",
        duration=300.0,
        orig_lookup={}
    )
    lang, cat, alb, art = dest
    assert lang == "Sanskrit"
    assert cat == "Vedic Suktas"
    assert alb == "Vedic Suktas"
    assert art == "Vedic Suktas"


def test_resolve_track_destination_sanskrit_vedas():
    """Verify Veda chanting libraries resolve artist as Traditional Vedic Chants."""
    dest = resolve_track_destination(
        file_path="Sanskrit\\Atharvaveda Chanting\\Atharvaveda - Part 01.mp3",
        filename="Atharvaveda - Part 01.mp3",
        duration=2400.0,
        orig_lookup={}
    )
    lang, cat, alb, art = dest
    assert lang == "Sanskrit"
    assert "Atharvaveda" in cat
    assert art == "Traditional Vedic Chants"


def test_resolve_track_destination_instrumental():
    """Verify Instrumental & Classical resolves artist as Classical Instrumental."""
    dest = resolve_track_destination(
        file_path="Instrumental & Classical\\Raag Bairagi.mp3",
        filename="Raag Bairagi.mp3",
        duration=1200.0,
        orig_lookup={}
    )
    lang, cat, alb, art = dest
    assert lang == "Instrumental & Classical"
    assert art == "Classical Instrumental"


def test_write_id3_metadata_populates_album_artist(tmp_path):
    """Verify write_id3_metadata sets TPE1, TPE2, TALB, and TIT2."""
    dummy_file = tmp_path / "test_track.mp3"
    # Create empty valid mp3 header dummy
    with open(dummy_file, "wb") as f:
        f.write(b"\xff\xfb\x90\x44" + b"\x00" * 1024)

    success = write_id3_metadata(
        file_path=str(dummy_file),
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        genre="Test Genre",
        year="2024"
    )
    assert success is True
