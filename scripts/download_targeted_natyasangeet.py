r"""
Targeted downloader for essential missing Marathi Natyasangeet tracks.
Ensures every play folder has >= 2 tracks and 0 empty folders.
"""

import os
import io
import time
import requests
from PIL import Image
import imageio_ffmpeg
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, COMM, APIC, PictureType

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = r"D:\Songs\organized\Marathi\Natyasangeet"

TARGETS = [
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Lagi Kalejwa Kator",
        "artist": "Pt. Vasantrao Deshpande",
        "url": "https://www.youtube.com/watch?v=YbY6SFp6PMA",
    },
    {
        "play": "Sangeet Ekach Pyala",
        "title": "Vasudhatal Ramaniya Sudhakar",
        "artist": "Ramdas Kamat",
        "url": "https://www.youtube.com/watch?v=PK9kcsa9QXA",
    },
    {
        "play": "Sangeet Ekach Pyala",
        "title": "Lage Hrudayi Hurhur",
        "artist": "Ramdas Kamat",
        "url": "https://www.youtube.com/watch?v=6eiFL4QA1y8",
    },
    {
        "play": "Sangeet Sharada",
        "title": "Mhatara Ituka Na Avaghe",
        "artist": "Balgandharva",
        "url": "https://www.youtube.com/watch?v=nkDbOtnftHw",
    },
    {
        "play": "Sangeet Matsyagandha",
        "title": "Guntata Hriday He",
        "artist": "Ramdas Kamat",
        "url": "https://www.youtube.com/watch?v=QJKMTjVOddk",
    },
    {
        "play": "Sangeet Matsyagandha",
        "title": "Swar Gangechya Kathavarti",
        "artist": "Ramdas Kamat",
        "url": "https://www.youtube.com/watch?v=VmpMjznFlD8",
    },
    {
        "play": "Sangeet Manapman",
        "title": "Mala Madan Bhase",
        "artist": "Balgandharva",
        "url": "https://www.youtube.com/watch?v=4w_a8fTgcKk",
    },
]


def fetch_and_convert_thumb(thumb_url: str) -> bytes:
    """Download thumbnail and convert to JPEG bytes."""
    if not thumb_url:
        return b""
    try:
        r = requests.get(thumb_url, timeout=10)
        if r.status_code == 200:
            im = Image.open(io.BytesIO(r.content)).convert("RGB")
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
    except Exception:
        pass
    return b""


def main():
    for item in TARGETS:
        target_dir = os.path.join(BASE_DIR, item["play"])
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, item["title"] + ".mp3")
        if os.path.exists(target_path):
            print("Exists:", target_path)
            continue

        temp_base = f"temp_tgt_{int(time.time() * 1000)}"
        ydl_opts = {
            "ffmpeg_location": FFMPEG_EXE,
            "format": "bestaudio/best",
            "outtmpl": f"{temp_base}.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }
        print(f"Downloading {item['title']}...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(item["url"], download=True)
                thumb = info.get("thumbnail", "")

            temp_mp3 = f"{temp_base}.mp3"
            if os.path.exists(temp_mp3):
                os.rename(temp_mp3, target_path)

                art_bytes = fetch_and_convert_thumb(thumb)

                tags = ID3()
                tags.add(TIT2(encoding=3, text=[item["title"]]))
                tags.add(TPE1(encoding=3, text=[item["artist"]]))
                tags.add(TALB(encoding=3, text=[item["play"]]))
                tags.add(TCON(encoding=3, text=["Natyasangeet"]))
                comment = f"Marathi Sangeet Natak: {item['play']}"
                tags.add(COMM(encoding=3, lang="eng", desc="", text=[comment]))
                if art_bytes:
                    tags.add(
                        APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=PictureType.COVER_FRONT,
                            desc="Front Cover",
                            data=art_bytes,
                        )
                    )
                tags.save(target_path)
                print("Successfully saved:", target_path)
        except Exception as e:
            print("Failed:", item["title"], e)


if __name__ == "__main__":
    main()
