"""
Auralis - File Utilities Module
"""

import hashlib
import os
import re
import shutil
from typing import Optional


def ensure_dir_exists(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary

    Args:
        path (str): Directory path

    Returns:
        bool: True if successful
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {str(e)}")
        return False


def move_file(src: str, dest: str, copy_only: bool = False) -> bool:
    """
    Move or copy a file, ensuring the destination directory exists

    Args:
        src (str): Source file path
        dest (str): Destination file path
        copy_only (bool): If True, copy instead of move

    Returns:
        bool: True if successful
    """
    try:
        # Ensure destination directory exists
        dest_dir = os.path.dirname(dest)
        ensure_dir_exists(dest_dir)

        # Move or copy file
        if copy_only:
            shutil.copy2(src, dest)
        else:
            shutil.move(src, dest)

        return True
    except Exception as e:
        print(f"Error moving file {src} to {dest}: {str(e)}")
        return False


def calculate_file_hash(
    file_path: str, block_size: int = 65536, algorithm: str = "md5"
) -> Optional[str]:
    """
    Calculate hash of a file

    Args:
        file_path (str): Path to the file
        block_size (int): Size of blocks to read
        algorithm (str): Hash algorithm ('md5', 'sha1', 'sha256')

    Returns:
        str: Hash of the file
    """
    try:
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha1":
            hasher = hashlib.sha1()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        with open(file_path, "rb") as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)

        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {str(e)}")
        return None


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes

    Args:
        file_path (str): Path to the file

    Returns:
        int: Size of the file in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        print(f"Error getting file size for {file_path}: {str(e)}")
        return 0


def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file

    Args:
        file_path (str): Path to the file

    Returns:
        str: Extension of the file (lowercase, with dot)
    """
    try:
        return os.path.splitext(file_path)[1].lower()
    except Exception as e:
        print(f"Error getting file extension for {file_path}: {str(e)}")
        return ""


def clean_string(text: Optional[str]) -> str:
    """
    Clean a string by removing unnecessary characters

    Args:
        text (str): String to clean

    Returns:
        str: Cleaned string
    """
    if not text:
        return ""

    # Remove leading/trailing whitespace
    text = text.strip()

    # Remove track numbers at beginning (e.g. "01 - ", "01.", "01 ", "[01]", etc.)
    text = re.sub(r"^(\d+[\s\.\-\[\]_]*)", "", text)

    # Remove unnecessary brackets and parentheses along with their content
    text = re.sub(r"\([^\)]*\)", "", text)  # Remove (anything)
    text = re.sub(r"\[[^\]]*\]", "", text)  # Remove [anything]
    text = re.sub(r"\{[^\}]*\}", "", text)  # Remove {anything}

    # Remove common suffixes like "Official Video", "HD", "HQ", etc.
    suffixes = [
        r"official\s*video",
        r"official\s*audio",
        r"official\s*music\s*video",
        r"lyrics\s*video",
        r"lyric\s*video",
        r"audio\s*only",
        r"full\s*album",
        r"full\s*song",
        r"original\s*soundtrack",
        r"hd",
        r"hq",
        r"high\s*quality",
        r"remastered",
        r"320\s*kbps",
        r"128\s*kbps",
        r"mp3",
        r"flac",
    ]
    for suffix in suffixes:
        text = re.sub(rf"(?i)[-\s]+{suffix}[-\s]*$", "", text)

    # Remove double spaces
    text = re.sub(r"\s+", " ", text)

    # Remove extra spaces around common separators
    text = re.sub(r"\s*-\s*", "-", text)  # Remove spaces around hyphens
    text = re.sub(r"\s*_\s*", "_", text)  # Remove spaces around underscores
    text = re.sub(r"\s*\.\s*", ".", text)  # Remove spaces around periods

    # Final trim
    text = text.strip()

    return text


def sanitize_filename(name: Optional[str]) -> str:
    """
    Sanitize a string to be used as a filename

    Args:
        name (str): String to sanitize

    Returns:
        str: Sanitized string
    """
    if not name:
        return "Unknown"

    # First clean the string
    name = clean_string(name)

    # Strictly enforce alphanumeric characters only, with limited separators
    # Keep only alphanumeric (0-9, a-z, A-Z) and specific separator characters
    allowed_chars = r"a-zA-Z0-9\-_ "
    name = re.sub(f"[^{allowed_chars}]", "", name)

    # Replace spaces with underscores for better compatibility
    name = name.replace(" ", "_")

    # Replace multiple separators with a single one
    name = re.sub(r"[-_]{2,}", "_", name)

    # Remove leading and trailing separators
    name = name.strip("-_")

    # Limit length
    if len(name) > 100:
        name = name[:100]

    # Ensure not empty
    if not name:
        return "Unknown"

    return name


def format_filename(
    title: Optional[str],
    artist: Optional[str] = None,
    movie: Optional[str] = None,
    extension: Optional[str] = None,
) -> str:
    """
    Format a filename according to the pattern 'songname - artistname' or 'songname - moviename'

    Args:
        title (str): Song title
        artist (str, optional): Artist name
        movie (str, optional): Movie name
        extension (str, optional): File extension

    Returns:
        str: Formatted filename
    """
    # Clean inputs
    clean_title = clean_string(title) if title else "Unknown_Title"
    clean_artist = clean_string(artist) if artist else None
    clean_movie = clean_string(movie) if movie else None

    # Format filename
    if clean_artist:
        filename = f"{clean_title}-{clean_artist}"
    elif clean_movie:
        filename = f"{clean_title}-{clean_movie}"
    else:
        filename = clean_title

    # Sanitize to ensure only allowed characters
    filename = sanitize_filename(filename)

    # Add extension if provided
    if extension:
        if not extension.startswith("."):
            extension = f".{extension}"
        filename = f"{filename}{extension}"

    return filename


def remove_empty_directories(path: str) -> int:
    """
    Recursively remove empty directories

    Args:
        path (str): Directory path

    Returns:
        int: Number of directories removed
    """
    if not os.path.isdir(path):
        return 0

    # Count removed directories
    removed = 0

    # Walk from the bottom up
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
                removed += 1
                print(f"Removed empty directory: {dirpath}")
            except OSError:
                pass

    return removed


def ensure_unique_filename(file_path: str) -> str:
    """
    Ensure a filename is unique by adding a number if necessary

    Args:
        file_path (str): File path to check

    Returns:
        str: Unique file path
    """
    if not os.path.exists(file_path):
        return file_path

    base_path, ext = os.path.splitext(file_path)
    counter = 1

    while True:
        new_path = f"{base_path} ({counter}){ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1
