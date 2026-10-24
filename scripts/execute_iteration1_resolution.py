"""
Auralis - Iteration 1: Authentic Music Library Resolver & Re-homing Engine
Resolves:
1. All files in Hindi\\Soundtracks\\Assorted Classics -> genuine movie/Natyasangeet destinations.
2. Vague & polluted prefixes: 'Track ', 'Unknown - '.
3. Misplaced cross-language and indie tracks (Rocky, Song 2, Agnee, Ra.One, Metro).
4. Standardize bracket titles to eliminate bracket path violations.
"""

import os
import sys
import shutil
import json
import sqlite3
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, TCOM, TEXT

ORGANIZED = r"D:\Songs\organized"

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def safe_move(src: str, dst: str):
    if not os.path.exists(src):
        return False
    ensure_dir(os.path.dirname(dst))
    if os.path.exists(dst) and os.path.abspath(src) != os.path.abspath(dst):
        # Destination exists, check if duplicate or rename
        base, ext = os.path.splitext(dst)
        dst = f"{base} (Alt){ext}"
    shutil.move(src, dst)
    return True

def run_iteration1():
    print("=" * 80)
    print("STARTING ITERATION 1: AUTHENTIC RESOLUTION & RE-HOMING")
    print("=" * 80)

    # 1. Resolve 'Untitled' files in Assorted Classics
    with open('exact_untitled_origins.json', 'r', encoding='utf-8') as f:
        untitled_map = json.load(f)

    natya_album_map = {
        '10 natea suresh': ('Marathi\\Natyasangeet\\Suresh Haldankar', 'Suresh Haldankar', 'Natyasangeet - Suresh Haldankar', 'Pandit Jitendra Abhisheki'),
        '11 sath deti himshekari part 1': ('Marathi\\Natyasangeet\\Saath Deti Himshekhari', 'Various Artists', 'Saath Deti Himshekhari', 'Vasant Desai'),
        '12_bakul pandit - natya sangeet': ('Marathi\\Natyasangeet\\Bakul Pandit', 'Bakul Pandit', 'Natyasangeet - Bakul Pandit', 'Traditional Natyasangeet'),
        '14_uthang natyashilpa': ('Marathi\\Natyasangeet\\Uttung Natyashilpa', 'Various Artists', 'Uttung Natyashilpa', 'Traditional Natyasangeet'),
        '15  pushp parag': ('Marathi\\Natyasangeet\\Pushpa Parag', 'Various Artists', 'Pushpa Parag', 'Traditional Natyasangeet'),
        '16 gajlyli natea geete part 2': ('Marathi\\Natyasangeet\\Gajleli Natyageete', 'Various Artists', 'Gajleli Natyageete Vol 2', 'Traditional Natyasangeet'),
        '02 _ramdas kamat': ('Marathi\\Natyasangeet\\Ramdas Kamat', 'Ramdas Kamat', 'Natyasangeet - Ramdas Kamat', 'Govindrao Tembe'),
        '04 _natea sangeet part 1': ('Marathi\\Natyasangeet\\Natyasangeet Suvarna Kal', 'Various Artists', 'Natyasangeet Suvarna Kal Vol 1', 'Traditional Natyasangeet'),
        '07 _natea sangeet part 2 -': ('Marathi\\Natyasangeet\\Natyasangeet Ratnamala', 'Various Artists', 'Natyasangeet Ratnamala Vol 2', 'Traditional Natyasangeet'),
        '09  natea banthali theu he - ajit': ('Marathi\\Natyasangeet\\Ajit Kadkade', 'Ajit Kadkade', 'Natyasangeet - Banthali Thev', 'Traditional Natyasangeet')
    }

    assorted_dir = os.path.join(ORGANIZED, "Hindi", "Soundtracks", "Assorted Classics")

    # Special specific track resolutions
    specific_resolutions = {
        'Untitled .Mp3 - Part 11.mp3': ('Marathi\\Natyasangeet\\Suresh Haldankar', 'Vilopale Madhumilanat Ya (Alap Intro).mp3', 'Suresh Haldankar', 'Natyasangeet - Suresh Haldankar', '1965'),
        'Untitled .Mp3 - Part 12.mp3': ('Marathi\\Natyasangeet\\Suresh Haldankar', 'Vilopale Madhumilanat Ya.mp3', 'Suresh Haldankar', 'Natyasangeet - Suresh Haldankar', '1965'),
        'Untitled .Mp3 - Part 18.mp3': ('Hindi\\Soundtracks\\Kuch Naa Kaho', 'Achhi Lagti Ho.mp3', 'Udit Narayan & Kavita Krishnamurthy', 'Kuch Naa Kaho', '2003'),
        'Untitled .Mp3 - Part 31.mp3': ('Sanskrit\\Vedic Samhita\\Shrimad Bhagawat Samhita', 'Bhagawat Samhita Chapter 05 Part 11.mp3', 'Traditional Vedic Chants', 'Shrimad Bhagawat Samhita', 'Vedic Era'),
        'Untitled .Mp3 - Part 32.mp3': ('Hindi\\Soundtracks\\Tere Naam', 'O Jaana.mp3', 'Udit Narayan & Alka Yagnik', 'Tere Naam', '2003'),
        'Untitled - Various Artists.mp3': ('Hindi\\Artists\\Pankaj Udhas', 'Yaad Aane Lagi.mp3', 'Pankaj Udhas', 'Stolen Moments', '1999'),
    }

    for f, info in untitled_map.items():
        src_path = os.path.join(assorted_dir, f)
        if not os.path.exists(src_path):
            continue

        if f in specific_resolutions:
            rel_folder, new_fn, artist, album, year = specific_resolutions[f]
            dst_path = os.path.join(ORGANIZED, rel_folder, new_fn)
            safe_move(src_path, dst_path)
            print(f"Moved {f} -> {rel_folder}\\{new_fn}")
        else:
            orig = info['orig_path']
            # Find which natya folder it matched
            matched_folder = None
            for key, val in natya_album_map.items():
                if key in orig.lower():
                    matched_folder = val
                    break
            
            if matched_folder:
                rel_folder, artist, album, composer = matched_folder
                orig_stem = os.path.splitext(os.path.basename(orig))[0]
                new_fn = f"{album} - Track {orig_stem}.mp3"
                dst_path = os.path.join(ORGANIZED, rel_folder, new_fn)
                safe_move(src_path, dst_path)
                print(f"Moved {f} -> {rel_folder}\\{new_fn}")
            else:
                dst_path = os.path.join(ORGANIZED, "Marathi", "Natyasangeet", "Gajleli Natyageete", f)
                safe_move(src_path, dst_path)
                print(f"Moved fallback {f} -> Marathi\\Natyasangeet\\Gajleli Natyageete")

    # 2. Re-home classic tracks in Assorted Classics
    classic_track_map = {
        'Awaara Hoon.mp3': ('Hindi\\Soundtracks\\Awaara', 'Awaara Hoon.mp3', 'Mukesh', 'Awaara', '1951', 'Shankar-Jaikishan', 'Shailendra'),
        'Track Ek Bewafa Se Pyar Kiya.mp3': ('Hindi\\Soundtracks\\Awaara', 'Ek Bewafa Se Pyar Kiya.mp3', 'Lata Mangeshkar', 'Awaara', '1951', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Ek Do Teen.mp3': ('Hindi\\Soundtracks\\Awaara', 'Ek Do Teen Aaja Mausam Hai Rangeen.mp3', 'Shamshad Begum', 'Awaara', '1951', 'Shankar-Jaikishan', 'Shailendra'),
        'Track Jab Se Balam Ghar Aae.mp3': ('Hindi\\Soundtracks\\Awaara', 'Jab Se Balam Ghar Aae.mp3', 'Lata Mangeshkar', 'Awaara', '1951', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Naiya Teri Manjhdhar.mp3': ('Hindi\\Soundtracks\\Awaara', 'Naiya Teri Manjhdhar.mp3', 'Mohammed Rafi', 'Awaara', '1951', 'Shankar-Jaikishan', 'Shailendra'),

        'Track Ramaiya Vastavaiya.mp3': ('Hindi\\Soundtracks\\Shree 420', 'Ramaiya Vastavaiya.mp3', 'Lata Mangeshkar, Mukesh & Mohammed Rafi', 'Shree 420', '1955', 'Shankar-Jaikishan', 'Shailendra'),
        'Track Pyar Hua Ikrar Hua.mp3': ('Hindi\\Soundtracks\\Shree 420', 'Pyar Hua Ikrar Hua.mp3', 'Manna Dey & Lata Mangeshkar', 'Shree 420', '1955', 'Shankar-Jaikishan', 'Shailendra'),

        'Track Dil Deke Dekho.mp3': ('Hindi\\Soundtracks\\Dil Deke Dekho', 'Dil Deke Dekho.mp3', 'Mohammed Rafi', 'Dil Deke Dekho', '1959', 'Usha Khanna', 'Majrooh Sultanpuri'),
        'Track Pyar Ki Kasam Hai.mp3': ('Hindi\\Soundtracks\\Dil Deke Dekho', 'Pyar Ki Kasam Hai.mp3', 'Asha Bhosle & Mohammed Rafi', 'Dil Deke Dekho', '1959', 'Usha Khanna', 'Majrooh Sultanpuri'),
        'Track Yaar Chulbula Hai.mp3': ('Hindi\\Soundtracks\\Dil Deke Dekho', 'Yaar Chulbula Hai.mp3', 'Mohammed Rafi & Asha Bhosle', 'Dil Deke Dekho', '1959', 'Usha Khanna', 'Majrooh Sultanpuri'),

        'Track Duniyawalon Se Door.mp3': ('Hindi\\Soundtracks\\Ujala', 'Duniyawalon Se Door.mp3', 'Mukesh & Lata Mangeshkar', 'Ujala', '1959', 'Shankar-Jaikishan', 'Shailendra'),
        'O Mora Nadan Balma.mp3': ('Hindi\\Soundtracks\\Ujala', 'O Mora Nadan Balma.mp3', 'Lata Mangeshkar', 'Ujala', '1959', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Tera Jalwa Jisne Dekha.mp3': ('Hindi\\Soundtracks\\Ujala', 'Tera Jalwa Jisne Dekha.mp3', 'Manna Dey, Lata Mangeshkar & Mohammed Rafi', 'Ujala', '1959', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),

        'Track Mujhko Apne Gale Lagalo.mp3': ('Hindi\\Soundtracks\\Hamrahi', 'Mujhko Apne Gale Lagalo.mp3', 'Mubarak Begum & Mohammed Rafi', 'Hamrahi', '1963', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Yeh Ansoo Mere Dil Ki Zuban Hai.mp3': ('Hindi\\Soundtracks\\Hamrahi', 'Yeh Ansoo Mere Dil Ki Zuban Hai.mp3', 'Mukesh', 'Hamrahi', '1963', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),

        'Track Mujhe Kahte Hain Kallu Qawwal.mp3': ('Hindi\\Soundtracks\\Dulhan Dulhan', 'Mujhe Kahte Hain Kallu Qawwal.mp3', 'Mohammed Rafi', 'Dulhan Dulhan', '1958', 'Naushad', 'Shakeel Badayuni'),
        'Track Jumme Ki Raat.mp3': ('Hindi\\Soundtracks\\Dulhan Dulhan', 'Jumme Ki Raat.mp3', 'Shamshad Begum & Mohammed Rafi', 'Dulhan Dulhan', '1958', 'Naushad', 'Shakeel Badayuni'),

        'Aise Na Jao Sanam.mp3': ('Hindi\\Artists\\Mohammed Rafi', 'Aise Na Jao Sanam.mp3', 'Mohammed Rafi', 'Parwana', '1971', 'Madan Mohan', 'Kaifi Azmi'),
        'Khayalon Mein Kisi Ke.mp3': ('Hindi\\Artists\\Mukesh', 'Khayalon Mein Kisi Ke.mp3', 'Mukesh & Geeta Dutt', 'Bawre Nain', '1950', 'Roshan', 'Kedar Sharma'),
        'Tere Bin Soone Nain Hamare.mp3': ('Hindi\\Soundtracks\\Meri Surat Teri Ankhen', 'Tere Bin Soone Nain Hamare.mp3', 'Lata Mangeshkar & Mohammed Rafi', 'Meri Surat Teri Ankhen', '1963', 'S.D. Burman', 'Shailendra'),
        'Track Poochho Na Kaise Maine I.mp3': ('Hindi\\Soundtracks\\Meri Surat Teri Ankhen', 'Poochho Na Kaise Maine Rain Bitai.mp3', 'Manna Dey', 'Meri Surat Teri Ankhen', '1963', 'S.D. Burman', 'Shailendra'),
        'Wafa Jin Se Ki Bewafa Ho Gaye.mp3': ('Hindi\\Artists\\Mukesh', 'Wafa Jin Se Ki Bewafa Ho Gaye.mp3', 'Mukesh', 'Pyar Ka Saagar', '1961', 'Ravi', 'Prem Dhawan'),
        'Track Budtameez Kaho.mp3': ('Hindi\\Artists\\Mohammed Rafi', 'Budtameez Kaho Ya Kaho Janwar.mp3', 'Mohammed Rafi', 'Junglee', '1961', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Dil Ko Na Mere.mp3': ('Hindi\\Artists\\Lata Mangeshkar', 'Dil Ko Na Mere Tadpao.mp3', 'Lata Mangeshkar', 'Sargam', '1950', 'C. Ramchandra', 'P.L. Santoshi'),
        'Track Haseen Ho Tum.mp3': ('Hindi\\Artists\\Mohammed Rafi', 'Haseen Ho Tum Khuda Nahin Ho.mp3', 'Mohammed Rafi', 'Pyaar Ka Mausam', '1969', 'R.D. Burman', 'Majrooh Sultanpuri'),
        'Track Mujhe Apna Yaar Banalo Happy.mp3': ('Hindi\\Artists\\Mohammed Rafi', 'Mujhe Apna Yaar Banalo.mp3', 'Mohammed Rafi', 'Boy Friend', '1961', 'Shankar-Jaikishan', 'Hasrat Jaipuri'),
        'Track Salam Aape Ki Meethi Nazarki.mp3': ('Hindi\\Artists\\Mohammed Rafi', 'Salam Aapki Meethi Nazar Ko Salam.mp3', 'Mohammed Rafi & Asha Bhosle', 'Do Phool', '1958', 'Vasant Desai', 'Hasrat Jaipuri'),
        'Rocky Soundtrack - Bill Conti - Rocky - Gonna Fly Now.mp3': ('English\\Soundtracks', 'Rocky - Gonna Fly Now.mp3', 'Bill Conti', 'Rocky', '1976', 'Bill Conti', 'Carol Connors'),
    }

    for fn, tinfo in classic_track_map.items():
        src_path = os.path.join(assorted_dir, fn)
        if os.path.exists(src_path):
            rel_folder, new_fn = tinfo[0], tinfo[1]
            dst_path = os.path.join(ORGANIZED, rel_folder, new_fn)
            safe_move(src_path, dst_path)
            print(f"Re-homed {fn} -> {rel_folder}\\{new_fn}")

    # Remove Assorted Classics if empty
    if os.path.exists(assorted_dir) and not os.listdir(assorted_dir):
        os.rmdir(assorted_dir)
        print("Removed empty folder: Hindi\\Soundtracks\\Assorted Classics")

    # 3. Clean up Vague & Polluted prefixes across the entire library
    cleanup_renames = [
        # Track prefixes
        (r"Hindi\Soundtracks\Aap Ki Kasam\Track Mujhe Pyar Ki Zindagi Denewale.mp3", r"Hindi\Soundtracks\Aap Ki Kasam\Mujhe Pyar Ki Zindagi Denewale.mp3"),
        (r"Hindi\Soundtracks\Mere Mehboob\Track 2 Tere Pyar Mein Dildar.mp3", r"Hindi\Soundtracks\Mere Mehboob\Tere Pyar Mein Dildar.mp3"),
        (r"Hindi\Soundtracks\Mere Mehboob\Track Mere Mehboob Tujhe M.mp3", r"Hindi\Soundtracks\Mere Mehboob\Mere Mehboob Tujhe Meri Mohabbat Ki Kasam.mp3"),
        (r"Hindi\Soundtracks\Mere Mehboob\Track Yaad Mein Teri.mp3", r"Hindi\Soundtracks\Mere Mehboob\Yaad Mein Teri.mp3"),
        (r"Hindi\Soundtracks\Dulhan Dulhan\Track Jo Pyar Tum Ne.mp3", r"Hindi\Soundtracks\Dulhan Dulhan\Jo Pyar Tumne Diya Mujhe.mp3"),
        (r"Hindi\Soundtracks\Khilona\Track Sada Khush Rahe Tu Jafa Karnewale.mp3", r"Hindi\Soundtracks\Khilona\Sada Khush Rahe Tu Jafa Karnewale.mp3"),
        (r"Hindi\Soundtracks\Paap\Track 2 Karke Jiska Intezar.mp3", r"Hindi\Soundtracks\Paap\Karke Jiska Intezar.mp3"),
        (r"Hindi\Soundtracks\Pavitra Papi\Track Teri Duniya Mein Dil Lagta Nahin.mp3", r"Hindi\Soundtracks\Pavitra Papi\Teri Duniya Mein Dil Lagta Nahin.mp3"),
        (r"Hindi\Soundtracks\Shree 420\Track Mera Joota Hai Japani.mp3", r"Hindi\Soundtracks\Shree 420\Mera Joota Hai Japani.mp3"),
        (r"Hindi\Artists\Mohammed Rafi\Track Hum Aur Tum Aur Yeh Sama.mp3", r"Hindi\Artists\Mohammed Rafi\Hum Aur Tum Aur Yeh Sama.mp3"),
        
        # Unknown prefixes
        (r"Hindi\Soundtracks\Dev D\Unknown - Emosanalattyachar.mp3", r"Hindi\Soundtracks\Dev D\Emosanal Attyachar.mp3"),
        (r"Hindi\Soundtracks\Dor\Unknown - Yeh Hosla.mp3", r"Hindi\Soundtracks\Dor\Yeh Honsla.mp3"),
        (r"Hindi\Soundtracks\Force\Unknown - Khwabon Khwabon Force Hindi Leak Version.mp3", r"Hindi\Soundtracks\Force\Khwabon Khwabon.mp3"),
        (r"Hindi\Soundtracks\Johnny Gaddaar\Unknown - Johnny House.mp3", r"Hindi\Soundtracks\Johnny Gaddaar\Johnny House.mp3"),
        (r"Hindi\Soundtracks\Johnny Gaddaar\Unknown - Move U'R Body.mp3", r"Hindi\Soundtracks\Johnny Gaddaar\Move Your Body.mp3"),
        (r"Hindi\Soundtracks\Naqaab\Unknown - Ek Din Teri Raahon.mp3", r"Hindi\Soundtracks\Naqaab\Ek Din Teri Raahon.mp3"),
        (r"Hindi\Soundtracks\Salaam-E-Ishq\Unknown - Saiyaan Re Si.mp3", r"Hindi\Soundtracks\Salaam-E-Ishq\Saiyaan Re.mp3"),
        (r"Hindi\Soundtracks\Soundtrack Singles\Unknown - Inquilaab2.mp3", r"Hindi\Soundtracks\Soundtrack Singles\Inquilaab.mp3"),
        (r"Hindi\Soundtracks\Supari\Unknown - Supari2.mp3", r"Hindi\Soundtracks\Supari\Supari.mp3"),
        (r"Hindi\Soundtracks\Veer-Zaara\Unknown - Do Pal.mp3", r"Hindi\Soundtracks\Veer-Zaara\Do Pal.mp3"),
        (r"Hindi\Soundtracks\Veer-Zaara\Unknown - Mein Pal Do Pal Ka Shair Hoon.mp3", r"Hindi\Artists\Mukesh\Main Pal Do Pal Ka Shayar Hoon.mp3"),
        (r"Hindi\Soundtracks\Zeher\Unknown - Aye Bekhabar.mp3", r"Hindi\Soundtracks\Zeher\Aye Bekhabar.mp3"),
        
        # Miscellaneous vague tracks
        (r"English\Assorted Pop & Rock\Song.mp3", r"English\Blur\Song 2.mp3"),
        (r"English\Indian Rock Bands\Zero\Unknown Artist - Zero.mp3", r"Hindi\Soundtracks\3 Moonu\Idhazhin Oram.mp3"),
        (r"Hindi\Soundtracks\Life In A Metro\Track 11.wma", r"Hindi\Soundtracks\Life In A Metro\Baatein Kuch Ankahee Si - Unplugged.wma"),
        (r"Hindi\Albums\Lucky Ali\Track 10.wma", r"Hindi\Albums\Lucky Ali\Aks - Track 10.wma"),
        (r"Pravachan\Bhagwat Katha\Ghaisasi Guruji\Song.mp3", r"Pravachan\Bhagwat Katha\Ghaisasi Guruji\Bhagwat Katha Discourse.mp3"),
        (r"English\Assorted Pop & Rock\Track 1.wma", r"English\Assorted Pop & Rock\Trance Energy - Track 1.wma"),
        (r"English\Assorted Pop & Rock\Prelude.wma", r"English\Assorted Pop & Rock\Trance Energy - Prelude.wma"),

        # Assorted Bollywood misplacements
        (r"Hindi\Soundtracks\Assorted Bollywood\Bhare Naina.mp3", r"Hindi\Soundtracks\Ra.One\Bhare Naina.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Dino.mp3", r"Hindi\Soundtracks\Life In A Metro\In Dino.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Aahatein.mp3", r"English\Indian Rock Bands\Agnee\Aahatein.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Bin Tere Jawad Ahmad.mp3", r"Hindi\Albums\Indipop Classics\Bin Tere - Jawad Ahmad.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Glassy Sona Family.mp3", r"Hindi\Albums\Indipop Classics\The Glassy - Ashok Mastie & Sona Family.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Ey Gori Holi.mp3", r"Hindi\Soundtracks\Delhi Heights\Ey Gori Holi.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\De Dana Dan U I.mp3", r"Hindi\Soundtracks\De Dana Dan\De Dana Dan.mp3"),

        # Bracket path sanitization (standardizing parentheses to hyphens)
        (r"English\Bob Marley\Rainbow Country (Fatboy Slim Remix).mp3", r"English\Bob Marley\Rainbow Country - Fatboy Slim Remix.mp3"),
        (r"English\Indian Rock Bands\Demonic Resurrection\Demonic Resurrection (Title Track).mp3", r"English\Indian Rock Bands\Demonic Resurrection\Demonic Resurrection - Title Track.mp3"),
        (r"English\Soundtracks\A Beautiful Mind (Main Theme).mp3", r"English\Soundtracks\A Beautiful Mind - Main Theme.mp3"),
        (r"English\Soundtracks\Ghostbusters (Main Theme).mp3", r"English\Soundtracks\Ghostbusters - Main Theme.mp3"),
        (r"Hindi\Albums\Indipop Classics\Emptiness (Tune Mere Jaana).mp3", r"Hindi\Albums\Indipop Classics\Emptiness - Tune Mere Jaana.mp3"),
        (r"Hindi\Albums\Indipop Classics\Ishq Tera Tadpave (Oh Ho Ho Ho).mp3", r"Hindi\Albums\Indipop Classics\Ishq Tera Tadpave - Oh Ho Ho Ho.mp3"),
        (r"Hindi\Soundtracks\Assorted Bollywood\Tera Mera Rishta (Remix).mp3", r"Hindi\Soundtracks\Assorted Bollywood\Tera Mera Rishta - Remix.mp3"),
        (r"Hindi\Soundtracks\Krazzy 4\Krazzy 4 (Title Track).mp3", r"Hindi\Soundtracks\Krazzy 4\Krazzy 4 - Title Track.mp3"),
        (r"Hindi\Soundtracks\Life In A Metro\Baatein Kuch Ankahee Si (Unplugged).mp3", r"Hindi\Soundtracks\Life In A Metro\Baatein Kuch Ankahee Si - Unplugged.mp3"),
        (r"Hindi\Soundtracks\Soundtrack Singles\Ha Raham (Mehfuz).mp3", r"Hindi\Soundtracks\Soundtrack Singles\Ha Raham - Mehfuz.mp3")
    ]

    for rel_src, rel_dst in cleanup_renames:
        full_src = os.path.join(ORGANIZED, rel_src)
        full_dst = os.path.join(ORGANIZED, rel_dst)
        if os.path.exists(full_src):
            safe_move(full_src, full_dst)
            print(f"Renamed: {rel_src} -> {rel_dst}")

    print("\nITERATION 1 RESOLUTION AND RE-HOMING COMPLETE!")

if __name__ == '__main__':
    run_iteration1()
