r"""
Auralis - Systematic Rare Marathi Natyasangeet Downloader & Library Enricher.

Downloads rare, iconic Marathi Natyasangeet masterworks using yt-dlp, converts them
to 320kbps MP3 via FFmpeg, extracts and embeds high-resolution cover artwork,
populates standard ID3v2 tags (TIT2, TPE1, TALB, TCON, COMM, APIC),
and organizes them into canonical play/album folders under D:\Songs\organized\Marathi\Natyasangeet\.
"""

import os
import io
import time
import requests
from PIL import Image
import imageio_ffmpeg
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, COMM, APIC, PictureType

BASE_DIR = r"D:\Songs\organized\Marathi\Natyasangeet"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Curated Manifest of iconic, rare Marathi Natyasangeet
NATYASANGEET_MANIFEST = [
    # 1. Katyar Kaljat Ghusali
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Ghei Chhand Makarand",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Ghei Chhand Makarand Vasantrao Deshpande Katyar Kaljat Ghusali Saregama",
    },
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Sur Niragas Ho",
        "artist": "Shankar Mahadevan & Anandi Joshi",
        "composer": "Pt. Jitendra Abhisheki / Shankar-Ehsaan-Loy",
        "query": "ytsearch1:Sur Niragas Ho Shankar Mahadevan Katyar Kaljat Ghusli Zee Music",
    },
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Lagi Kalejwa Kator",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Lagi Kalejwa Kator Vasantrao Deshpande Katyar Kaljat Ghusali",
    },
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Ya Bhawanatil Geet Purane",
        "artist": "Pt. Jitendra Abhisheki",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Ya Bhawanatil Geet Purane Jitendra Abhisheki Katyar Kaljat Ghusali",
    },
    {
        "play": "Katyar Kaljat Ghusali",
        "title": "Tejonidhi Lohagol",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Tejonidhi Lohagol Vasantrao Deshpande Saregama",
    },

    # 2. Sangeet Saubhadra
    {
        "play": "Sangeet Saubhadra",
        "title": "Priyakar Vinu Nari",
        "artist": "Balgandharva",
        "composer": "Annasaheb Kirloskar",
        "query": "ytsearch1:Priyakar Vinu Nari Balgandharva Sangeet Saubhadra Saregama",
    },
    {
        "play": "Sangeet Saubhadra",
        "title": "Pandu Nrupati Janak Jaya",
        "artist": "Malini Rajurkar",
        "composer": "Annasaheb Kirloskar",
        "query": "ytsearch1:Pandu Nrupati Janak Jaya Malini Rajurkar Saregama",
    },
    {
        "play": "Sangeet Saubhadra",
        "title": "Nahi Mi Bolat Nath",
        "artist": "Balgandharva",
        "composer": "Annasaheb Kirloskar",
        "query": "ytsearch1:Nahi Mi Bolat Nath Balgandharva Sangeet Saubhadra",
    },

    # 3. Sangeet Manapman
    {
        "play": "Sangeet Manapman",
        "title": "Chandrika Hi Janu",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Chandrika Hi Janu Vasantrao Deshpande Manapman Saregama",
    },
    {
        "play": "Sangeet Manapman",
        "title": "Bhalachandra Bhal Shobhe",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Bhalachandra Bhal Shobhe Vasantrao Deshpande Manapman Saregama",
    },
    {
        "play": "Sangeet Manapman",
        "title": "Khara To Prema",
        "artist": "Balgandharva",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Khara To Prema Balgandharva Manapman Saregama",
    },
    {
        "play": "Sangeet Manapman",
        "title": "Shura Mi Vandile",
        "artist": "Balgandharva",
        "composer": "Govindrao Tembe",
        "query": "ytsearch1:Shura Mi Vandile Balgandharva Manapman Saregama",
    },

    # 4. Sangeet Swayamvar
    {
        "play": "Sangeet Swayamvar",
        "title": "Swakul Tarak Suta",
        "artist": "Pt. Kumar Gandharva",
        "composer": "Pt. Bhaskarbuwa Bakhale",
        "query": "ytsearch1:Swakul Tarak Suta Kumar Gandharva Swayamvar Saregama",
    },
    {
        "play": "Sangeet Swayamvar",
        "title": "Nrupakanya Hi Chintit Mani Ka",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Pt. Bhaskarbuwa Bakhale",
        "query": "ytsearch1:Nrupakanya Hi Chintit Mani Ka Vasantrao Deshpande Swayamvar",
    },
    {
        "play": "Sangeet Swayamvar",
        "title": "Mama Aatma Gamala",
        "artist": "Balgandharva",
        "composer": "Pt. Bhaskarbuwa Bakhale",
        "query": "ytsearch1:Mama Aatma Gamala Balgandharva Swayamvar Saregama",
    },

    # 5. Sangeet Ekach Pyala
    {
        "play": "Sangeet Ekach Pyala",
        "title": "Kashi Ya Tyaju Padala",
        "artist": "Balgandharva",
        "composer": "Ram Ganesh Gadkari",
        "query": "ytsearch1:Kashi Ya Tyaju Padala Balgandharva Ekach Pyala Saregama",
    },
    {
        "play": "Sangeet Ekach Pyala",
        "title": "Mata Pitru Charani",
        "artist": "Ramdas Kamat",
        "composer": "Ram Ganesh Gadkari",
        "query": "ytsearch1:Mata Pitru Charani Ramdas Kamat Ekach Pyala Saregama",
    },
    {
        "play": "Sangeet Ekach Pyala",
        "title": "Sukada Ghorati Ghor",
        "artist": "Balgandharva",
        "composer": "Ram Ganesh Gadkari",
        "query": "ytsearch1:Sukada Ghorati Ghor Balgandharva Ekach Pyala",
    },

    # 6. Sangeet Matsyagandha
    {
        "play": "Sangeet Matsyagandha",
        "title": "Gartha Andhari Lajat Gau Kashi",
        "artist": "Ramdas Kamat",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Gartha Andhari Lajat Gau Kashi Ramdas Kamat Matsyagandha Saregama",
    },
    {
        "play": "Sangeet Matsyagandha",
        "title": "Sadha Bhole Prema Majhe",
        "artist": "Ramdas Kamat",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Sadha Bhole Prema Majhe Ramdas Kamat Matsyagandha Saregama",
    },
    {
        "play": "Sangeet Matsyagandha",
        "title": "Naka Todoo Re Gal",
        "artist": "Ramdas Kamat",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Naka Todoo Re Gal Matsyagandha Ramdas Kamat",
    },

    # 7. Sangeet Sanshaykallol
    {
        "play": "Sangeet Sanshaykallol",
        "title": "Dharila Pandharicha Chor",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Govind Ballal Deval",
        "query": "ytsearch1:Dharila Pandharicha Chor Vasantrao Deshpande Sanshaykallol Saregama",
    },
    {
        "play": "Sangeet Sanshaykallol",
        "title": "Ha Naad Sod Mana",
        "artist": "Ramdas Kamat",
        "composer": "Govind Ballal Deval",
        "query": "ytsearch1:Ha Naad Sod Mana Sanshaykallol Ramdas Kamat",
    },

    # 8. Sangeet Sharada
    {
        "play": "Sangeet Sharada",
        "title": "Mhatara Deepika Teja",
        "artist": "Balgandharva",
        "composer": "Govind Ballal Deval",
        "query": "ytsearch1:Mhatara Deepika Teja Balgandharva Sharada Saregama",
    },
    {
        "play": "Sangeet Sharada",
        "title": "Murti Manta Bhiti Ubhi",
        "artist": "Chhota Gandharva",
        "composer": "Govind Ballal Deval",
        "query": "ytsearch1:Murti Manta Bhiti Ubhi Chhota Gandharva Sharada",
    },

    # 9. Sangeet Shakuntal
    {
        "play": "Sangeet Shakuntal",
        "title": "Pari Mam Chitta Nale",
        "artist": "Balgandharva",
        "composer": "Annasaheb Kirloskar",
        "query": "ytsearch1:Pari Mam Chitta Nale Balgandharva Shakuntal Saregama",
    },

    # 10. Evergreen Natyageete
    {
        "play": "Evergreen Natyageete",
        "title": "Runanubandhachya Jithun Padlya Gathi",
        "artist": "Pt. Kumar Gandharva",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Runanubandhachya Kumar Gandharva Saregama",
    },
    {
        "play": "Evergreen Natyageete",
        "title": "Kaivalyachya Chandanyala",
        "artist": "Pt. Jitendra Abhisheki",
        "composer": "Pt. Jitendra Abhisheki",
        "query": "ytsearch1:Kaivalyachya Chandanyala Jitendra Abhisheki Saregama",
    },
    {
        "play": "Evergreen Natyageete",
        "title": "Uthi Uthi Gopala",
        "artist": "Pt. Kumar Gandharva",
        "composer": "Pt. Kumar Gandharva",
        "query": "ytsearch1:Uthi Uthi Gopala Kumar Gandharva Saregama",
    },
    {
        "play": "Evergreen Natyageete",
        "title": "Natha Ghari Nache Majha Sakha Pandurang",
        "artist": "Pt. Vasantrao Deshpande",
        "composer": "Pt. Vasantrao Deshpande",
        "query": "ytsearch1:Natha Ghari Nache Vasantrao Deshpande Saregama",
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


def fetch_artwork(thumbnail_url: str) -> bytes:
    """Fetch and return high quality JPEG bytes for cover art."""
    if not thumbnail_url:
        return b""
    try:
        resp = requests.get(thumbnail_url, timeout=12)
        if resp.status_code == 200:
            return convert_image_to_jpeg_bytes(resp.content)
    except Exception as e:
        print(f"  Warning: Artwork fetch failed: {e}")
    return b""


def tag_audio_file(file_path: str, item: dict, art_bytes: bytes):
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
        tags.delall("COMM")
        if art_bytes:
            tags.delall("APIC")

        tags.add(TIT2(encoding=3, text=[item["title"]]))
        tags.add(TPE1(encoding=3, text=[item["artist"]]))
        tags.add(TALB(encoding=3, text=[item["play"]]))
        tags.add(TCON(encoding=3, text=["Natyasangeet"]))
        comment = f"Marathi Sangeet Natak: {item['play']} | Composer: {item.get('composer', 'Traditional')}"
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
        print(f"  Tags & Artwork successfully written to: {os.path.basename(file_path)}")
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


def download_track(item: dict) -> bool:
    """Download a single track using yt-dlp, convert, tag and place in target folder."""
    target_dir = os.path.join(BASE_DIR, item["play"])
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, f"{item['title']}.mp3")

    if os.path.exists(target_path):
        print(f"[SKIP] Already exists: {target_path}")
        return True

    temp_base = f"temp_dl_{int(time.time() * 1000)}"
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
            info = ydl.extract_info(item["query"], download=True)
            entries = info.get("entries")
            thumb_url = entries[0].get("thumbnail", "") if entries else info.get("thumbnail", "")

        temp_mp3 = f"{temp_base}.mp3"
        if not os.path.exists(temp_mp3):
            print(f"  Error: {temp_mp3} not found after download.")
            return False

        art_bytes = fetch_artwork(thumb_url)
        if os.path.exists(target_path):
            os.remove(target_path)
        os.rename(temp_mp3, target_path)

        tag_audio_file(target_path, item, art_bytes)
        print(f"  Successfully organized: {target_path}")
        return True
    except Exception as e:
        print(f"  Download error for {item['title']}: {e}")
        cleanup_temp_files(temp_base)
        return False


def reorganize_existing_loose_natyasangeet():
    """Reorganize existing loose files in Marathi\\Natyasangeet into play folders."""
    mapping = {
        # Sangeet Saubhadra
        "Radhadhar Madhu Milind.mp3": "Sangeet Saubhadra",
        "Balam Na Mora.mp3": "Sangeet Saubhadra",
        # Sangeet Manapman
        "Ravi Mee Ha Chandra.mp3": "Sangeet Manapman",
        "Ravi Mee Ha Chandra - Vol 2.mp3": "Sangeet Manapman",
        "Mana Manav Wa Parmeshwar.mp3": "Sangeet Manapman",
        "Yuvati Mana Dharuni.mp3": "Sangeet Manapman",
        # Sangeet Sanshaykallol
        "Mrunal Kanti Roop Manasi.mp3": "Sangeet Sanshaykallol",
        "Sujan Kasa Man Chori.mp3": "Sangeet Sanshaykallol",
        # Sangeet Swayamvar
        "Narwar Krushnasamaan.mp3": "Sangeet Swayamvar",
        "Narwar Krushnasamaan - Vol 2.mp3": "Sangeet Swayamvar",
        # Sangeet Shakuntal
        "Naman Natwara.mp3": "Sangeet Shakuntal",
        "Naman Natwara - Vol 2.mp3": "Sangeet Shakuntal",
        # Katyar Kaljat Ghusali
        "Surat Piya Ki Na Chhinn.mp3": "Katyar Kaljat Ghusali",
        # Evergreen Natyageete
        "Kanhoji Anand Zala.mp3": "Evergreen Natyageete",
        "Kathin Kathin Maaza.mp3": "Evergreen Natyageete",
        "Paravashyata Paash Daive.mp3": "Evergreen Natyageete",
        "Rupavali.mp3": "Evergreen Natyageete",
        "Vithu Majha Lekurwala.mp3": "Evergreen Natyageete",
    }

    print("\n--- Reorganizing Existing Loose Natyasangeet Files ---")
    for fname, play in mapping.items():
        src = os.path.join(BASE_DIR, fname)
        if os.path.exists(src):
            dest_dir = os.path.join(BASE_DIR, play)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, fname)
            os.rename(src, dest)
            print(f"Moved: {fname} -> {play}\\")

            # Update album tag
            try:
                t = ID3(dest)
                t["TALB"] = TALB(encoding=3, text=[play])
                t["TCON"] = TCON(encoding=3, text=["Natyasangeet"])
                t.save()
            except Exception:
                pass


def main():
    print("=" * 60)
    print("AURALIS: RARE MARATHI NATYASANGEET ACQUISITION & ENRICHMENT")
    print("=" * 60)

    # Step 1: Reorganize existing loose files first
    reorganize_existing_loose_natyasangeet()

    # Step 2: Download rare tracks
    print(f"\nProcessing {len(NATYASANGEET_MANIFEST)} curated Natyasangeet tracks...")
    success_count = 0
    for idx, item in enumerate(NATYASANGEET_MANIFEST, 1):
        print(f"\n[{idx}/{len(NATYASANGEET_MANIFEST)}] {item['play']} - {item['title']} ({item['artist']})")
        if download_track(item):
            success_count += 1
        time.sleep(1)  # Polite pacing

    print("\n" + "=" * 60)
    print(f"ACQUISITION COMPLETE: {success_count}/{len(NATYASANGEET_MANIFEST)} processed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
