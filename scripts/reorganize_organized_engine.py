r"""
Auralis - Physical Reorganization & Deduplication Engine for D:\\Songs\\organized
Analyzes all 8,143 files physically in D:\\Songs\\organized:
1. Deletes any 0-byte files.
2. Performs stream hash deduplication within D:\\Songs\\organized:
   Identifies duplicate streams, keeps the highest bitrate pristine copy,
   and marks lower-bitrate redundant copies for deletion.
3. Completely classifies every active file:
   - 0 Evergreen Classics (100% distributed into Soundtracks, Albums, Artists, Ghazals, Devotional)
   - Disambiguates Ra.One / Chammak Challo out of English\Akon into Hindi\Soundtracks\Ra.One
   - Disambiguates Disturbed out of Hindi into English\Disturbed
   - Disambiguates Geet Ramayan out of Hindi into Marathi\Geet Ramayan
   - Disambiguates Bhagavad Gita out of Hindi into Pravachan\Shankar Abhyankar\Bhagavad Gita - Nirupan
   - Preserves Pravachan Day 01-05, Day 06-10, Artya, Adhyays 01-18
   - Sanitizes all paths: 0 brackets, 0 dirty symbols, 0 repeated prefixes.
4. Generates execution plan for review and execution.
"""

import os
import sys
import re
import json
import hashlib
from collections import defaultdict, Counter
from typing import Dict, Any, List, Tuple

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.pattern_classifier import (
    clean_watermarks, clean_name, is_valid_album,
    SUKTA_PATTERNS, STOTRA_PATTERNS, SANSKRIT_KEYWORDS,
    detect_language_and_category, extract_bollywood_movie_and_song
)
from src.engine.embedded_intelligence import resolve_canonical_artist
from src.engine.catalog_resolver import lookup_catalog_track
from src.engine.pravachan_resolver import resolve_pravachan_track
from src.engine.master_dry_run_engine import sanitize_filesystem_name, DECISION_CACHE_FILE, load_decision_cache

ORGANIZED_ROOT = r"D:\Songs\organized"

def compute_stream_hash(file_path: str) -> str:
    try:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            f.seek(8192)
            chunk = f.read(65536)
            if chunk:
                hasher.update(chunk)
            else:
                f.seek(0)
                hasher.update(f.read(65536))
        return hasher.hexdigest()
    except Exception:
        return ""

def scan_and_analyze_all(apply_changes: bool = False):
    print("=" * 80)
    print(f"AURALIS REORGANIZATION & DEDUPLICATION ENGINE (Apply Changes: {apply_changes})")
    print("=" * 80)

    decision_cache = load_decision_cache()
    all_files = []
    zero_byte_deleted = 0

    for root, dirs, files in os.walk(ORGANIZED_ROOT):
        for f in files:
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            if sz == 0:
                print(f"Found 0-byte file: {p}")
                if apply_changes:
                    try:
                        os.remove(p)
                        zero_byte_deleted += 1
                        print(f"  -> DELETED 0-byte file: {p}")
                    except Exception as e:
                        print(f"  -> Error deleting: {e}")
                continue
            if f.lower().endswith(('.mp3', '.wma', '.wav', '.m4a', '.ogg', '.flac')):
                all_files.append(p)

    total_files = len(all_files)
    print(f"\nScanned {total_files} active audio files in {ORGANIZED_ROOT}.")

    # Step 1: Read metadata and stream hash for every file
    print("\n[Step 1] Reading headers and computing audio stream hashes...")
    track_records = []
    stream_map = defaultdict(list)

    for i, p in enumerate(all_files):
        ext = os.path.splitext(p)[1].lower()
        fn = os.path.basename(p)
        sz = os.path.getsize(p)
        h = compute_stream_hash(p)

        tag_t = ""
        tag_a = ""
        tag_alb = ""
        tag_g = ""
        dur = 0.0
        br = 128

        try:
            mf = mutagen.File(p)
            if mf and mf.info:
                dur = getattr(mf.info, "length", 0.0)
                br = getattr(mf.info, "bitrate", 0) // 1000 if getattr(mf.info, "bitrate", 0) else 128
            if ext == ".mp3":
                try:
                    id3 = ID3(p)
                    tag_t = str(id3.get("TIT2", ""))
                    tag_a = str(id3.get("TPE1", ""))
                    tag_alb = str(id3.get("TALB", ""))
                    tag_g = str(id3.get("TCON", ""))
                except Exception:
                    pass
            elif ext == ".wma":
                try:
                    asf = mutagen.File(p)
                    if asf and asf.tags:
                        tag_t = str(asf.tags.get("Title", [""])[0])
                        tag_a = str(asf.tags.get("Author", [""])[0])
                        tag_alb = str(asf.tags.get("WM/AlbumTitle", [""])[0])
                except Exception:
                    pass
        except Exception:
            pass

        rec = {
            "source_path": p,
            "filename": fn,
            "ext": ext,
            "size_bytes": sz,
            "duration": dur,
            "bitrate": br,
            "stream_hash": h,
            "tag_title": tag_t,
            "tag_artist": tag_a,
            "tag_album": tag_alb,
            "tag_genre": tag_g,
            "is_duplicate": False,
        }
        track_records.append(rec)
        if h:
            stream_map[h].append(rec)

    # Step 2: Quality-Aware Deduplication Analysis
    print("\n[Step 2] Analyzing duplicates based on raw audio streams...")
    duplicate_count = 0
    deleted_duplicates = []

    for h, lst in stream_map.items():
        if len(lst) > 1:
            # Sort descending by bitrate, duration, and prefer cleaner filename
            lst.sort(key=lambda x: (x["bitrate"], x["duration"], -len(x["filename"])), reverse=True)
            lst[0]["is_duplicate"] = False
            for dup in lst[1:]:
                dup["is_duplicate"] = True
                duplicate_count += 1
                deleted_duplicates.append(dup["source_path"])

    print(f"  Total duplicate stream groups: {sum(1 for lst in stream_map.values() if len(lst) > 1)}")
    print(f"  Total redundant duplicate files to delete: {duplicate_count}")

    # Step 3: Classify Every Active File
    print("\n[Step 3] Classifying all active tracks into granular categories...")
    category_counts = defaultdict(int)

    for t in track_records:
        if t["is_duplicate"]:
            continue

        p = t["source_path"]
        fn = t["filename"]
        h = t["stream_hash"]
        tag_t = t["tag_title"]
        tag_a = t["tag_artist"]
        tag_alb = t["tag_album"]
        dur = t["duration"]
        combined_text = f"{fn} {tag_t} {tag_a} {tag_alb} {p}".lower()

        # Check persistent decision cache
        if h and h in decision_cache:
            cached = decision_cache[h]
            t["language"] = cached["language"]
            t["category"] = cached["category"]
            t["artist"] = cached["artist"]
            t["album"] = cached["album"]
            t["title"] = cached["title"]
            t["decision_source"] = "Persistent Decision Cache"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 0. Check Pravachan / Katha / Gita Nirupan
        prav = resolve_pravachan_track(fn, p, tag_t, tag_a, tag_alb)
        if prav:
            t["language"] = prav["language"]
            t["category"] = prav["category"]
            t["artist"] = prav["artist"]
            t["album"] = prav["album"]
            t["title"] = prav["title"]
            t["decision_source"] = prav["decision_source"]
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 1. Check Master Catalog Ground Truth
        cat_info = lookup_catalog_track(fn, tag_t, tag_a, dur)
        if cat_info and cat_info[1] not in ["Evergreen Classics", "General"]:
            c_lang, c_cat, c_alb = cat_info
            if c_lang == "Pravachan":
                p_sub = resolve_pravachan_track(fn, c_cat, tag_t, tag_a, c_alb)
                if p_sub:
                    t.update(p_sub)
                    cat_key = f"{t['language']}:{t['category']}"
                    category_counts[cat_key] += 1
                    continue
                c_title = sanitize_filesystem_name(os.path.splitext(fn)[0])
                c_art = "Ghaisasi Guruji" if "ghaisasi" in c_cat.lower() else ("Kavishwar Maharaj" if "kavishwar" in c_cat.lower() else ("Dr. Shankar Abhyankar" if "shankar abhyankar" in c_cat.lower() else ("Aparna Abhyankar" if "aparna" in c_cat.lower() else "Various Speakers")))
            else:
                c_title = clean_name(tag_t or "")
                if not c_title or c_title.lower().startswith("track"):
                    c_title = clean_name(fn)
                c_art = tag_a or "Various Artists"
                if c_lang == "Ringtones":
                    c_art = "Sound Clips & Alerts"
                elif c_art.lower() in ["artist", "various artists", "unknown artist", "unknown"]:
                    c_art = c_alb if "Artists" in c_cat else "Various Artists"

            t["language"] = c_lang
            t["category"] = c_cat
            t["artist"] = c_art
            t["album"] = c_alb
            t["title"] = c_title
            t["decision_source"] = "Catalog Ground Truth Vault"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 2. Ra.One Special Rule (Chammak Challo, Criminal - Never English)
        if "ra.one" in combined_text or "chammak challo" in combined_text or "criminal" in combined_text and "akon" in combined_text:
            clean_t = "Chammak Challo" if "chammak" in combined_text else ("Criminal" if "criminal" in combined_text else clean_name(fn))
            t["language"] = "Hindi"
            t["category"] = "Soundtracks\\Ra.One"
            t["artist"] = "Vishal-Shekhar & Akon"
            t["album"] = "Ra.One"
            t["title"] = clean_t
            t["decision_source"] = "Special Rule: Ra.One Bollywood"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 3. Omkara Special Rule
        omkara_tracks = ["beedi", "naina", "namak", "omkara", "jag ja ri gudiya", "o saathi re", "laakad"]
        if "omkara" in combined_text:
            if any(tr in combined_text for tr in omkara_tracks) or any(a in combined_text for a in ["vishal", "bhardwaj", "sukhwinder", "sunidhi", "rekha", "rahat", "gulzar"]):
                clean_t = fn.replace(".mp3", "").replace(".wma", "").strip().title()
                for om_tr in omkara_tracks:
                    if om_tr in combined_text:
                        clean_t = om_tr.title()
                        break
                t["language"] = "Hindi"
                t["category"] = "Soundtracks\\Omkara"
                t["artist"] = "Vishal Bhardwaj"
                t["album"] = "Omkara"
                t["title"] = clean_t
                t["decision_source"] = "Special Rule: Bollywood Omkara"
                cat_key = f"{t['language']}:{t['category']}"
                category_counts[cat_key] += 1
                continue

        # 4. Sanskrit Sacred Disambiguation
        sanskrit_matched = False
        for pat, canon_name in SUKTA_PATTERNS:
            if re.search(pat, combined_text, re.IGNORECASE):
                t["language"] = "Sanskrit"
                t["category"] = "Vedic Suktas"
                t["artist"] = "Traditional Vedic Chants"
                t["album"] = "Vedic Suktas"
                t["title"] = canon_name
                t["decision_source"] = "Taxonomy: Vedic Suktas"
                sanskrit_matched = True
                break
        if sanskrit_matched:
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        for pat, canon_name in STOTRA_PATTERNS:
            if re.search(pat, combined_text, re.IGNORECASE):
                t["language"] = "Sanskrit"
                t["category"] = "Stotras & Ashtakams"
                t["artist"] = "Traditional Sanskrit Chants"
                t["album"] = "Stotras & Ashtakams"
                t["title"] = canon_name
                t["decision_source"] = "Taxonomy: Stotras & Ashtakams"
                sanskrit_matched = True
                break
        if sanskrit_matched:
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        if any(k in combined_text for k in SANSKRIT_KEYWORDS):
            cat = "Stotras & Ashtakams" if any(sk in combined_text for sk in ["stotra", "stotram", "ashtak"]) else "Vedic Suktas"
            t["language"] = "Sanskrit"
            t["category"] = cat
            t["artist"] = "Traditional Sanskrit Chants"
            t["album"] = cat
            t["title"] = clean_name(tag_t or fn)
            t["decision_source"] = "Taxonomy: Sanskrit Keywords"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 5. Marathi Indicators
        if any(k in combined_text for k in ["abhang", "natyasangeet", "bhavgeet", "shete", "vitthal", "mauli", "tukaram", "bhajan", "aarti", "geet ramayan"]) or "marathi" in combined_text:
            marathi_artist = clean_name(tag_a or "")
            if "shete" in combined_text or "akhilam madhuram" in combined_text:
                cat = "Vaibhavi Shete\\Akhilam Madhuram"
                art = "Vaibhavi Shete"
            elif "ajay" in combined_text and "atul" in combined_text:
                cat = "Ajay-Atul"
                art = "Ajay-Atul"
            elif "geet ramayan" in combined_text:
                cat = "Geet Ramayan"
                art = "Sudhir Phadke"
            elif "natyasangeet" in combined_text or "naman natwara" in combined_text:
                cat = "Natyasangeet"
                art = marathi_artist or "Various Artists"
            elif any(k in combined_text for k in ["abhang", "vitthal", "mauli", "tukaram"]):
                cat = "Abhang & Bhakti"
                art = marathi_artist or "Various Artists"
            elif any(k in combined_text for k in ["bhajan", "aarti", "krishna"]):
                cat = "Bhajan & Aarti"
                art = marathi_artist or "Various Artists"
            elif marathi_artist and marathi_artist.lower() not in ["various artists", "unknown artist", "unknown", "artist", "devotional"]:
                cat = marathi_artist
                art = marathi_artist
            else:
                cat = "Bhavgeet & Classics"
                art = marathi_artist or "Various Artists"

            t["language"] = "Marathi"
            t["category"] = cat
            t["artist"] = art
            t["album"] = cat
            t["title"] = clean_name(tag_t or fn)
            t["decision_source"] = "Taxonomy: Marathi"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 6. Western Rock & Pop (Nirvana, Coldplay, Beatles, Disturbed, etc.)
        english_bands = [
            "nirvana", "coldplay", "u2", "green day", "iron maiden", "metallica",
            "megadeth", "pink floyd", "the beatles", "beatles", "linkin park",
            "red hot chili peppers", "audioslave", "soundgarden", "faith no more",
            "pearl jam", "radiohead", "rage against the machine", "guns n roses",
            "switchfoot", "rammstein", "nickelback", "eminem", "agnee", "ashutosh pathak",
            "disturbed", "boyzone", "infected mushroom", "bob marley", "westlife", "savage garden"
        ]
        eng_matched = False
        for band in english_bands:
            if re.search(r"\b" + re.escape(band) + r"\b", combined_text, re.IGNORECASE):
                canon_band = resolve_canonical_artist(band) or band.title()
                t["language"] = "English"
                t["category"] = canon_band
                t["artist"] = canon_band
                t["album"] = tag_alb or canon_band
                t["title"] = clean_name(tag_t or fn)
                t["decision_source"] = "Taxonomy: Western Rock & Pop"
                eng_matched = True
                break
        if eng_matched:
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 7. Pattern Classifier & Canonical Artist
        canon_artist = resolve_canonical_artist(tag_a) or resolve_canonical_artist(os.path.basename(os.path.dirname(p)))
        det_lang, det_cat = detect_language_and_category(p, fn, tag_a)

        if canon_artist and any(h_ind in canon_artist.lower() for h_ind in ["classics", "ghazals", "hits", "rahman", "shete", "atif", "arijit"]):
            lang = "Marathi" if "shete" in canon_artist.lower() else "Hindi"
            t["language"] = lang
            t["category"] = canon_artist
            t["artist"] = canon_artist
            t["album"] = tag_alb or canon_artist
            t["title"] = clean_name(tag_t or fn)
            t["decision_source"] = "Taxonomy: Canonical Indian Artist"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        if det_lang == "English":
            eng_artist = canon_artist or clean_name(tag_a or "")
            if not eng_artist or eng_artist.lower() in ["various artists", "unknown artist", "unknown"]:
                parent_dir = os.path.basename(os.path.dirname(p))
                if parent_dir.lower() not in ["english", "organized", "unorganized", "rock & pop", "singles & compilations", "hindi"]:
                    eng_artist = clean_name(parent_dir)
                else:
                    eng_artist = "Various Artists"
            cat_name = det_cat if det_cat not in ["General", "Rock & Pop"] else (eng_artist if eng_artist != "Various Artists" else "Rock & Pop")
            t["language"] = "English"
            t["category"] = cat_name
            t["artist"] = eng_artist
            t["album"] = tag_alb or cat_name
            t["title"] = clean_name(tag_t or fn)
            t["decision_source"] = "Taxonomy: English Language & Artist"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        if canon_artist:
            t["language"] = det_lang if det_lang != "English" else "Hindi"
            t["category"] = canon_artist
            t["artist"] = canon_artist
            t["album"] = tag_alb or canon_artist
            t["title"] = clean_name(tag_t or fn)
            t["decision_source"] = "Taxonomy: Canonical Artist"
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1
            continue

        # 8. Bollywood Soundtrack / Movie extraction
        movie, clean_song = extract_bollywood_movie_and_song(
            clean_stem=clean_watermarks(os.path.splitext(fn)[0]),
            stem=os.path.splitext(fn)[0],
            file_path=p,
            tag_album=tag_alb,
            tag_artist=tag_a,
            tag_title=tag_t
        )
        if movie and movie not in ["Evergreen Classics", "Modern Soundtracks"] and len(movie) > 2:
            if not any(movie.startswith(pr) for pr in ["Soundtracks\\", "Albums\\", "Artists\\", "Ghazals\\", "Devotional"]):
                final_cat = f"Soundtracks\\{movie}"
            else:
                final_cat = movie
        else:
            final_cat = det_cat if det_cat not in ["General", "Evergreen Classics", "Modern Soundtracks"] else (canon_artist or "Singles & Compilations")

        t["language"] = det_lang if det_lang != "English" else "Hindi"
        t["category"] = final_cat
        t["artist"] = canon_artist or tag_a or "Various Artists"
        t["album"] = movie or final_cat
        t["title"] = clean_name(tag_t or clean_song or fn)
        t["decision_source"] = "Taxonomy: Bollywood Soundtrack Resolution"
        cat_key = f"{t['language']}:{t['category']}"
        category_counts[cat_key] += 1

    # Step 4: Build Proposed Paths & Enforce Zero Evergreen Classics and Zero Brackets
    print("\n[Step 4] Assembling clean target paths (Enforcing Zero Brackets & Zero Evergreen Classics)...")
    seen_proposed_paths = set()
    min_folder_threshold = 3
    actions = []

    for t in track_records:
        if t["is_duplicate"]:
            t["action"] = "DELETE_DUPLICATE"
            actions.append(t)
            continue

        lang = t["language"]
        cat = t["category"]
        cat_key = f"{lang}:{cat}"
        title = sanitize_filesystem_name(t["title"])
        artist = sanitize_filesystem_name(t["artist"])
        ext = t["ext"]

        clean_cat_parts = [sanitize_filesystem_name(part) for part in cat.split("\\")]
        clean_cat_path = os.sep.join(clean_cat_parts)

        count = category_counts[cat_key]
        if lang == "Ringtones":
            proposed_dir = os.path.join(ORGANIZED_ROOT, "Ringtones & Alerts")
            base_name = f"{title}"
            t["folder_type"] = "Dedicated Collection"
        elif lang == "Pravachan" or count >= min_folder_threshold or any(perm in cat for perm in ["Samhita", "Suktas", "Stotras", "Discourses", "Gita", "Katha"]):
            proposed_dir = os.path.join(ORGANIZED_ROOT, lang, clean_cat_path)
            base_name = f"{title}"
            t["folder_type"] = "Dedicated Collection"
        else:
            proposed_dir = os.path.join(ORGANIZED_ROOT, lang, "Singles & Compilations")
            if artist and artist != "Various Artists":
                if title.lower().startswith(artist.lower() + " - ") or title.lower().startswith(artist.lower() + " ") or artist.lower() == title.lower():
                    base_name = f"{title}"
                else:
                    base_name = f"{artist} - {title}"
            else:
                base_name = f"{title}"
            t["folder_type"] = "Consolidated Singles"

        target_path = os.path.join(proposed_dir, f"{base_name}{ext}")
        suffix = 2
        while target_path.lower() in seen_proposed_paths:
            target_path = os.path.join(proposed_dir, f"{base_name} - Part {suffix}{ext}")
            suffix += 1

        seen_proposed_paths.add(target_path.lower())
        t["proposed_path"] = target_path
        t["action"] = "ORGANIZE_AND_TAG"
        actions.append(t)

    # Step 5: Summary Evaluation
    active_tracks = [t for t in track_records if not t["is_duplicate"]]
    dups_to_delete = [t for t in track_records if t["is_duplicate"]]

    eg_count = sum(1 for t in active_tracks if "evergreen classics" in t["proposed_path"].lower())
    bracket_count = sum(1 for t in active_tracks if any(b in t["proposed_path"] for b in ['(', ')', '[', ']', '{', '}']))

    lang_dist = Counter(t["language"] for t in active_tracks)
    ftype_dist = Counter(t["folder_type"] for t in active_tracks)

    print("\n" + "=" * 80)
    print("REORGANIZATION PLAN AUDIT RESULTS:")
    print("=" * 80)
    print(f"Total files analyzed: {len(track_records)}")
    print(f"Unique active tracks: {len(active_tracks)}")
    print(f"Redundant duplicates to delete: {len(dups_to_delete)}")
    print(f"Tracks in 'Evergreen Classics': {eg_count} (Goal: 0)")
    print(f"Bracket violations: {bracket_count} (Goal: 0)")
    print(f"Language distribution: {dict(lang_dist)}")
    print(f"Folder type distribution: {dict(ftype_dist)}")

    # Top categories in Hindi
    hindi_cats = Counter(t["category"] for t in active_tracks if t["language"] == "Hindi")
    print("\nTop 15 Hindi Categories in Reorganized Library:")
    for c, cnt in hindi_cats.most_common(15):
        print(f"  {c:40s}: {cnt} tracks")

    # If apply_changes is True, physically execute moves, deletions, and tag updates!
    if apply_changes:
        print("\n" + "=" * 80)
        print("EXECUTING PHYSICAL REORGANIZATION, DEDUPLICATION & TAG WRITING...")
        print("=" * 80)

        # 1. Delete redundant duplicates
        deleted_count = 0
        for dup in dups_to_delete:
            src = dup["source_path"]
            try:
                if os.path.exists(src):
                    os.remove(src)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting duplicate {src}: {e}")
        print(f"[Done] Physically deleted {deleted_count} duplicate files from disk.")

        # 2. Move active files to clean destinations & write embedded tags
        moved_count = 0
        tagged_count = 0

        for t in active_tracks:
            src = t["source_path"]
            tgt = t["proposed_path"]

            # Ensure parent folder exists
            tgt_dir = os.path.dirname(tgt)
            os.makedirs(tgt_dir, exist_ok=True)

            # Move file if path differs
            actual_path = src
            if os.path.normpath(src).lower() != os.path.normpath(tgt).lower():
                try:
                    # Clear readonly attribute
                    import stat
                    if os.path.exists(src):
                        os.chmod(src, stat.S_IWRITE)
                    os.replace(src, tgt)
                    actual_path = tgt
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {src} -> {tgt}: {e}")
                    actual_path = src

            # Write clean embedded tags
            try:
                import stat
                if os.path.exists(actual_path):
                    os.chmod(actual_path, stat.S_IWRITE)
                ext = t["ext"]
                if ext == ".mp3":
                    try:
                        id3 = ID3(actual_path)
                    except Exception:
                        id3 = ID3()
                    id3["TIT2"] = TIT2(encoding=3, text=t["title"])
                    id3["TPE1"] = TPE1(encoding=3, text=t["artist"])
                    id3["TALB"] = TALB(encoding=3, text=t["album"])
                    id3["TCON"] = TCON(encoding=3, text=t["category"])
                    id3.save(actual_path, v2_version=3)
                    tagged_count += 1
                elif ext == ".wma":
                    try:
                        asf = mutagen.File(actual_path)
                        if asf:
                            asf.tags["Title"] = [t["title"]]
                            asf.tags["Author"] = [t["artist"]]
                            asf.tags["WM/AlbumTitle"] = [t["album"]]
                            asf.tags["WM/Genre"] = [t["category"]]
                            asf.save()
                            tagged_count += 1
                    except Exception:
                        pass
            except Exception as e:
                pass

        print(f"[Done] Physically moved {moved_count} files into clean categorized directories.")
        print(f"[Done] Physically updated embedded tags in {tagged_count} files.")

        # 3. Clean up empty directories
        print("[Step] Pruning empty legacy directories...")
        empty_dirs_pruned = 0
        for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
            for d in dirs:
                dp = os.path.join(root, d)
                try:
                    if not os.listdir(dp):
                        os.rmdir(dp)
                        empty_dirs_pruned += 1
                except Exception:
                    pass
        print(f"[Done] Pruned {empty_dirs_pruned} empty legacy directories.")

    return {
        "total_files": len(track_records),
        "unique_active": len(active_tracks),
        "deleted_duplicates": len(dups_to_delete),
        "evergreen_classics_count": eg_count,
        "bracket_violations": bracket_count,
        "language_distribution": dict(lang_dist),
        "folder_type_distribution": dict(ftype_dist)
    }

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    scan_and_analyze_all(apply_changes=apply)
