"""
Auralis - Transcribe and Identify Remaining 3.mp3 and Cryptic Tracks
Uses Whisper to listen to vocal lyrics and rename them to canonical song titles.
"""

import os
import sys
import imageio_ffmpeg
import whisper

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.master_acoustic_organizer import write_id3_metadata

# Ensure ffmpeg is on PATH
os.environ["PATH"] = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()) + os.pathsep + os.environ["PATH"]

TARGETS = [
    (r"D:\Songs\organized\English\Michael Jackson\3.mp3", "Michael Jackson"),
    (r"D:\Songs\organized\English\Nickelback\3.mp3", "Nickelback"),
    (r"D:\Songs\organized\English\Matt Nathanson\3.mp3", "Matt Nathanson"),
    (r"D:\Songs\organized\Hindi\Albums\Jal - Pakistani Grp\3.mp3", "Jal"),
    (r"D:\Songs\organized\Hindi\Soundtracks\Ajab Prem Ki Gazab Kahani\3.mp3", "Ajab Prem Ki Gazab Kahani"),
    (r"D:\Songs\organized\Hindi\Soundtracks\Don\3.mp3", "Don"),
    (r"D:\Songs\organized\Hindi\Soundtracks\Julie\3.mp3", "Julie"),
    (r"D:\Songs\organized\Marathi\Geet Ramayan\3.mp3", "Geet Ramayan"),
]

def main():
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Whisper loaded.")

    for path, folder in TARGETS:
        if not os.path.exists(path):
            continue
        try:
            res = model.transcribe(path, fp16=False)
            text = res["text"].strip()
            print(f"\n[{folder}] -> Lyrics snippet: {text[:150]}")
        except Exception as e:
            print(f"[{folder}] Error: {e}")

if __name__ == "__main__":
    main()
