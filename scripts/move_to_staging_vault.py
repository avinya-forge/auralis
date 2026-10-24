import os
import shutil
import stat

ORGANIZED_ROOT = r"D:\Songs\organized"
STAGING_VAULT = r"D:\Songs\unorganized\_staging_vault"

LANGUAGE_ROOTS = [
    "Hindi",
    "Marathi",
    "English",
    "Sanskrit",
    "Pravachan",
    "Ringtones & Alerts"
]

def reset_to_staging_vault():
    print("=" * 80)
    print("PHASE 1: MOVING ORGANIZED FILES TO STAGING VAULT & CREATING EMPTY ROOTS")
    print("=" * 80)

    os.makedirs(STAGING_VAULT, exist_ok=True)
    moved_count = 0

    if os.path.exists(ORGANIZED_ROOT):
        items = os.listdir(ORGANIZED_ROOT)
        for item in items:
            src = os.path.join(ORGANIZED_ROOT, item)
            tgt = os.path.join(STAGING_VAULT, item)

            try:
                # If tgt exists, merge or move files
                if os.path.isdir(src):
                    if os.path.exists(tgt):
                        for root, dirs, files in os.walk(src):
                            rel = os.path.relpath(root, src)
                            dest_dir = os.path.join(tgt, rel)
                            os.makedirs(dest_dir, exist_ok=True)
                            for f in files:
                                f_src = os.path.join(root, f)
                                f_tgt = os.path.join(dest_dir, f)
                                if os.path.exists(f_tgt):
                                    base, ext = os.path.splitext(f)
                                    f_tgt = os.path.join(dest_dir, f"{base}_staged{ext}")
                                os.chmod(f_src, stat.S_IWRITE)
                                os.replace(f_src, f_tgt)
                                moved_count += 1
                        shutil.rmtree(src)
                    else:
                        os.chmod(src, stat.S_IWRITE)
                        os.replace(src, tgt)
                        moved_count += 1
                else:
                    if os.path.exists(tgt):
                        base, ext = os.path.splitext(item)
                        tgt = os.path.join(STAGING_VAULT, f"{base}_staged{ext}")
                    os.chmod(src, stat.S_IWRITE)
                    os.replace(src, tgt)
                    moved_count += 1
            except Exception as e:
                print(f"Error moving {src} -> {tgt}: {e}")

    print(f"[Done] Moved organized content to: {STAGING_VAULT}")

    # Create empty language roots in D:\Songs\organized
    for lang in LANGUAGE_ROOTS:
        p = os.path.join(ORGANIZED_ROOT, lang)
        os.makedirs(p, exist_ok=True)
        print(f"  Created clean empty root: {p}")

    print("\nPhase 1 Complete! D:\\Songs\\organized is now cleanly primed with empty language roots.")

if __name__ == "__main__":
    reset_to_staging_vault()
