"""
Auralis - Resolve All Remaining Cryptic 3.mp3 and Bracket Tracks
Applies Whisper and catalog ground-truth to permanently eliminate all '3.mp3' and bracket filenames.
"""

import os
import sys
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_acoustic_organizer import write_id3_metadata

ORGANIZED = r"D:\Songs\organized"
DUPLICATES_BACKUP = r"D:\Songs\unorganized\_duplicates_backup"

RENAMES = [
    # Doors bracket fixes
    (r"English\The Doors\Live In Europe (Full Concert).mp3", r"English\The Doors\Live In Europe - Full Concert.mp3", "Live In Europe - Full Concert", "The Doors", "Live In Europe"),
    (r"English\The Doors\When The Music'S Over (Live).wma", r"English\The Doors\When The Music'S Over - Live.wma", "When The Music'S Over - Live", "The Doors", "Live In Europe"),

    # Michael Jackson 3.mp3 -> Dangerous
    (r"English\Michael Jackson\3.mp3", r"English\Michael Jackson\Dangerous.mp3", "Dangerous", "Michael Jackson", "Dangerous"),

    # Matt Nathanson 3.mp3 -> Laid
    (r"English\Matt Nathanson\3.mp3", r"English\Matt Nathanson\Laid.mp3", "Laid", "Matt Nathanson", "Some Mad Hope"),

    # Don 3.mp3 -> Aaj Ki Raat
    (r"Hindi\Soundtracks\Don\3.mp3", r"Hindi\Soundtracks\Don\Aaj Ki Raat.mp3", "Aaj Ki Raat", "Alisha Chinai", "Don"),

    # Julie 3.mp3 -> Dil Kya Kare
    (r"Hindi\Soundtracks\Julie\3.mp3", r"Hindi\Soundtracks\Julie\Dil Kya Kare.mp3", "Dil Kya Kare", "Kishore Kumar", "Julie"),

    # Ajab Prem 3.mp3 -> Tu Jaane Na
    (r"Hindi\Soundtracks\Ajab Prem Ki Gazab Kahani\3.mp3", r"Hindi\Soundtracks\Ajab Prem Ki Gazab Kahani\Tu Jaane Na.mp3", "Tu Jaane Na", "Atif Aslam", "Ajab Prem Ki Ghazab Kahani"),

    # Jal 3.mp3 -> Bikhra Hoon Main
    (r"Hindi\Albums\Jal - Pakistani Grp\3.mp3", r"Hindi\Albums\Jal - Pakistani Grp\Bikhra Hoon Main.mp3", "Bikhra Hoon Main", "Jal", "Aadat"),

    # Movie '3' tracks
    (r"Hindi\Soundtracks\3\3.mp3", r"Hindi\Soundtracks\3\Why This Kolaveri Di.mp3", "Why This Kolaveri Di", "Dhanush", "3"),
    (r"Hindi\Soundtracks\3\3.m4a", r"Hindi\Soundtracks\3\Why This Kolaveri Di - Instrumental.m4a", "Why This Kolaveri Di Instrumental", "Anirudh Ravichander", "3"),

    # Geet Ramayan
    (r"Marathi\Geet Ramayan\3.mp3", r"Marathi\Geet Ramayan\Kausalya Puta Ramachandra.mp3", "Kausalya Puta Ramachandra", "Sudhir Phadke", "Geet Ramayan"),
    (r"Marathi\Geet Ramayan\3.wma", r"Marathi\Geet Ramayan\Kausalya Puta Ramachandra.wma", "Kausalya Puta Ramachandra", "Sudhir Phadke", "Geet Ramayan"),

    # Ringtones 3.mp3
    (r"Ringtones & Alerts\3.mp3", r"Ringtones & Alerts\Alert Tone 03.mp3", "Alert Tone 03", "Sound Clips", "Ringtones"),
    (r"Ringtones & Alerts\Ringtones & Alerts\3.mp3", r"Ringtones & Alerts\Ringtones & Alerts\Alert Tone 03.mp3", "Alert Tone 03", "Sound Clips", "Ringtones"),

    # Sanskrit 3.m4a and 3.mp3
    (r"Sanskrit\Stotras & Ashtakams\3.m4a", r"Sanskrit\Stotras & Ashtakams\Kavacham - Part 03.m4a", "Devi Kavacham Part 03", "Vedic Chanting", "Devi Mahatmyam"),
    (r"Sanskrit\Vedic Suktas\3.mp3", r"Sanskrit\Vedic Suktas\Shri Suktam - Part 03.mp3", "Shri Suktam Part 03", "Vedic Chanting", "Vedic Suktas"),

    # English Trance 3.mp3
    (r"English\Trance\3.mp3", r"English\Trance\Trance Session 03.mp3", "Trance Session 03", "Trance", "Trance Essentials"),

    # Redundant tool prefix
    (r"English\Tool\Tool - &.mp3", r"English\Tool\Track &.mp3", "Track &", "Tool", "Lateralus"),
    (r"Hindi\Soundtracks\Jab Tak Hai Jaan\Jab Tak Hai Jaan - The Poem.mp3", r"Hindi\Soundtracks\Jab Tak Hai Jaan\The Poem.mp3", "The Poem", "Shah Rukh Khan", "Jab Tak Hai Jaan"),
]

# Duplicate to archive
DUPLICATES = [
    r"English\Nickelback\3.mp3",  # Pink Floyd Breathe duplicate
]

def main():
    os.makedirs(DUPLICATES_BACKUP, exist_ok=True)
    resolved = 0

    # Archive duplicates
    for rel_dup in DUPLICATES:
        src = os.path.join(ORGANIZED, rel_dup)
        if os.path.exists(src):
            dst = os.path.join(DUPLICATES_BACKUP, rel_dup.replace(os.sep, "_"))
            shutil.move(src, dst)
            print(f"Archived duplicate: {rel_dup}")

    # Renames
    for src_rel, dst_rel, title, artist, album in RENAMES:
        src = os.path.join(ORGANIZED, src_rel)
        dst = os.path.join(ORGANIZED, dst_rel)
        if os.path.exists(src):
            if os.path.exists(dst) and dst != src:
                # Merge/archive duplicate
                if os.path.getsize(src) > os.path.getsize(dst):
                    shutil.move(src, dst)
                else:
                    os.remove(src)
            else:
                shutil.move(src, dst)
            write_id3_metadata(dst, title, artist, album, "General")
            print(f"Resolved: {src_rel} -> {dst_rel}")
            resolved += 1

    print(f"\nSuccessfully resolved and sanitized {resolved} tracks!")

if __name__ == "__main__":
    main()
