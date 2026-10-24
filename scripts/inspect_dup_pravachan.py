import os

dup_dir = r"D:\Songs\unorganized\_duplicates_backup"
files = os.listdir(dup_dir)

keywords = ["kavish", "ghaisasi", "abhyankar", "bhagwat", "katha", "pravachan", "dutta", "gita", "geeta", "ramdas", "day", "yog"]
dup_prav = [f for f in files if any(k in f.lower() for k in keywords)]

print(f"Total files in duplicates backup: {len(files)}")
print(f"Pravachan files in duplicates backup: {len(dup_prav)}")

for f in sorted(dup_prav)[:40]:
    print("  ", f)
