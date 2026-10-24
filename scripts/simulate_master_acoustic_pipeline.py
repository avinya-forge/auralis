"""
Simulate Master Acoustic Pipeline
Tests language routing, acoustic deduplication, zero brackets, and granular sub-sorting.
"""

import os
import sys
import re
import sqlite3
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.path_sanitizer import sanitize_filename, sanitize_path_component, sanitize_relative_path
from src.engine.acoustic_language_sorter import CULTURAL_LANGUAGE_MAP, resolve_artist_canonical_name
from src.engine.catalog_resolver import lookup_catalog_track, normalize_title, clean_catalog_folder_name
from src.engine.pravachan_resolver import resolve_pravachan_track

VAULT_DIR = r"D:\Songs\unorganized\_staging_vault"
CATALOG_DB = os.path.join(PROJECT_ROOT, "master_cross_drive_catalog.db")

def get_original_path_lookup():
    conn = sqlite3.connect(CATALOG_DB)
    c = conn.cursor()
    c.execute("SELECT filename, file_path FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
    lookup = defaultdict(list)
    for fname, fpath in c.fetchall():
        lookup[fname.lower()].append(fpath)
    conn.close()
    return lookup

def resolve_file(rel_path, fname, orig_lookup):
    f_lower = fname.lower()
    full_orig = rel_path.lower()
    
    # 1. Cultural Language Map Override (Highest Priority)
    for k, (lang, cat, alb) in CULTURAL_LANGUAGE_MAP.items():
        k_re = r"\b" + r"[-\s]*".join(re.escape(w) for w in k.split()) + r"\b"
        if re.search(k_re, f_lower) or re.search(k_re, full_orig):
            return lang, cat, alb

    # 2. Pravachan Resolver
    if any(k in full_orig for k in ["pravachan", "katha", "ghaisasi", "kavishwar", "abhyankar", "gita pathan"]):
        res = resolve_pravachan_track(rel_path, fname)
        if res:
            return "Pravachan", res.get("category", "Discourses"), res.get("album", "Discourses")

    # 3. Catalog Resolver Lookup
    res = lookup_catalog_track(fname)
    if res:
        return res[0], res[1], res[2]

    # 4. Check Original Cross-Drive Source Path
    orig_paths = orig_lookup.get(f_lower, [])
    for op in orig_paths:
        op_lower = op.lower()
        if "marathi" in op_lower:
            # Check for movie or artist
            parts = op.split("\\")
            for i, p in enumerate(parts):
                if p.lower() == "marathi" and i + 1 < len(parts) - 1:
                    cand = clean_catalog_folder_name(parts[i+1])
                    if cand and cand.lower() not in ["songs", "new", "old", "artist"]:
                        return "Marathi", f"Soundtracks\\{cand}", cand
            return "Marathi", "Bhavgeet & Classics", "Bhavgeet & Classics"
        elif "english" in op_lower:
            parts = op.split("\\")
            for i, p in enumerate(parts):
                if p.lower() in ["english", "discography"] and i + 1 < len(parts) - 1:
                    cand = clean_catalog_folder_name(parts[i+1])
                    if cand and cand.lower() not in ["singles", "soundtracks", "compilations", "random"]:
                        cand = resolve_artist_canonical_name(cand)
                        return "English", cand, cand
            return "English", "Rock & Pop", "Rock & Pop"
        elif "hindi" in op_lower:
            parts = op.split("\\")
            for i, p in enumerate(parts):
                if p.lower() in ["soundtracks", "movies", "new", "old"] and i + 1 < len(parts) - 1:
                    cand = clean_catalog_folder_name(parts[i+1])
                    if cand and cand.lower() not in ["songs", "new", "old", "soundtracks"]:
                        return "Hindi", f"Soundtracks\\{cand}", cand
                if p.lower() == "albums" and i + 1 < len(parts) - 1:
                    cand = clean_catalog_folder_name(parts[i+1])
                    if cand:
                        return "Hindi", f"Albums\\{cand}", cand

    # 5. Default by vault directory context if present
    parts = rel_path.split("\\")
    top = parts[0] if parts else "Hindi"
    if top in ["Hindi", "Marathi", "English", "Pravachan", "Sanskrit", "Ringtones & Alerts"]:
        # Sub-folder within top
        if len(parts) > 2:
            sub = clean_catalog_folder_name(parts[1])
            if top == "English":
                sub = resolve_artist_canonical_name(sub)
            return top, sub, sub
        return top, "Soundtracks\\Classics" if top == "Hindi" else "General", "General"

    return "Hindi", "Soundtracks\\Classics", "Classics"

def main():
    print("Loading cross-drive catalog lookup...")
    orig_lookup = get_original_path_lookup()
    print("Catalog loaded.")

    lang_counts = defaultdict(int)
    category_counts = defaultdict(lambda: defaultdict(int))
    bracket_errors = []
    evergreen_detected = []

    total_files = 0
    for root, _, files in os.walk(VAULT_DIR):
        for f in files:
            if not f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.aac')):
                continue
            total_files += 1
            rel = os.path.relpath(os.path.join(root, f), VAULT_DIR)
            lang, cat, alb = resolve_file(rel, f, orig_lookup)

            # Sanitize paths
            clean_cat = sanitize_relative_path(cat)
            clean_fn = sanitize_filename(f)
            target_path = os.path.join(lang, clean_cat, clean_fn)

            if "(" in target_path or ")" in target_path or "[" in target_path or "]" in target_path:
                bracket_errors.append(target_path)

            if "Evergreen Classics" in target_path:
                evergreen_detected.append(target_path)

            lang_counts[lang] += 1
            category_counts[lang][clean_cat] += 1

    print("\n--- RESOLUTION SUMMARY ---")
    print(f"Total files analyzed: {total_files}")
    print(f"Bracket violations in generated paths: {len(bracket_errors)}")
    print(f"Evergreen Classics in generated paths: {len(evergreen_detected)}")
    print("\nLanguage Distribution:")
    for lang, cnt in sorted(lang_counts.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {cnt} tracks ({len(category_counts[lang])} distinct categories)")

    print("\nHindi Categories Sample (First 15):")
    hindi_cats = sorted(category_counts["Hindi"].items(), key=lambda x: -x[1])
    for c, cnt in hindi_cats[:15]:
        print(f"  Hindi\\{c}: {cnt} tracks")

    print("\nEnglish Categories Sample (First 15):")
    eng_cats = sorted(category_counts["English"].items(), key=lambda x: -x[1])
    for c, cnt in eng_cats[:15]:
        print(f"  English\\{c}: {cnt} tracks")

    print("\nMarathi Categories Sample (First 15):")
    mar_cats = sorted(category_counts["Marathi"].items(), key=lambda x: -x[1])
    for c, cnt in mar_cats[:15]:
        print(f"  Marathi\\{c}: {cnt} tracks")

if __name__ == "__main__":
    main()
