"""
Auralis - Canonical Artist & Typo Folder Unification Pass
Merges typo folders, discography subfolders, and standalone song folders into canonical artist directories.
"""

import os
import shutil

ORGANIZED = r"D:\Songs\organized"

MERGES = {
    # Marathi
    r"Marathi\P L Despande": r"Marathi\P. L. Deshpande",
    r"Marathi\Marathi Songs": r"Marathi\Bhavgeet & Classics",
    r"Marathi\Singles & Compilations": r"Marathi\Bhavgeet & Classics",

    # English Typo & Canonical Band Merges
    r"English\Pink Foyd": r"English\Pink Floyd",
    r"English\Deep Purple - The Early Years": r"English\Deep Purple",
    r"English\Michael Jackson - Discography": r"English\Michael Jackson",
    r"English\Celion Dion": r"English\Celine Dion",
    r"English\Alice Chains": r"English\Alice In Chains",
    r"English\Evanesence": r"English\Evanescence",
    r"English\Guns N' Roses": r"English\Guns N Roses",
    r"English\Led Zepplin": r"English\Led Zeppelin",
    r"English\Radio Head": r"English\Radiohead",
    r"English\Ramstein": r"English\Rammstein",
    r"English\Rhcp": r"English\Red Hot Chili Peppers",
    r"English\Inception Ost - Hans Zimmer": r"English\Soundtracks\Inception",

    # Bob Marley song folders -> Bob Marley
    r"English\Buffalo Soldier": r"English\Bob Marley",
    r"English\Could You Be Loved": r"English\Bob Marley",
    r"English\Get Up Stand Up": r"English\Bob Marley",
    r"English\No Woman No Cry": r"English\Bob Marley",
    r"English\One Love": r"English\Bob Marley",
    r"English\Rebel Music": r"English\Bob Marley",
    r"English\Stir It Up": r"English\Bob Marley",
    r"English\Three Little Birds": r"English\Bob Marley",

    # Iron Maiden song folders -> Iron Maiden
    r"English\No Prayer For The Dying": r"English\Iron Maiden",
    r"English\Fear Of The Dark": r"English\Iron Maiden",
    r"English\Running Free": r"English\Iron Maiden",

    # Indian Pop / Rock from English -> Hindi Albums
    r"English\Agnee": r"Hindi\Albums\Agnee",
    r"English\Rabbi Shergill": r"Hindi\Albums\Rabbi Shergill",
    r"English\Junoon": r"Hindi\Albums\Junoon",
}

def main():
    moved_count = 0
    cleaned_folders = 0

    for src_rel, dst_rel in MERGES.items():
        src_path = os.path.join(ORGANIZED, src_rel)
        dst_path = os.path.join(ORGANIZED, dst_rel)

        if not os.path.exists(src_path):
            continue

        os.makedirs(dst_path, exist_ok=True)
        for root, dirs, files in os.walk(src_path):
            for f in files:
                sp = os.path.join(root, f)
                dp = os.path.join(dst_path, f)
                # Clean brackets if any
                dp = dp.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                if os.path.exists(dp) and dp != sp:
                    stem, ext = os.path.splitext(dp)
                    dp = f"{stem} - Part 2{ext}"
                try:
                    shutil.move(sp, dp)
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {sp} -> {dp}: {e}")

        # Clean empty src directory tree
        try:
            shutil.rmtree(src_path)
            cleaned_folders += 1
        except Exception:
            pass

    print(f"Unification Complete: Moved {moved_count} tracks into canonical directories.")
    print(f"Removed {cleaned_folders} redundant / typo / split folders.")

if __name__ == "__main__":
    main()
