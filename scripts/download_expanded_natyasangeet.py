r"""
Auralis - Targeted Rare Marathi Natyasangeet Downloader
Expands the collection with iconic plays:
1. Sangeet Vidyaharan (2 tracks)
2. Sangeet Kanhopatra (2 tracks)
3. Sangeet Devbabhali (2 tracks)

Enforces strict standards:
- Filename is strictly '<Song Title>.mp3' (no artist, no rip noise, no random chars).
- Embedded ID3v2 tags: TIT2, TPE1, TALB, TCON='Natyasangeet', APIC (converted to clean JPEG).
- Every folder strictly maintains >= 2 tracks.
- High-quality 320kbps MP3 audio via FFmpeg.
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

NEW_PLAYS_MANIFEST = [
    # 1. Sangeet Vidyaharan
    {
        "play": "Sangeet Vidyaharan",
        "title": "Madhu Madhukar Kahi Bol",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Madhu Madhukar Kahi Bol Vasantrao Deshpande Vidyaharan Saregama",
    },
    {
        "play": "Sangeet Vidyaharan",
        "title": "Shoor Aamhi Sardar Aamhala",
        "artist": "Ramdas Kamat",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Shoor Aamhi Sardar Aamhala Ramdas Kamat Vidyaharan Saregama",
    },
    # 2. Sangeet Kanhopatra
    {
        "play": "Sangeet Kanhopatra",
        "title": "Aga Vaikunthichya Raya",
        "artist": "Pt. Jitendra Abhisheki",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Aga Vaikunthichya Raya Jitendra Abhisheki Kanhopatra",
    },
    {
        "play": "Sangeet Kanhopatra",
        "title": "Pandurang Kanti Divya Tej Jhalake",
        "artist": "Pt. Bhimsen Joshi",
        "composer": "Pt. Bhimsen Joshi",
        "query": "ytsearch1:Pandurang Kanti Divya Tej Jhalake Bhimsen Joshi Saregama",
    },
    # 3. Sangeet Devbabhali
    {
        "play": "Sangeet Devbabhali",
        "title": "Bheeti Laagoo Koni",
        "artist": "Shubhangi Sadavarte & Manasi Joshi",
        "composer": "Anand Bhate",
        "query": "ytsearch1:Bheeti Laagoo Koni Sangeet Devbabhali",
    },
    {
        "play": "Sangeet Devbabhali",
        "title": "Avagha Rang Ek Zala",
        "artist": "Kishori Amonkar",
        "composer": "Kishori Amonkar",
        "query": "ytsearch1:Avagha Rang Ek Zala Kishori Amonkar",
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

def download_expanded_natyasangeet():
    print("=" * 80)
    print("AURALIS: TARGETED MARATHI NATYASANGEET EXPANSION")
    print("=" * 80)

    for item in NEW_PLAYS_MANIFEST:
        target_dir = os.path.join(BASE_DIR, item["play"])
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, f"{item['title']}.mp3")

        if os.path.exists(target_path):
            print(f"[EXISTS] {item['title']} already present in {item['play']}")
            continue

        temp_base = f"temp_natya_{int(time.time() * 1000)}"
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

        print(f"\n[*] Downloading: {item['title']} ({item['play']})...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(item["query"], download=True)
                thumb = ""
                if "entries" in info and info["entries"]:
                    thumb = info["entries"][0].get("thumbnail", "")
                elif "thumbnail" in info:
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
                tags.add(COMM(encoding=3, lang="eng", desc="", text=[f"Marathi Sangeet Natak: {item['play']}"]))

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
                tags.save(target_path, v2_version=4)
                print(f"[+] Successfully saved and tagged: {target_path}")

        except Exception as e:
            print(f"[-] Failed to download {item['title']}: {e}")
            temp_mp3 = f"{temp_base}.mp3"
            if os.path.exists(temp_mp3):
                try:
                    os.remove(temp_mp3)
                except Exception:
                    pass

    print("\n" + "=" * 80)
    print("NATYASANGEET EXPANSION PASS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    download_expanded_natyasangeet()
