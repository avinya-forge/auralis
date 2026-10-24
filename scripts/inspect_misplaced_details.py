import json

with open("misplacements_audit.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print("1. TRACKS TARGETED TO ENGLISH (Originated in Hindi or Marathi)")
print("=" * 80)
for d in data:
    if d["target_lang"] == "English" and d["orig_lang"] != "English":
        print(f"Target:   {d['organized_path']}")
        print(f"Orig:     {d['orig_path']}")
        print(f"OrigName: {d['orig_filename']} | Title: {d['orig_title']}\n")

print("=" * 80)
print("2. TRACKS TARGETED TO SANSKRIT (Originated in Hindi, Marathi, English)")
print("=" * 80)
for d in data:
    if d["target_lang"] == "Sanskrit" and d["orig_lang"] != "Sanskrit":
        print(f"Target:   {d['organized_path']}")
        print(f"Orig:     {d['orig_path']}")
        print(f"OrigName: {d['orig_filename']} | Title: {d['orig_title']}\n")

print("=" * 80)
print("3. TRACKS TARGETED TO HINDI (Originated in Marathi or English)")
print("=" * 80)
for d in data:
    if d["target_lang"] == "Hindi" and d["orig_lang"] != "Hindi":
        print(f"Target:   {d['organized_path']}")
        print(f"Orig:     {d['orig_path']}")
        print(f"OrigName: {d['orig_filename']} | Title: {d['orig_title']}\n")
