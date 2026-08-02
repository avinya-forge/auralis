import os
import shutil
import pytest
from unittest.mock import patch
from src.utils.file_utils import (
    ensure_dir_exists,
    move_file,
    calculate_file_hash,
    get_file_size,
    get_file_extension,
    clean_string,
    sanitize_filename,
    format_filename,
    remove_empty_directories,
    ensure_unique_filename,
)


def test_ensure_dir_exists(tmp_path):
    new_dir = tmp_path / "new_dir"

    # Test creation
    assert ensure_dir_exists(str(new_dir)) is True
    assert new_dir.exists()

    # Test exception (mocking os.makedirs)
    with patch("os.makedirs", side_effect=Exception("Permission denied")):
        assert ensure_dir_exists("/root/protected") is False


def test_move_file(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("hello")
    dest = tmp_path / "dest" / "dest.txt"

    # Test move
    assert move_file(str(src), str(dest)) is True
    assert dest.exists()
    assert not src.exists()

    # Test copy
    src.write_text("hello again")
    dest_copy = tmp_path / "dest" / "dest_copy.txt"
    assert move_file(str(src), str(dest_copy), copy_only=True) is True
    assert src.exists()
    assert dest_copy.exists()

    # Test exception
    with patch("shutil.move", side_effect=Exception("Failed to move")):
        assert move_file(str(src), str(dest)) is False


def test_calculate_file_hash(tmp_path):
    test_file = tmp_path / "hash_test.txt"
    test_file.write_text("hello world")

    # Expected md5 for "hello world" is 5eb63bbbe01eeed093cb22bb8f5acdc3
    # Expected sha1 is 2aae6c35c94fcfb415dbe95f408b9ce91ee846ed
    # Expected sha256 is b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

    assert calculate_file_hash(str(test_file), algorithm="md5") == "5eb63bbbe01eeed093cb22bb8f5acdc3"
    assert calculate_file_hash(str(test_file), algorithm="sha1") == "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"
    assert calculate_file_hash(str(test_file), algorithm="sha256") == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    # Test unsupported algorithm
    assert calculate_file_hash(str(test_file), algorithm="md4") is None

    # Test file reading exception
    assert calculate_file_hash("/nonexistent/file.txt") is None


def test_get_file_size(tmp_path):
    test_file = tmp_path / "size_test.txt"
    test_file.write_text("hello")  # 5 bytes

    assert get_file_size(str(test_file)) == 5

    # Test exception
    assert get_file_size("/nonexistent/file.txt") == 0


def test_get_file_extension():
    assert get_file_extension("audio.MP3") == ".mp3"
    assert get_file_extension("audio.Wav") == ".wav"
    assert get_file_extension("no_extension") == ""

    with patch("os.path.splitext", side_effect=Exception("Error")):
        assert get_file_extension("test.txt") == ""


def test_clean_string():
    assert clean_string(None) == ""
    assert clean_string("") == ""
    assert clean_string("  Hello World  ") == "Hello World"
    assert clean_string("01 - Song") == "Song"
    assert clean_string("[01] Song") == "Song"
    assert clean_string("Song (Official Video)") == "Song"
    assert clean_string("Song [Remastered]") == "Song"
    assert clean_string("Song HD") == "Song"
    assert clean_string("Song   -   Artist") == "Song-Artist"


def test_sanitize_filename():
    assert sanitize_filename(None) == "Unknown"
    assert sanitize_filename("") == "Unknown"
    assert sanitize_filename("Good Name") == "Good_Name"
    assert sanitize_filename("Bad Name ///???") == "Bad_Name"
    assert sanitize_filename("A" * 150) == "A" * 100
    assert sanitize_filename("???") == "Unknown"
    assert sanitize_filename("Multiple---Dash___Underscore") == "Multiple_Dash_Underscore"


def test_format_filename():
    assert format_filename("Title", artist="Artist", extension=".mp3") == "Title-Artist.mp3"
    assert format_filename("Title", movie="Movie", extension="mp3") == "Title-Movie.mp3"
    assert format_filename("Title") == "Title"
    assert format_filename(None, artist="Artist") == "Unknown_Title-Artist"


def test_remove_empty_directories(tmp_path):
    # Setup structure
    base = tmp_path / "base"
    base.mkdir()
    (base / "empty1").mkdir()
    (base / "empty2").mkdir()
    (base / "empty2" / "empty3").mkdir()

    not_empty = base / "not_empty"
    not_empty.mkdir()
    (not_empty / "file.txt").write_text("data")

    # Call method
    removed = remove_empty_directories(str(base))

    # 2 empty directories should be removed (empty1, empty3)
    # empty2 won't be removed because in the walk dirnames had 'empty3'
    assert removed == 2
    assert not (base / "empty1").exists()
    assert (base / "empty2").exists()
    assert not (base / "empty2" / "empty3").exists()
    assert (base / "not_empty").exists()

    # Test invalid path
    assert remove_empty_directories("/nonexistent/path") == 0

    # Test rmdir OSError by patching
    (base / "empty4").mkdir()
    with patch("os.rmdir", side_effect=OSError("Perm denied")):
        assert remove_empty_directories(str(base)) == 0


def test_ensure_unique_filename(tmp_path):
    test_file = tmp_path / "unique.txt"

    # If not exists, returns original
    assert ensure_unique_filename(str(test_file)) == str(test_file)

    # Create file
    test_file.write_text("data")

    # Now it should append (1)
    expected_1 = str(tmp_path / "unique (1).txt")
    assert ensure_unique_filename(str(test_file)) == expected_1

    # Create the (1) file
    (tmp_path / "unique (1).txt").write_text("data")

    # Now it should append (2)
    expected_2 = str(tmp_path / "unique (2).txt")
    assert ensure_unique_filename(str(test_file)) == expected_2
