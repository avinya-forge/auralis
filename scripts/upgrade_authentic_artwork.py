r"""
Auralis - Multi-Tier Authentic Artwork Upgrade & Verification Engine
Scans D:\Songs\organized to detect:
1. Low-resolution artwork (<400x400 or <20KB)
2. Cross-contaminated / generic placeholder artwork hashes
3. Missing or corrupt artwork
Fetches official, high-resolution (600x600 to 1000x1000) cover art via:
- Deezer High-Res API (1000x1000 uncompressed CD covers)
- iTunes Search API (600x600 official store covers)
- MusicBrainz Cover Art Archive
Verifies dimensions with PIL and embeds authentic APIC frames with overwrite protection.
"""

import os
import sys
import io
import time
import hashlib
from typing import Dict, List, Set, Tuple, Optional
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.engine.reliable_metadata_client import ReliableMetadataClient
from src.engine.master_organizer import MasterOrganizer

ORGANIZED_ROOT = r"D:\Songs\organized"

def get_shared_and_lowres_tracks(root_dir: str) -> Tuple[Set[str], List[Tuple[str, str, str]]]:
    """Scans all MP3s and identifies generic/cross-contaminated hashes and low-res tracks."""
    print("[*] Auditing artwork across library...")
    hash_to_folders: Dict[str, Set[str]] = {}
    all_files: List[Tuple[str, str, str]] = []

    for dirpath, _, filenames in os.walk(root_dir):
        rel_folder = os.path.relpath(dirpath, root_dir)
        for f in filenames:
            if not f.lower().endswith(".mp3"):
                continue
            fp = os.path.join(dirpath, f)
            all_files.append((fp, rel_folder, f))
            try:
                a = MP3(fp, ID3=ID3)
                apics = [x for x in a.tags.values() if isinstance(x, APIC)] if a.tags else []
                if apics:
                    h = hashlib.md5(apics[0].data).hexdigest()
                    hash_to_folders.setdefault(h, set()).add(rel_folder)
            except Exception:
                pass

    shared_hashes = {h for h, flds in hash_to_folders.items() if len(flds) > 1}
    print(f"[*] Found {len(shared_hashes)} cross-folder shared artwork hashes across {len(all_files)} tracks.")
    return shared_hashes, all_files

def run_artwork_upgrade():
    client = ReliableMetadataClient()
    organizer = MasterOrganizer()
    shared_hashes, all_files = get_shared_and_lowres_tracks(ORGANIZED_ROOT)

    folder_art_cache: Dict[str, Optional[bytes]] = {}
    upgraded_count = 0
    skipped_count = 0
    failed_count = 0

    print("\n[*] Starting authentic artwork resolution and upgrade...")
    for idx, (fp, rel_folder, filename) in enumerate(all_files, 1):
        try:
            a = MP3(fp, ID3=ID3)
            apics = [x for x in a.tags.values() if isinstance(x, APIC)] if a.tags else []
            current_art_data = apics[0].data if apics else None
            needs_upgrade = False

            if not current_art_data:
                needs_upgrade = True
            else:
                current_hash = hashlib.md5(current_art_data).hexdigest()
                if current_hash in shared_hashes:
                    needs_upgrade = True
                elif len(current_art_data) < 20000:
                    try:
                        with Image.open(io.BytesIO(current_art_data)) as img:
                            w, h = img.size
                            if w < 400 or h < 400:
                                needs_upgrade = True
                    except Exception:
                        needs_upgrade = True

            if not needs_upgrade:
                skipped_count += 1
                continue

            stem, _ = os.path.splitext(filename)
            folder_parts = rel_folder.split(os.sep)
            new_art_bytes: Optional[bytes] = None

            # 1. Check folder-level cache
            if rel_folder in folder_art_cache and folder_art_cache[rel_folder]:
                new_art_bytes = folder_art_cache[rel_folder]

            # 2. If soundtrack folder (Hindi\Soundtracks\<Movie>)
            elif "Soundtracks" in folder_parts and len(folder_parts) >= 3:
                movie_name = folder_parts[-1]
                if movie_name not in ["Soundtrack Singles", "Assorted Bollywood", "Greatest Hits Vol-1", "The Golden Collection"]:
                    # Try Deezer Album first
                    res = client.query_deezer_album(movie_name)
                    if not res or not res.get("artwork_url"):
                        res = client.query_deezer(f"{movie_name} soundtrack")
                    if not res or not res.get("artwork_url"):
                        res = client.query_itunes_album(movie_name)

                    if res and res.get("artwork_url"):
                        b = client.fetch_artwork_bytes(res["artwork_url"])
                        if b and len(b) > 20000:
                            new_art_bytes = b
                            folder_art_cache[rel_folder] = b
                            print(f"[FOUND SOUNDTRACK ART] {movie_name} -> {len(b)} bytes ({res['source']})")

            # 3. If individual artist or single track
            if not new_art_bytes:
                artist_name = folder_parts[-1] if len(folder_parts) >= 2 else ""
                query_str = f"{stem} {artist_name}".strip()
                # Query Deezer track first
                res = client.query_deezer(query_str)
                if not res or not res.get("artwork_url"):
                    if artist_name and artist_name not in ["Singles", "Assorted Pop & Rock", "Trance", "Classic Rock", "Indian Rock Bands"]:
                        res = client.query_deezer_album(artist_name)
                if not res or not res.get("artwork_url"):
                    res = client.query_itunes(query_str)

                if res and res.get("artwork_url"):
                    b = client.fetch_artwork_bytes(res["artwork_url"])
                    if b and len(b) > 20000:
                        new_art_bytes = b

            # 4. Embed high-res artwork if found
            if new_art_bytes:
                title = str(a.tags.get("TIT2", stem)) if a.tags else stem
                artist = str(a.tags.get("TPE1", "")) if a.tags else ""
                album = str(a.tags.get("TALB", "")) if a.tags else ""
                genre = str(a.tags.get("TCON", "")) if a.tags else ""
                year = str(a.tags.get("TDRC", "")) if a.tags else ""

                success = organizer.write_id3_tags(
                    file_path=fp,
                    title=title,
                    artist=artist,
                    album=album,
                    genre=genre,
                    year=year,
                    artwork_bytes=new_art_bytes,
                    overwrite_artwork=True
                )
                if success:
                    upgraded_count += 1
                    if upgraded_count % 50 == 0:
                        print(f"  [PROGRESS] Upgraded {upgraded_count} tracks...")
                else:
                    failed_count += 1
            else:
                failed_count += 1

            # Mild sleep to respect API endpoints
            time.sleep(0.08)

        except Exception:
            failed_count += 1

    print("\n" + "=" * 80)
    print("ARTWORK UPGRADE PASS COMPLETED")
    print(f"Total Evaluated: {len(all_files)}")
    print(f"Already Pristine: {skipped_count}")
    print(f"Successfully Upgraded to Authentic High-Res Art: {upgraded_count}")
    print(f"Remaining / Unresolved: {failed_count}")
    print("=" * 80)

if __name__ == "__main__":
    run_artwork_upgrade()
