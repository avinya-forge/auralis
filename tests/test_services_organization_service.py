import os
from unittest.mock import patch

import pytest

from src.services.organization_service import OrganizationService


@pytest.fixture
def service():
    return OrganizationService()


def test_scan_directory(service, tmp_path):
    # Create some files
    (tmp_path / "test1.mp3").touch()
    (tmp_path / "test2.flac").touch()
    (tmp_path / "test3.txt").touch()

    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "test4.wav").touch()

    files = service.scan_directory(str(tmp_path))
    assert len(files) == 3
    assert any(f.endswith("test1.mp3") for f in files)
    assert any(f.endswith("test2.flac") for f in files)
    assert any(f.endswith("test4.wav") for f in files)


def test_scan_directory_exception(service, tmp_path):
    with patch("os.walk") as mock_walk:
        mock_walk.side_effect = Exception("Test error")
        files = service.scan_directory(str(tmp_path))
        assert files == []


def test_sanitize_filename(service):
    assert service.sanitize_filename("") == "Unknown"
    assert service.sanitize_filename(None) == "Unknown"
    assert service.sanitize_filename('invalid<>:"/\\|?*name') == "invalid_________name"
    assert service.sanitize_filename("  spaces  ") == "spaces"
    assert service.sanitize_filename("..dots..") == "dots"
    assert service.sanitize_filename("multiple   spaces") == "multiple spaces"


def test_organize_file_copy(service, tmp_path):
    source_file = tmp_path / "source.mp3"
    source_file.touch()

    metadata = {"artist": "Test Artist", "album": "Test Album", "title": "Test Title"}

    target_root = tmp_path / "target"

    with patch("shutil.copy2") as mock_copy:
        result = service.organize_file(str(source_file), metadata, str(target_root), move=False)

        expected_target = os.path.join(
            str(target_root), "Test Artist", "Test Album", "Test Title.mp3"
        )
        assert result == expected_target
        mock_copy.assert_called_once_with(str(source_file), expected_target)


def test_organize_file_move(service, tmp_path):
    source_file = tmp_path / "source.flac"
    source_file.touch()

    metadata = {"artist": "Test Artist", "album": "Test Album", "title": "Test Title"}

    target_root = tmp_path / "target"

    with patch("shutil.move") as mock_move:
        result = service.organize_file(str(source_file), metadata, str(target_root), move=True)

        expected_target = os.path.join(
            str(target_root), "Test Artist", "Test Album", "Test Title.flac"
        )
        assert result == expected_target
        mock_move.assert_called_once_with(str(source_file), expected_target)


def test_organize_file_existing(service, tmp_path):
    source_file = tmp_path / "source.mp3"
    source_file.touch()

    metadata = {"artist": "Test Artist", "album": "Test Album", "title": "Test Title"}

    target_root = tmp_path / "target"
    target_dir = target_root / "Test Artist" / "Test Album"
    target_dir.mkdir(parents=True)
    existing_file = target_dir / "Test Title.mp3"
    existing_file.touch()

    with patch("shutil.copy2") as mock_copy:
        result = service.organize_file(str(source_file), metadata, str(target_root), move=False)

        expected_target = os.path.join(
            str(target_root), "Test Artist", "Test Album", "Test Title (1).mp3"
        )
        assert result == expected_target
        mock_copy.assert_called_once_with(str(source_file), expected_target)


def test_organize_file_same_path(service, tmp_path):
    target_root = tmp_path / "target"
    target_dir = target_root / "Test Artist" / "Test Album"
    target_dir.mkdir(parents=True)
    source_file = target_dir / "Test Title.mp3"
    source_file.touch()

    metadata = {"artist": "Test Artist", "album": "Test Album", "title": "Test Title"}

    result = service.organize_file(str(source_file), metadata, str(target_root), move=False)
    assert result == str(source_file)


def test_organize_file_exception(service, tmp_path):
    source_file = tmp_path / "source.mp3"
    source_file.touch()

    metadata = {"artist": "Test Artist", "album": "Test Album", "title": "Test Title"}

    target_root = tmp_path / "target"

    with patch("os.makedirs") as mock_makedirs:
        mock_makedirs.side_effect = Exception("Test error")
        result = service.organize_file(str(source_file), metadata, str(target_root), move=False)
        assert result is None
