with open('tests/conftest.py', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = 'for name in ["APIC", "TALB", "TCON", "TDRC", "TIT2", "TPE1", "TPE2", "TRCK", "ID3", "USLT"]:'
repl1 = 'for name in ["APIC", "TALB", "TCON", "TDRC", "TIT2", "TPE1", "TPE2", "TRCK", "ID3", "USLT", "TCOM", "TEXT"]:'
c = c.replace(target1, repl1)

target2 = 'mock_mp4.MP4 = MP4'
repl2 = '''mock_mp4.MP4 = MP4
class MP4Cover(MagicMock):
    FORMAT_JPEG = 13
mock_mp4.MP4Cover = MP4Cover

mock_wave = types.ModuleType("mutagen.wave")
class WAVE(MagicMock):
    pass
mock_wave.WAVE = WAVE
mock_mutagen.wave = mock_wave
sys.modules["mutagen.wave"] = mock_wave'''

if target2 in c and 'mock_wave' not in c:
    c = c.replace(target2, repl2)

with open('tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Successfully patched tests/conftest.py')
