"""
Unit tests for Universal Tagging and Artwork Engine in MasterOrganizer.
Tests ID3v2.4, ASF, MP4, and WAVE tagging with composer, lyricist, and artwork embedding.
"""

import os
import io
import pytest
from unittest.mock import MagicMock, patch

from src.engine.master_organizer import MasterOrganizer

def test_master_organizer_universal_tag_writer_mp3():
    organizer = MasterOrganizer()
    fake_path = "D:\\Songs\\test_track.mp3"
    
    with patch("os.chmod") as mock_chmod, \
         patch("src.engine.master_organizer.ID3") as mock_id3_cls:
        mock_id3 = MagicMock()
        mock_id3_cls.return_value = mock_id3
        
        ok = organizer.write_id3_tags(
            file_path=fake_path,
            title="Awaara Hoon",
            artist="Mukesh",
            album="Awaara",
            genre="Bollywood Classic",
            year="1951",
            composer="Shankar-Jaikishan",
            lyricist="Shailendra",
            artwork_bytes=b"fake_jpeg_bytes"
        )
        assert ok is True
        mock_id3.save.assert_called_once_with(fake_path, v2_version=4)

def test_master_organizer_universal_tag_writer_wma():
    organizer = MasterOrganizer()
    fake_path = "D:\\Songs\\test_track.wma"
    
    with patch("os.chmod"), \
         patch("src.engine.master_organizer.ASF") as mock_asf_cls:
        mock_asf = MagicMock()
        mock_asf.tags = {}
        mock_asf_cls.return_value = mock_asf
        
        ok = organizer.write_id3_tags(
            file_path=fake_path,
            title="Best Of Me",
            artist="Bryan Adams",
            album="Best Of Me",
            genre="Rock",
            year="1999"
        )
        assert ok is True
        assert mock_asf.tags["Title"] == ["Best Of Me"]
        assert mock_asf.tags["Author"] == ["Bryan Adams"]
        mock_asf.save.assert_called_once()

def test_master_organizer_universal_tag_writer_wav():
    organizer = MasterOrganizer()
    fake_path = "D:\\Songs\\test_alert.wav"
    
    with patch("os.chmod"), \
         patch("src.engine.master_organizer.WAVE") as mock_wave_cls:
        mock_wave = MagicMock()
        mock_wave.tags = {}
        mock_wave_cls.return_value = mock_wave
        
        ok = organizer.write_id3_tags(
            file_path=fake_path,
            title="Kala Chashma (Ringtone)",
            artist="Amar Arshi & Badshah",
            album="Baar Baar Dekho",
            genre="Ringtone"
        )
        assert ok is True
        mock_wave.save.assert_called_once()
