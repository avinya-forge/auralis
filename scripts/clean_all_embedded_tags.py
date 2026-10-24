import os
import re
import stat
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON

ORGANIZED_ROOT = r"D:\Songs\organized"

SPAM_REGEX = re.compile(
    r'\b(www\.[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-\.]+\.(com|pk|in|net|org)|songs\.pk|djluv|papuyaar|apniisp|downloadming|mp3pk)\b',
    re.I
)

def clean_tag_text(text: str) -> str:
    if not text:
        return ""
    # Strip watermarks
    cleaned = SPAM_REGEX.sub("", text)
    # Strip brackets
    cleaned = re.sub(r'[\(\)\[\]\{\}]', '', cleaned)
    # Strip dirty symbols
    cleaned = re.sub(r'[\$\%\!\@\~\+\^\=\;\`\#]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip('. -_,')
    return cleaned

def sweep_and_clean_tags():
    print("=" * 80)
    print(f"CLEANING EMBEDDED METADATA TAGS IN: {ORGANIZED_ROOT}")
    print("=" * 80)

    updated_count = 0
    missing_title_fixed = 0
    watermarks_removed = 0

    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in ['.mp3', '.wma']:
                continue

            p = os.path.join(root, f)
            stem = os.path.splitext(f)[0]
            clean_stem = clean_tag_text(stem)

            # Determine fallback artist and album from folder hierarchy
            rel = os.path.relpath(root, ORGANIZED_ROOT)
            parts = rel.split(os.sep)
            folder_genre = parts[0]
            folder_album = parts[-1] if len(parts) > 1 else folder_genre
            folder_artist = parts[-2] if len(parts) > 2 and parts[-2] not in ["Soundtracks", "Albums", "Artists", "Ghazals", "Devotional & Bhajans"] else (folder_album if "Artists" in rel else "Various Artists")

            try:
                os.chmod(p, stat.S_IWRITE)
                if ext == '.mp3':
                    try:
                        id3 = ID3(p)
                    except Exception:
                        id3 = ID3()

                    t_title = str(id3.get("TIT2", "")).strip()
                    t_artist = str(id3.get("TPE1", "")).strip()
                    t_album = str(id3.get("TALB", "")).strip()
                    t_genre = str(id3.get("TCON", "")).strip()

                    had_watermark = bool(SPAM_REGEX.search(f"{t_title} {t_artist} {t_album}"))
                    if had_watermark:
                        watermarks_removed += 1

                    c_title = clean_tag_text(t_title) or clean_stem
                    if not t_title:
                        missing_title_fixed += 1

                    c_artist = clean_tag_text(t_artist) or folder_artist
                    c_album = clean_tag_text(t_album) or folder_album
                    c_genre = clean_tag_text(t_genre) or folder_genre

                    id3["TIT2"] = TIT2(encoding=3, text=c_title)
                    id3["TPE1"] = TPE1(encoding=3, text=c_artist)
                    id3["TALB"] = TALB(encoding=3, text=c_album)
                    id3["TCON"] = TCON(encoding=3, text=c_genre)
                    id3.save(p, v2_version=3)
                    updated_count += 1

                elif ext == '.wma':
                    asf = mutagen.File(p)
                    if asf and asf.tags:
                        t_title = str(asf.tags.get("Title", [""])[0]).strip()
                        t_artist = str(asf.tags.get("Author", [""])[0]).strip()
                        t_album = str(asf.tags.get("WM/AlbumTitle", [""])[0]).strip()

                        c_title = clean_tag_text(t_title) or clean_stem
                        c_artist = clean_tag_text(t_artist) or folder_artist
                        c_album = clean_tag_text(t_album) or folder_album

                        asf.tags["Title"] = [c_title]
                        asf.tags["Author"] = [c_artist]
                        asf.tags["WM/AlbumTitle"] = [c_album]
                        asf.save()
                        updated_count += 1
            except Exception:
                pass

    print(f"Total files updated with clean tags: {updated_count}")
    print(f"Missing titles populated: {missing_title_fixed}")
    print(f"Web spam watermarks removed: {watermarks_removed}")

if __name__ == "__main__":
    sweep_and_clean_tags()
