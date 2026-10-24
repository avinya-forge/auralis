"""
Unit tests for EmbeddedLanguageIntelligence, LanguageParallelEngine, and organize-nvme CLI command
"""

import os
import sqlite3
import tempfile
import pytest
from src.engine.embedded_intelligence import EmbeddedLanguageIntelligence
from src.engine.language_parallel_engine import LanguageParallelEngine
from src.cli.cli_main import setup_parser

def test_embedded_language_intelligence():
    """Confirms that EmbeddedLanguageIntelligence classifies tracks across languages in-process with minimal RAM."""
    intelligence = EmbeddedLanguageIntelligence(enable_airllm=False)
    
    # Hindi classification
    res_hindi = intelligence.classify_track("001 AAH = YE SHAAM.mp3", album="Aah")
    assert res_hindi["language"] == "Hindi"
    assert "Aah" in res_hindi["category"]

    # Sanskrit classification
    res_sanskrit = intelligence.classify_track("Daridraya_Dahana_Stotram.mp3")
    assert res_sanskrit["language"] == "Sanskrit"

    # English classification
    res_eng = intelligence.classify_track("Smells Like Teen Spirit.mp3", artist="Nirvana")
    assert res_eng["language"] == "English"
    assert res_eng["category"] == "Nirvana"

def test_language_parallel_engine_safety():
    """Verifies that LanguageParallelEngine processes tracks concurrently with zero overwrite safety."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        out_root = os.path.join(tmpdir, "organized")
        
        # Create test source files
        s1 = os.path.join(tmpdir, "song1.mp3")
        s2 = os.path.join(tmpdir, "song2.mp3")
        with open(s1, "wb") as f:
            f.write(b"AUDIO1" * 200)
        with open(s2, "wb") as f:
            f.write(b"AUDIO2" * 250)

        plan_items = [
            {
                "original_path": s1,
                "target_path": os.path.join(out_root, "English", "Nirvana", "Track.mp3"),
                "status": "ORGANIZE_UNIQUE",
                "parsed": {"language": "English", "category": "Nirvana", "title": "Track", "artist": "Nirvana", "album": "Nevermind"}
            },
            {
                "original_path": s2,
                "target_path": os.path.join(out_root, "English", "Nirvana", "Track.mp3"), # Potential collision!
                "status": "ORGANIZE_UNIQUE",
                "parsed": {"language": "English", "category": "Nirvana", "title": "Track", "artist": "Nirvana", "album": "Nevermind"}
            }
        ]

        engine = LanguageParallelEngine(db_path=db_path, output_root=out_root, num_workers=2)
        res = engine.execute_parallel(plan_items)
        assert res["total_processed"] == 2
        assert res["files_organized_and_copied"] == 2

        # Verify zero overwrites: both files exist, second file disambiguated with (1)
        f1 = os.path.join(out_root, "English", "Nirvana", "Track.mp3")
        f2 = os.path.join(out_root, "English", "Nirvana", "Track (1).mp3")
        assert os.path.exists(f1)
        assert os.path.exists(f2)
        assert os.path.getsize(f1) != os.path.getsize(f2)

def test_cli_organize_nvme_parser():
    """Verifies that the organize-nvme CLI subcommand is properly registered and configured."""
    parser = setup_parser()
    args = parser.parse_args(["organize-nvme", "--dry-run", "--limit", "50", "--destination", r"D:\Songs\test_org", "--parallel-workers", "5"])
    assert args.command == "organize-nvme"
    assert args.dry_run is True
    assert args.limit == 50
    assert args.destination == r"D:\Songs\test_org"
    assert args.parallel_workers == 5
