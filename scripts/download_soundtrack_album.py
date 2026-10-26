r"""
Auralis - Soundtrack Album Downloader & Enricher.

Downloads canonical Hindi / Bollywood soundtrack albums (e.g. Hum Aapke Hain Koun..!),
converts them to 320kbps MP3 via FFmpeg, extracts and embeds official album artwork,
populates standard ID3v2 tags, and organizes them under:
D:\Songs\organized\Hindi\Soundtracks\<Album Name>\<Song Title>.mp3
"""

import os
import io
import time
import requests
from PIL import Image
import imageio_ffmpeg
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, COMM, APIC, PictureType

BASE_SOUNDTRACKS_DIR = r"D:\Songs\organized\Hindi\Soundtracks"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

HAHK_MANIFEST = [
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Didi Tera Devar Deewana",
        "artist": "Lata Mangeshkar & S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Didi Tera Devar Deewana Hum Aapke Hain Koun Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Pehla Pehla Pyar",
        "artist": "S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Pehla Pehla Pyar S. P. Balasubrahmanyam Hum Aapke Hain Koun Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Mausam Ka Jaadu",
        "artist": "Lata Mangeshkar & S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Mausam Ka Jaadu Hum Aapke Hain Koun Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Joote Do, Paise Lo",
        "artist": "Lata Mangeshkar & S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Joote De Do Paise Lelo Hum Aapke Hain Koun Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Hum Aapke Hain Koun",
        "artist": "Lata Mangeshkar & S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Hum Aapke Hain Koun Title Track Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Wah Wah Ramji",
        "artist": "Lata Mangeshkar & S. P. Balasubrahmanyam",
        "year": "1994",
        "query": "ytsearch1:Wah Wah Ramji Hum Aapke Hain Koun Saregama",
    },
    {
        "album": "Hum Aapke Hain Koun",
        "title": "Maye Ni Maye",
        "artist": "Lata Mangeshkar",
        "year": "1994",
        "query": "ytsearch1:Maye Ni Maye Hum Aapke Hain Koun Saregama",
    },
]


def convert_image_to_jpeg_bytes(img_bytes: bytes) -> bytes:
    """Convert any image byte buffer to clean JPEG bytes."""
    try:
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        out = io.BytesIO()
        image.save(out, format="JPEG", quality=90)
        return out.getvalue()
    except Exception as e:
        print(f"  Warning: Image conversion failed: {e}")
        return b""


def fetch_official_album_artwork(album_name: str) -> bytes:
    """Fetch official high-res album art from iTunes."""
    try:
        url = "https://itunes.apple.com/search"
        params = {"term": album_name, "media": "music", "entity": "album", "limit": 1}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                art_url = results[0].get("artworkUrl100", "").replace("100x100bb", "600x600bb")
                if art_url:
                    img_resp = requests.get(art_url, timeout=10)
                    if img_resp.status_code == 200:
                        return convert_image_to_jpeg_bytes(img_resp.content)
    except Exception as e:
        print(f"  Warning: Album artwork fetch failed: {e}")
    return b""


def tag_soundtrack_file(file_path: str, item: dict, art_bytes: bytes):
    """Embed standard ID3 tags and cover art into the MP3 file."""
    try:
        try:
            tags = ID3(file_path)
        except Exception:
            tags = ID3()

        tags.delall("TIT2")
        tags.delall("TPE1")
        tags.delall("TALB")
        tags.delall("TCON")
        tags.delall("TDRC")
        tags.delall("COMM")
        if art_bytes:
            tags.delall("APIC")

        tags.add(TIT2(encoding=3, text=[item["title"]]))
        tags.add(TPE1(encoding=3, text=[item["artist"]]))
        tags.add(TALB(encoding=3, text=[item["album"]]))
        tags.add(TCON(encoding=3, text=["Bollywood / Soundtrack"]))
        if "year" in item:
            tags.add(TDRC(encoding=3, text=[item["year"]]))
        comment = f"Soundtrack: {item['album']} | Music Director: Raamlaxman"
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

        tags.save(file_path)
        print(f"  Tags & Artwork written to: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  Error tagging {file_path}: {e}")


def cleanup_temp_files(prefix: str):
    """Remove temporary files matching the prefix."""
    for f in os.listdir("."):
        if f.startswith(prefix):
            try:
                os.remove(f)
            except Exception:
                pass


def download_soundtrack_track(item: dict, art_bytes: bytes) -> bool:
    """Download a single soundtrack track using yt-dlp."""
    target_dir = os.path.join(BASE_SOUNDTRACKS_DIR, item["album"])
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, f"{item['title']}.mp3")

    if os.path.exists(target_path):
        print(f"[SKIP] Already exists: {target_path}")
        return True

    temp_base = f"temp_stk_{int(time.time() * 1000)}"
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

    print(f"\n[DOWNLOAD] Searching: {item['query']}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([item["query"]])

        temp_mp3 = f"{temp_base}.mp3"
        if not os.path.exists(temp_mp3):
            print(f"  Error: {temp_mp3} not found after download.")
            return False

        if os.path.exists(target_path):
            os.remove(target_path)
        os.rename(temp_mp3, target_path)

        tag_soundtrack_file(target_path, item, art_bytes)
        print(f"  Successfully organized: {target_path}")
        return True
    except Exception as e:
        print(f"  Download error for {item['title']}: {e}")
        cleanup_temp_files(temp_base)
        return False


def main():
    print("=" * 60)
    print("AURALIS: SOUNDTRACK ALBUM ACQUISITION & ENRICHMENT")
    print("=" * 60)

    art_bytes = fetch_official_album_artwork("Hum Aapke Hain Koun")
    print(f"Fetched album artwork: {len(art_bytes)} bytes")

    success_count = 0
    for idx, item in enumerate(HAHK_MANIFEST, 1):
        print(f"\n[{idx}/{len(HAHK_MANIFEST)}] {item['album']} - {item['title']}")
        if download_soundtrack_track(item, art_bytes):
            success_count += 1
        time.sleep(1)

    print("\n" + "=" * 60)
    print(f"SOUNDTRACK COMPLETE: {success_count}/{len(HAHK_MANIFEST)} processed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
