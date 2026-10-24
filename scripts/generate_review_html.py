import os
import sys
import json
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_dry_run_engine import MasterDryRunEngine

logging.basicConfig(level=logging.INFO)

def main():
    cache_path = "cached_dry_run_results.json"
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tracks = data.get("tracks", [])
    active_tracks = [t for t in tracks if not t.get("is_duplicate", False)]
    dups = [t for t in tracks if t.get("is_duplicate", False)]

    # Compute updated summary
    lang_dist = {}
    folder_type_dist = {"Dedicated Collection": 0, "Consolidated Singles": 0}
    for t in active_tracks:
        l = t.get("language", "Unknown")
        lang_dist[l] = lang_dist.get(l, 0) + 1
        ft = t.get("folder_type", "Dedicated Collection")
        folder_type_dist[ft] = folder_type_dist.get(ft, 0) + 1

    summary = {
        "total_files_scanned": len(tracks),
        "unique_tracks": len(active_tracks),
        "duplicate_tracks": len(dups),
        "generic_resolved": sum(1 for t in tracks if t.get("is_generic", False)),
        "language_distribution": lang_dist,
        "folder_type_distribution": folder_type_dist,
        "high_confidence_matches": sum(1 for t in tracks if t.get("confidence", 0) >= 0.90)
    }

    data["summary"] = summary

    # Save updated data with fresh summary
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    engine = MasterDryRunEngine([])
    html_path = engine.generate_html_review(data, "dry_run_review.html")
    print(f"Generated fresh HTML review dashboard at {html_path} with summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
