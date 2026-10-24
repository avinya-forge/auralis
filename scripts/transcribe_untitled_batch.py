"""
Transcribe untitled tracks using Whisper with slice extraction and export to JSON.
"""
import os
import sys
import json
import imageio_ffmpeg
import whisper
import whisper.audio as wa

ff_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ['PATH'] = ff_dir + os.pathsep + os.environ['PATH']

model = whisper.load_model('base')
d = r'D:\Songs\organized\Hindi\Soundtracks\Assorted Classics'
untitled_files = sorted([f for f in os.listdir(d) if 'untitled' in f.lower()])

results = {}
for idx, f in enumerate(untitled_files):
    p = os.path.join(d, f)
    audio = wa.load_audio(p)
    dur = len(audio) / wa.SAMPLE_RATE
    # For songs, take slice between 35s and 65s (usually where mukhda begins)
    start = min(35.0, max(0.0, dur / 4.0))
    end = min(start + 30.0, dur)
    segment = audio[int(start * wa.SAMPLE_RATE):int(end * wa.SAMPLE_RATE)]
    
    # Transcribe in auto/Marathi
    res = model.transcribe(segment, fp16=False)
    text = res['text'].strip()
    lang = res.get('language', 'unknown')
    results[f] = {
        'duration': dur,
        'language': lang,
        'text': text
    }
    safe_text = text.encode('ascii', 'backslashreplace').decode('ascii')
    print(f"[{idx+1}/{len(untitled_files)}] {f} ({dur:.1f}s) [{lang}]: {safe_text}")

with open('untitled_transcriptions.json', 'w', encoding='utf-8') as fp:
    json.dump(results, fp, indent=2, ensure_ascii=False)

print("\nDone! Saved to untitled_transcriptions.json")
