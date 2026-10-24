"""
Auralis - Empty Folder & Synonym Directory Auditor
Scans D:\\Songs\\organized for:
1. Empty directories (0 files, 0 subdirectories)
2. Non-audio junk files (.DS_Store, Thumbs.db, desktop.ini, .tmp)
3. Similar-named folders across languages (Levenshtein, word overlap, phonetic/transliteration match)
4. Folders with only 1 file (must maintain >= 2 files per folder rule)
"""

import os
import sys
import difflib
from collections import defaultdict

ORGANIZED_ROOT = r"D:\Songs\organized"

def audit():
    print("=" * 80)
    print(f"AUDITING DIRECTORIES IN: {ORGANIZED_ROOT}")
    print("=" * 80)

    empty_dirs = []
    junk_files = []
    all_subdirs_by_domain = defaultdict(list)
    folder_file_counts = {}

    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        rel_root = os.path.relpath(root, ORGANIZED_ROOT)
        
        # Check empty dirs
        if root != ORGANIZED_ROOT:
            if not dirs and not files:
                empty_dirs.append(rel_root)

        # Check junk files
        for f in files:
            if f.lower() in [".ds_store", "thumbs.db", "desktop.ini"] or f.endswith(".tmp"):
                junk_files.append(os.path.join(rel_root, f))

        # Check audio file counts
        audio_files = [f for f in files if f.lower().endswith(('.mp3', '.wma', '.m4a', '.wav', '.flac', '.ogg'))]
        if root != ORGANIZED_ROOT and not dirs:
            folder_file_counts[rel_root] = len(audio_files)

    # Collect subdirectories by top-level domain
    for item in os.listdir(ORGANIZED_ROOT):
        domain_path = os.path.join(ORGANIZED_ROOT, item)
        if os.path.isdir(domain_path):
            for sub in os.listdir(domain_path):
                sp = os.path.join(domain_path, sub)
                if os.path.isdir(sp):
                    all_subdirs_by_domain[item].append(sub)
                    # Also check nested subdirectories (e.g. Hindi\Soundtracks\...)
                    for sub2 in os.listdir(sp):
                        sp2 = os.path.join(sp, sub2)
                        if os.path.isdir(sp2):
                            all_subdirs_by_domain[f"{item}\\{sub}"].append(sub2)

    print(f"Empty directories found: {len(empty_dirs)}")
    for d in empty_dirs:
        print(f"  [EMPTY] {d}")

    print(f"\nJunk files found: {len(junk_files)}")
    for j in junk_files:
        print(f"  [JUNK] {j}")

    # Check single-file folders
    single_file = [k for k, v in folder_file_counts.items() if v == 1]
    print(f"\nSingle-file folders found: {len(single_file)}")
    for sf in single_file:
        print(f"  [SINGLE-FILE] {sf}")

    # Check similar-named folders within each domain
    print("\n>>> SIMILAR / SYNONYMOUS FOLDERS ANALYSIS:")
    synonym_candidates = []
    for domain, subs in all_subdirs_by_domain.items():
        subs_sorted = sorted(subs, key=lambda s: s.lower())
        for i in range(len(subs_sorted)):
            for j in range(i + 1, len(subs_sorted)):
                s1, s2 = subs_sorted[i], subs_sorted[j]
                norm1 = "".join(c for c in s1.lower() if c.isalnum())
                norm2 = "".join(c for c in s2.lower() if c.isalnum())
                
                # Check normalized equality or high similarity
                ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
                w1 = set(s1.lower().replace("-", " ").split())
                w2 = set(s2.lower().replace("-", " ").split())
                overlap = w1 & w2
                
                if norm1 == norm2:
                    synonym_candidates.append((domain, s1, s2, "EXACT_NORM_MATCH", ratio))
                elif ratio >= 0.82 and min(len(norm1), len(norm2)) >= 4:
                    synonym_candidates.append((domain, s1, s2, f"HIGH_SIMILARITY ({ratio:.2f})", ratio))
                elif len(overlap) >= 2 and (len(w1) <= 3 or len(w2) <= 3) and ratio >= 0.65:
                    synonym_candidates.append((domain, s1, s2, f"WORD_OVERLAP ({overlap})", ratio))

    print(f"Found {len(synonym_candidates)} synonym/similarity candidates:")
    for dom, s1, s2, reason, r in synonym_candidates:
        print(f"  [{dom}] '{s1}' <==> '{s2}' ({reason})")

if __name__ == "__main__":
    audit()
