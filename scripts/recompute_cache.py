import os
import sys
import json
import logging
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_dry_run_engine import MasterDryRunEngine, sanitize_filesystem_name

logging.basicConfig(level=logging.INFO)

def recompute():
    cache_path = "cached_dry_run_results.json"
    if not os.path.exists(cache_path):
        print("Cache not found.")
        return
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tracks = data["tracks"]
    engine = MasterDryRunEngine([], min_folder_threshold=3)

    print(f"Fast recomputing taxonomy for {len(tracks)} tracks (reusing existing transcribed lyrics)...")
    category_counts = defaultdict(int)

    for i, t in enumerate(tracks):
        # Preserve previously transcribed lyrics if present to avoid re-invoking Whisper
        existing_lyrics = t.get("transcribed_lyrics", "")
        # Temporarily set is_generic to False during taxonomy pass so Whisper is not re-invoked
        was_generic = t.get("is_generic", False)
        t["is_generic"] = False

        res = engine.resolve_deep_audio_and_taxonomy(t)
        t["is_generic"] = was_generic

        if existing_lyrics:
            res["transcribed_lyrics"] = existing_lyrics

        t.update(res)

        if not t.get("is_duplicate", False):
            cat_key = f"{t['language']}:{t['category']}"
            category_counts[cat_key] += 1

    seen_proposed_paths = set()
    for t in tracks:
        if t.get("is_duplicate", False):
            dup_stem, dup_ext = os.path.splitext(t['filename'])
            t["proposed_path"] = f"D:\\Songs\\unorganized\\_duplicates_backup\\{sanitize_filesystem_name(dup_stem)}{dup_ext}"
            t["action"] = "Archive Lower-Bitrate Duplicate"
        else:
            lang = t["language"]
            cat = t["category"]
            cat_key = f"{lang}:{cat}"
            title = sanitize_filesystem_name(t["title"])
            artist = sanitize_filesystem_name(t["artist"])
            ext = t["ext"]

            clean_cat_parts = [sanitize_filesystem_name(p) for p in cat.split("\\")]
            clean_cat_path = os.sep.join(clean_cat_parts)

            count = category_counts[cat_key]
            if lang == "Ringtones":
                proposed_dir = os.path.join(r"D:\Songs\organized", "Ringtones & Alerts")
                base_name = f"{title}"
                t["folder_type"] = "Dedicated Collection"
            elif lang == "Pravachan" or count >= engine.min_folder_threshold or any(perm in cat for perm in ["Samhita", "Suktas", "Stotras", "Discourses", "Gita", "Katha"]):
                proposed_dir = os.path.join(r"D:\Songs\organized", lang, clean_cat_path)
                base_name = f"{title}"
                t["folder_type"] = "Dedicated Collection"
            else:
                proposed_dir = os.path.join(r"D:\Songs\organized", lang, "Singles & Compilations")
                if artist and artist != "Various Artists":
                    if title.lower().startswith(artist.lower() + " - ") or title.lower().startswith(artist.lower() + " ") or artist.lower() == title.lower():
                        base_name = f"{title}"
                    else:
                        base_name = f"{artist} - {title}"
                else:
                    base_name = f"{title}"
                t["folder_type"] = "Consolidated Singles"

            target_path = os.path.join(proposed_dir, f"{base_name}{ext}")
            # Ensure unique filename to prevent overwriting different audio versions without brackets
            suffix = 2
            while target_path.lower() in seen_proposed_paths:
                target_path = os.path.join(proposed_dir, f"{base_name} - Part {suffix}{ext}")
                suffix += 1

            seen_proposed_paths.add(target_path.lower())
            t["proposed_path"] = target_path
            t["action"] = "Organize & Tag"

    summary = {
        "total_files_scanned": len(tracks),
        "unique_tracks": sum(1 for t in tracks if not t.get("is_duplicate")),
        "duplicate_tracks": sum(1 for t in tracks if t.get("is_duplicate")),
        "generic_resolved": sum(1 for t in tracks if t.get("is_generic")),
        "languages": defaultdict(int),
        "folder_types": defaultdict(int)
    }
    for t in tracks:
        if not t.get("is_duplicate"):
            summary["languages"][t["language"]] += 1
            summary["folder_types"][t["folder_type"]] += 1

    result = {"summary": summary, "tracks": tracks}
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Recomputation successfully finished!")
    print("Language distribution:", dict(summary["languages"]))
    print("Folder type distribution:", dict(summary["folder_types"]))

if __name__ == "__main__":
    recompute()
