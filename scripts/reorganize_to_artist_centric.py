"""
Auralis - Reorganize to Artist-Centric Library Architecture
1. Hindi:
   - Consolidate all non-film artist folders from Hindi\\Albums, Hindi\\Ghazals, Hindi\\Devotional (Anup Jalota) into Hindi\\Artists.
   - Re-home misplaced Bollywood tracks from English back to Hindi\\Soundtracks.
   - Delete vacated category folders (Hindi\\Albums, Hindi\\Ghazals).
2. Marathi:
   - Move Natyasangeet artists (Ajit Kadkade, Bakul Pandit, Ramdas Kamat, Suresh Haldankar) to Marathi\\<Artist>.
   - Re-home iconic vocal tracks to Pt. Bhimsen Joshi, Asha Bhosle, Suman Kalyanpur, Pt. Vasantrao Deshpande, Pralhad Shinde, Anuradha Paudwal.
3. English:
   - Move Indian Rock Bands subfolders (Brahma, Demonic Resurrection, Zero) directly to English\\<Artist>.
   - Re-home loose tracks in Classic Rock, Trance, Indian Rock Bands, and Assorted Pop & Rock to their authentic artist directories.
   - Delete vacated category folders (Classic Rock, Trance, Indian Rock Bands).
4. Tag & Filename Harmonization:
   - Filename: Original song title ONLY (no prefixes, no dirty symbols).
   - Title (TIT2): Original song title.
   - Artist (TPE1): Canonical artist.
   - Album (TALB): Canonical album/movie.
   - Embedded Artwork: 100% preserved/updated.
5. Bottom-up empty directory sweeper.
"""

import os
import shutil
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON

ORGANIZED_ROOT = r"D:\Songs\organized"
BACKUP_DIR = r"D:\Songs\unorganized\_duplicates_backup"

os.makedirs(BACKUP_DIR, exist_ok=True)

def update_tags(filepath, title=None, artist=None, album=None, genre=None):
    """Update ID3 tags while strictly preserving embedded artwork."""
    try:
        audio = mutagen.File(filepath)
        if audio is None:
            return
        if not audio.tags:
            audio.add_tags()
        
        if hasattr(audio, 'tags') and isinstance(audio.tags, ID3):
            if title:
                audio.tags.setall('TIT2', [TIT2(encoding=3, text=[title])])
            if artist:
                audio.tags.setall('TPE1', [TPE1(encoding=3, text=[artist])])
            if album:
                audio.tags.setall('TALB', [TALB(encoding=3, text=[album])])
            if genre:
                audio.tags.setall('TCON', [TCON(encoding=3, text=[genre])])
            audio.save()
    except Exception as e:
        print(f"Error updating tags for {filepath}: {e}")

def safe_move(src, dst):
    """Safely move a file or directory with target directory creation."""
    if not os.path.exists(src):
        return False
    dst_dir = os.path.dirname(dst)
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(dst):
        # If destination exists and sizes match, archive source to backup
        if os.path.isfile(src) and os.path.isfile(dst):
            if os.path.getsize(src) == os.path.getsize(dst):
                safe_move(src, os.path.join(BACKUP_DIR, os.path.basename(src)))
                return True
            else:
                base, ext = os.path.splitext(os.path.basename(dst))
                dst = os.path.join(dst_dir, f"{base} - Alt{ext}")
                if os.path.exists(dst):
                    safe_move(src, os.path.join(BACKUP_DIR, os.path.basename(src)))
                    return True
    shutil.move(src, dst)
    print(f"[MOVED] {src} -> {dst}")
    return True

def run_artist_centric_reorganization():
    print("=" * 80)
    print("STARTING ARTIST-CENTRIC REORGANIZATION")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. HINDI: Consolidate all artists into Hindi\Artists
    # ---------------------------------------------------------
    print("\n>>> 1. Consolidating Hindi Artists...")
    hindi_artists_root = os.path.join(ORGANIZED_ROOT, "Hindi", "Artists")
    os.makedirs(hindi_artists_root, exist_ok=True)

    # Move all artist subdirectories from Hindi\Albums into Hindi\Artists
    hindi_albums_root = os.path.join(ORGANIZED_ROOT, "Hindi", "Albums")
    if os.path.exists(hindi_albums_root):
        for item in list(os.listdir(hindi_albums_root)):
            src_path = os.path.join(hindi_albums_root, item)
            dst_path = os.path.join(hindi_artists_root, item)
            if os.path.isdir(src_path):
                if not os.path.exists(dst_path):
                    safe_move(src_path, dst_path)
                else:
                    for f in list(os.listdir(src_path)):
                        safe_move(os.path.join(src_path, f), os.path.join(dst_path, f))

    # Move all artist subdirectories from Hindi\Ghazals into Hindi\Artists
    hindi_ghazals_root = os.path.join(ORGANIZED_ROOT, "Hindi", "Ghazals")
    if os.path.exists(hindi_ghazals_root):
        for item in list(os.listdir(hindi_ghazals_root)):
            src_path = os.path.join(hindi_ghazals_root, item)
            dst_path = os.path.join(hindi_artists_root, item)
            if os.path.isdir(src_path):
                if not os.path.exists(dst_path):
                    safe_move(src_path, dst_path)
                else:
                    for f in list(os.listdir(src_path)):
                        safe_move(os.path.join(src_path, f), os.path.join(dst_path, f))

    # Move Anup Jalota from Hindi\Devotional into Hindi\Artists
    anup_jalota_src = os.path.join(ORGANIZED_ROOT, "Hindi", "Devotional", "Anup Jalota")
    anup_jalota_dst = os.path.join(hindi_artists_root, "Anup Jalota")
    if os.path.exists(anup_jalota_src):
        if not os.path.exists(anup_jalota_dst):
            safe_move(anup_jalota_src, anup_jalota_dst)
        else:
            for f in list(os.listdir(anup_jalota_src)):
                safe_move(os.path.join(anup_jalota_src, f), os.path.join(anup_jalota_dst, f))

    # Re-home misplaced Bollywood tracks from English into Hindi\Soundtracks
    bollywood_rehomes = [
        # Source, Target Folder, Target Name, Title, Artist, Album
        (r"English\Trance\Bin Tere.mp3", r"Hindi\Soundtracks\I Hate Luv Storys", "Bin Tere.mp3",
         "Bin Tere", "Shafqat Amanat Ali & Sunidhi Chauhan", "I Hate Luv Storys"),
        (r"English\Assorted Pop & Rock\Bin Tere Reprise.mp3", r"Hindi\Soundtracks\I Hate Luv Storys", "Bin Tere - Reprise.mp3",
         "Bin Tere (Reprise)", "Shekhar Ravjiani", "I Hate Luv Storys"),
        (r"English\Trance\Dil Chahta Hai Reprise.mp3", r"Hindi\Soundtracks\Dil Chahta Hai", "Dil Chahta Hai - Reprise.mp3",
         "Dil Chahta Hai (Reprise)", "Shankar Mahadevan & Clinton Cerejo", "Dil Chahta Hai"),
        (r"English\Trance\Dil Chahta Hai Rockin Goa.mp3", r"Hindi\Soundtracks\Dil Chahta Hai", "Dil Chahta Hai - Rockin Goa.mp3",
         "Dil Chahta Hai (Rockin Goa)", "Shankar-Ehsaan-Loy", "Dil Chahta Hai"),
        (r"English\Trance\Tanhayee.mp3", r"Hindi\Soundtracks\Dil Chahta Hai", "Tanhayee.mp3",
         "Tanhayee", "Sonu Nigam", "Dil Chahta Hai"),
        (r"English\Trance\Rock On.mp3", r"Hindi\Soundtracks\Rock On", "Rock On.mp3",
         "Rock On", "Farhan Akhtar", "Rock On!!"),
        (r"English\Trance\Socha Hai.mp3", r"Hindi\Soundtracks\Rock On", "Socha Hai.mp3",
         "Socha Hai", "Farhan Akhtar", "Rock On!!"),
        (r"English\Trance\Ye Tumhari Meri Baten.mp3", r"Hindi\Soundtracks\Rock On", "Tumhari Meri Baatein.mp3",
         "Tumhari Meri Baatein", "Dominique Cerejo", "Rock On!!"),
        (r"English\Trance\O Humdum Suniyo Re.mp3", r"Hindi\Soundtracks\Saathiya", "O Humdum Suniyo Re.mp3",
         "O Humdum Suniyo Re", "Shaan, KK, Kunal Ganjawala, Pravin Mani", "Saathiya"),
        (r"English\Trance\Raaz-Soniyo.mp3", r"Hindi\Soundtracks\Raaz The Mystery Continues", "Soniyo.mp3",
         "Soniyo", "Sonu Nigam, Shreya Ghoshal & Neeraj Shridhar", "Raaz: The Mystery Continues"),
        (r"English\Trance\Roobaroo.mp3", r"Hindi\Soundtracks\Rang De Basanti", "Roobaroo.mp3",
         "Roobaroo", "A.R. Rahman & Naresh Iyer", "Rang De Basanti"),
        (r"English\Assorted Pop & Rock\It's Rocking.mp3", r"Hindi\Soundtracks\Kya Love Story Hai", "It's Rocking.mp3",
         "It's Rocking", "Alisha Chinai", "Kya Love Story Hai"),
        (r"English\Assorted Pop & Rock\Desi Beat Snippet.mp3", r"Hindi\Soundtracks\Bodyguard", "Desi Beat.mp3",
         "Desi Beat", "Mika Singh & Amrita Kak", "Bodyguard"),
        (r"English\Trance\Dosti.mp3", r"Hindi\Artists\Mohammed Rafi", "Mere Dushman Tu Meri Dosti.mp3",
         "Mere Dushman Tu Meri Dosti", "Mohammed Rafi", "Aan Milo Sajna"),
        (r"English\Classic Rock\Taandav.mp3", r"Hindi\Artists\Kailash Kher", "Taandav.mp3",
         "Taandav", "Kailash Kher", "Taandav"),
    ]

    for rel_src, rel_dst_dir, target_name, tit, art, alb in bollywood_rehomes:
        src = os.path.join(ORGANIZED_ROOT, rel_src)
        dst = os.path.join(ORGANIZED_ROOT, rel_dst_dir, target_name)
        if os.path.exists(src):
            if safe_move(src, dst):
                update_tags(dst, title=tit, artist=art, album=alb, genre="Bollywood")

    # ---------------------------------------------------------
    # 2. MARATHI: Artist-Based Marathi Library
    # ---------------------------------------------------------
    print("\n>>> 2. Restructuring Marathi Library to Artist-Centric...")
    marathi_root = os.path.join(ORGANIZED_ROOT, "Marathi")
    natyasangeet_dir = os.path.join(marathi_root, "Natyasangeet")

    # Move artist folders from Natyasangeet directly to Marathi
    if os.path.exists(natyasangeet_dir):
        for artist_folder in ["Ajit Kadkade", "Bakul Pandit", "Ramdas Kamat", "Suresh Haldankar"]:
            src_dir = os.path.join(natyasangeet_dir, artist_folder)
            dst_dir = os.path.join(marathi_root, artist_folder)
            if os.path.exists(src_dir):
                if not os.path.exists(dst_dir):
                    safe_move(src_dir, dst_dir)
                else:
                    for f in list(os.listdir(src_dir)):
                        safe_move(os.path.join(src_dir, f), os.path.join(dst_dir, f))

        # Re-home iconic Natyasangeet tracks to their singers
        natya_rehomes = [
            ("Deva Gharche Ghyave Daan.mp3", "Pt. Bhimsen Joshi", "Deva Gharche Ghyave Daan", "Pt. Bhimsen Joshi", "Natyasangeet"),
            ("Bala Gaau Kashi Angai.mp3", "Asha Bhosle", "Bala Gaau Kashi Angai", "Asha Bhosle", "Natyasangeet"),
            ("Keshava Madhava Karuna Kara.mp3", "Suman Kalyanpur", "Keshava Madhava Karuna Kara", "Suman Kalyanpur", "Natyasangeet"),
            ("Ghei Chhand Makarand.mp3", "Pt. Vasantrao Deshpande", "Ghei Chhand Makarand", "Pt. Vasantrao Deshpande", "Katyar Kaljat Ghusali"),
            ("Ghei Chhand Makarand - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Ghei Chhand Makarand - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Katyar Kaljat Ghusali"),
            ("Chandrika Hi Janu.mp3", "Pt. Vasantrao Deshpande", "Chandrika Hi Janu", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Chandrika Hi Janu - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Chandrika Hi Janu - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Priye Paha.mp3", "Pt. Vasantrao Deshpande", "Priye Paha", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Priye Paha - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Priye Paha - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Sharad Sundar Chanderi.mp3", "Pt. Vasantrao Deshpande", "Sharad Sundar Chanderi", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Sharad Sundar Chanderi - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Sharad Sundar Chanderi - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Ugavala Chandra Punvecha.mp3", "Pt. Vasantrao Deshpande", "Ugavala Chandra Punvecha", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Ugavala Chandra Punvecha - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Ugavala Chandra Punvecha - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Natyasangeet"),
            ("Shoora Mee Vandile.mp3", "Pt. Vasantrao Deshpande", "Shoora Mee Vandile", "Pt. Vasantrao Deshpande", "Maanapmaan"),
            ("Shoora Mee Vandile - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Shoora Mee Vandile - Vol 2.mp3", "Pt. Vasantrao Deshpande", "Maanapmaan"),
        ]

        for song_file, target_artist, tit, art, alb in natya_rehomes:
            src = os.path.join(natyasangeet_dir, song_file)
            dst = os.path.join(marathi_root, target_artist, song_file)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Natyasangeet")

    # In Ganpati Geete, re-home top tracks to artist folders
    ganpati_dir = os.path.join(marathi_root, "Ganpati Geete")
    if os.path.exists(ganpati_dir):
        ganpati_rehomes = [
            ("Avaghe Garaje Pandharpur.mp3", "Pt. Bhimsen Joshi", "Avaghe Garaje Pandharpur", "Pt. Bhimsen Joshi", "Abhangavani"),
            ("Abir Gulal Udhalit.mp3", "Pt. Bhimsen Joshi", "Abir Gulal Udhalit Rang", "Pt. Bhimsen Joshi", "Santanche Abhang"),
            ("Bappa Morya Re.mp3", "Pralhad Shinde", "Bappa Morya Re", "Pralhad Shinde", "Ganpati Aarti Va Geete"),
            ("Ashtvinayaka Tuja.mp3", "Anuradha Paudwal", "Ashtvinayaka Tujha Mahima Kasa", "Anuradha Paudwal & Suresh Wadkar", "Ashtavinayak"),
        ]
        for song_file, target_artist, tit, art, alb in ganpati_rehomes:
            src = os.path.join(ganpati_dir, song_file)
            dst = os.path.join(marathi_root, target_artist, song_file)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Devotional")

    # ---------------------------------------------------------
    # 3. ENGLISH: Artist-Centric Re-Homing
    # ---------------------------------------------------------
    print("\n>>> 3. Re-Homing English Tracks to Artists...")
    english_root = os.path.join(ORGANIZED_ROOT, "English")

    # Move Indian Rock Bands subfolders directly to English
    irb_root = os.path.join(english_root, "Indian Rock Bands")
    if os.path.exists(irb_root):
        for sub in ["Brahma", "Demonic Resurrection", "Zero"]:
            sp = os.path.join(irb_root, sub)
            dp = os.path.join(english_root, sub)
            if os.path.exists(sp):
                if not os.path.exists(dp):
                    safe_move(sp, dp)
                else:
                    for f in list(os.listdir(sp)):
                        safe_move(os.path.join(sp, f), os.path.join(dp, f))

        # Re-home loose tracks in Indian Rock Bands
        irb_loose = [
            ("Agnee - Aahatein.mp3", "Agnee", "Aahatein.mp3", "Aahatein", "Agnee", "Agnee"),
            ("Parikrama-Tears Of The Wizard.mp3", "Parikrama", "Tears Of The Wizard.mp3", "Tears Of The Wizard", "Parikrama", "Tears Of The Wizard"),
            ("Hook - Psp Hook Hook - Zero.wma", "Zero", "Hook.wma", "Hook", "Zero", "Albummed"),
            ("Last Days On Earth-Dream Out Loud.mp3", "Dream Out Loud", "Last Days On Earth.mp3", "Last Days On Earth", "Dream Out Loud", "Dream Out Loud"),
            ("Motherjane.mp3", "Motherjane", "Mindstreet.mp3", "Mindstreet", "Motherjane", "Maktub"),
            ("Pin Drop Violence.mp3", "Pin Drop Violence", "Title Track.mp3", "Title Track", "Pin Drop Violence", "Right About Now"),
            ("Pin Drop Violence - Alt.mp3", "Pin Drop Violence", "Title Track - Alt.mp3", "Title Track (Alt)", "Pin Drop Violence", "Right About Now"),
            ("Bhayanak Maut.mp3", "Bhayanak Maut", "Boiled Unwound.mp3", "Boiled Unwound", "Bhayanak Maut", "Bhayanak Maut"),
            ("Menwhopause.mp3", "Menwhopause", "Can't Stop Dreaming.mp3", "Can't Stop Dreaming", "Menwhopause", "Home"),
        ]
        for old_name, art_folder, new_name, tit, art, alb in irb_loose:
            src = os.path.join(irb_root, old_name)
            dst = os.path.join(english_root, art_folder, new_name)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Rock")

    # Re-home Classic Rock tracks to Artists
    classic_rock_dir = os.path.join(english_root, "Classic Rock")
    if os.path.exists(classic_rock_dir):
        cr_mappings = [
            ("Akon-Wanna Love U.mp3", "Akon", "I Wanna Love You.mp3", "I Wanna Love You", "Snoop Dogg & Akon", "Tha Blue Carpet Treatment"),
            ("Blood On The Dance Floor.mp3", "Michael Jackson", "Blood On The Dance Floor.mp3", "Blood On The Dance Floor", "Michael Jackson", "Blood on the Dance Floor"),
            ("Is It Scary.mp3", "Michael Jackson", "Is It Scary.mp3", "Is It Scary", "Michael Jackson", "Blood on the Dance Floor"),
            ("Bon Jovi Its My Life.mp3", "Bon Jovi", "It's My Life.mp3", "It's My Life", "Bon Jovi", "Crush"),
            ("Bruno Mars Lazy.mp3", "Bruno Mars", "The Lazy Song.mp3", "The Lazy Song", "Bruno Mars", "Doo-Wops & Hooligans"),
            ("C'Mon C'Mon C'Mon.wma", "Bryan Adams", "C'mon C'mon C'mon.wma", "C'mon C'mon C'mon", "Bryan Adams", "On a Day Like Today"),
            ("Carnival Of Lust.mp3", "Poets Of The Fall", "Carnival Of Rust.mp3", "Carnival Of Rust", "Poets Of The Fall", "Carnival of Rust"),
            ("Crazy Frog.mp3", "Crazy Frog", "Axel F.mp3", "Axel F", "Crazy Frog", "Crazy Hits"),
            ("Eminem - Stan.mp3", "Eminem", "Stan.mp3", "Stan", "Eminem & Dido", "The Marshall Mathers LP"),
            ("Eye Of The Tiger.mp3", "Survivor", "Eye Of The Tiger.mp3", "Eye Of The Tiger", "Survivor", "Eye of the Tiger"),
            ("Frozen Madiona.mp3", "Madonna", "Frozen.mp3", "Frozen", "Madonna", "Ray of Light"),
            ("Heaven.mp3", "Bryan Adams", "Heaven.mp3", "Heaven", "Bryan Adams", "Reckless"),
            ("Return To Innocence.mp3", "Enigma", "Return To Innocence.mp3", "Return To Innocence", "Enigma", "The Cross of Changes"),
            ("Sadness.mp3", "Enigma", "Sadeness.mp3", "Sadeness", "Enigma", "MCMXC a.D."),
            ("Savage Garden - Truly Madly Deeply.mp3", "Savage Garden", "Truly Madly Deeply.mp3", "Truly Madly Deeply", "Savage Garden", "Savage Garden"),
            ("So Yesterday.mp3", "Hilary Duff", "So Yesterday.mp3", "So Yesterday", "Hilary Duff", "Metamorphosis"),
            ("We Will Rock You.mp3", "Queen", "We Will Rock You.mp3", "We Will Rock You", "Queen", "News of the World"),
            ("You Sang To Me-Marc Anthony.mp3", "Marc Anthony", "You Sang To Me.mp3", "You Sang To Me", "Marc Anthony", "Marc Anthony"),
            ("No Matter What.mp3", "Boyzone", "No Matter What.mp3", "No Matter What", "Boyzone", "Where We Belong"),
        ]
        for old_name, art_folder, new_name, tit, art, alb in cr_mappings:
            src = os.path.join(classic_rock_dir, old_name)
            dst = os.path.join(english_root, art_folder, new_name)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Rock")

    # Re-home Trance tracks to Artists
    trance_dir = os.path.join(english_root, "Trance")
    if os.path.exists(trance_dir):
        trance_mappings = [
            ("All I Ever Wanted.mp3", "Basshunter", "All I Ever Wanted.mp3", "All I Ever Wanted", "Basshunter", "Now You're Gone"),
            ("The Night.mp3", "Basshunter", "Angel In The Night.mp3", "Angel In The Night", "Basshunter", "Now You're Gone"),
            ("Alors On Danse.mp3", "Stromae", "Alors On Danse.mp3", "Alors On Danse", "Stromae", "Cheese"),
            ("Beautiful.mp3", "Eminem", "Beautiful.mp3", "Beautiful", "Eminem", "Relapse"),
            ("Not Afraid.mp3", "Eminem", "Not Afraid.mp3", "Not Afraid", "Eminem", "Recovery"),
            ("Imma Be.mp3", "Black Eyed Peas", "Imma Be.mp3", "Imma Be", "Black Eyed Peas", "The E.N.D."),
            ("Infinity.mp3", "Mexicolas", "Times Infinity.mp3", "Times Infinity", "Mexicolas", "Times Infinity"),
            ("Rihanna-Rude Boy.mp3", "Rihanna", "Rude Boy.mp3", "Rude Boy", "Rihanna", "Rated R"),
            ("Savage Garden-To The Moon And Back.mp3", "Savage Garden", "To The Moon And Back.mp3", "To The Moon And Back", "Savage Garden", "Savage Garden"),
            ("Sean Paul.mp3", "Sean Paul", "Get Busy.mp3", "Get Busy", "Sean Paul", "Dutty Rock"),
            ("Stay With Me.mp3", "Akcent", "Stay With Me.mp3", "Stay With Me", "Akcent", "True Believers"),
            ("Stay With Me - Alt.mp3", "Akcent", "Stay With Me - Alt.mp3", "Stay With Me (Alt)", "Akcent", "True Believers"),
            ("The Game.mp3", "David Guetta", "Winner Of The Game.mp3", "Winner Of The Game", "David Guetta & JD Davis", "Pop Life"),
            ("Time.mp3", "Michael Jackson", "Remember The Time.mp3", "Remember The Time", "Michael Jackson", "Dangerous"),
            ("Tonight Pitbull.mp3", "Pitbull", "Give Me Everything.mp3", "Give Me Everything", "Pitbull, Ne-Yo, Afrojack & Nayer", "Planet Pit"),
            ("Pitbull Ft Marc Anthony Rain Over Me.mp3", "Pitbull", "Rain Over Me.mp3", "Rain Over Me", "Pitbull & Marc Anthony", "Planet Pit"),
            ("Words.mp3", "Boyzone", "Words.mp3", "Words", "Boyzone", "A Different Beat"),
            ("Djtiesto-Titanic.mp3", "Tiesto", "Titanic.mp3", "Titanic (Remix)", "Tiesto", "Club Life"),
            ("Karunesh-Punjab.mp3", "Karunesh", "Punjab.mp3", "Punjab", "Karunesh", "Global Spirit"),
            ("Part 2.mp3", "Flipsyde", "Angel.mp3", "Angel", "Flipsyde", "We the People"),
            ("Part 3.mp3", "The Beatles", "Money.mp3", "Money (That's What I Want)", "The Beatles", "With the Beatles"),
            ("Jay-Z-Empire State Of Mind Featuring Alicia Keys.mp3", "Jay-Z", "Empire State Of Mind.mp3", "Empire State Of Mind", "Jay-Z & Alicia Keys", "The Blueprint 3"),
            ("Save The World Tonight Swedish House Mafia.mp3", "Swedish House Mafia", "Save The World.mp3", "Save The World", "Swedish House Mafia", "Until Now"),
            ("Too Late To Cry Zvukoff.Ru.mp3", "John O'Callaghan", "Too Late To Cry.mp3", "Too Late To Cry", "John O'Callaghan & Audrey Gallagher", "Never Fade Away"),
        ]
        for old_name, art_folder, new_name, tit, art, alb in trance_mappings:
            src = os.path.join(trance_dir, old_name)
            dst = os.path.join(english_root, art_folder, new_name)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Dance")

    # Re-home Assorted Pop & Rock tracks to Artists
    pop_rock_dir = os.path.join(english_root, "Assorted Pop & Rock")
    if os.path.exists(pop_rock_dir):
        pr_mappings = [
            ("A Little Less Conversation.mp3", "Elvis Presley", "A Little Less Conversation.mp3", "A Little Less Conversation", "Elvis Presley vs JXL", "ELV1S: 30 #1 Hits"),
            ("Affirmation.mp3", "Savage Garden", "Affirmation.mp3", "Affirmation", "Savage Garden", "Affirmation"),
            ("I Want You.mp3", "Savage Garden", "I Want You.mp3", "I Want You", "Savage Garden", "Savage Garden"),
            ("All Rise.mp3", "Blue", "All Rise.mp3", "All Rise", "Blue", "All Rise"),
            ("Fly By Ii.mp3", "Blue", "Fly By II.mp3", "Fly By II", "Blue", "All Rise"),
            ("U Make Me Wanna.mp3", "Blue", "U Make Me Wanna.mp3", "U Make Me Wanna", "Blue", "One Love"),
            ("Love Me For A Reason.mp3", "Boyzone", "Love Me For A Reason.mp3", "Love Me For A Reason", "Boyzone", "Said and Done"),
            ("Bartender.mp3", "Akon", "Bartender.mp3", "Bartender", "T-Pain & Akon", "Epiphany"),
            ("Sexy Bitch.mp3", "David Guetta", "Sexy Bitch.mp3", "Sexy Bitch", "David Guetta & Akon", "One Love"),
            ("When Love Takes Over.mp3", "David Guetta", "When Love Takes Over.mp3", "When Love Takes Over", "David Guetta & Kelly Rowland", "One Love"),
            ("Because I Got High.mp3", "Afroman", "Because I Got High.mp3", "Because I Got High", "Afroman", "The Good Times"),
            ("Been Caught Stealing.mp3", "Jane's Addiction", "Been Caught Stealing.mp3", "Been Caught Stealing", "Jane's Addiction", "Ritual de lo Habitual"),
            ("Bittersweet Symphony.mp3", "The Verve", "Bittersweet Symphony.mp3", "Bittersweet Symphony", "The Verve", "Urban Hymns"),
            ("Black.mp3", "Pearl Jam", "Black.mp3", "Black", "Pearl Jam", "Ten"),
            ("Brainstorm.mp3", "Arctic Monkeys", "Brainstorm.mp3", "Brianstorm", "Arctic Monkeys", "Favourite Worst Nightmare"),
            ("Old Yellow Bricks.mp3", "Arctic Monkeys", "Old Yellow Bricks.mp3", "Old Yellow Bricks", "Arctic Monkeys", "Favourite Worst Nightmare"),
            ("Buddy Holly.mp3", "Weezer", "Buddy Holly.mp3", "Buddy Holly", "Weezer", "Weezer (Blue Album)"),
            ("Burn.mp3", "Usher", "Burn.mp3", "Burn", "Usher", "Confessions"),
            ("Can't Tell Me Nothing.mp3", "Kanye West", "Can't Tell Me Nothing.mp3", "Can't Tell Me Nothing", "Kanye West", "Graduation"),
            ("Counting Blue Cars.mp3", "Dishwalla", "Counting Blue Cars.mp3", "Counting Blue Cars", "Dishwalla", "Pet Your Friends"),
            ("Crash Into Me.mp3", "Dave Matthews Band", "Crash Into Me.mp3", "Crash Into Me", "Dave Matthews Band", "Crash"),
            ("Empty Walls.mp3", "Serj Tankian", "Empty Walls.mp3", "Empty Walls", "Serj Tankian", "Elect the Dead"),
            ("Epic.mp3", "Faith No More", "Epic.mp3", "Epic", "Faith No More", "The Real Thing"),
            ("Every Breath You Take.mp3", "The Police", "Every Breath You Take.mp3", "Every Breath You Take", "The Police", "Synchronicity"),
            ("Everybody Hurts.mp3", "R.E.M.", "Everybody Hurts.mp3", "Everybody Hurts", "R.E.M.", "Automatic for the People"),
            ("Losing My Religion.mp3", "R.E.M.", "Losing My Religion.mp3", "Losing My Religion", "R.E.M.", "Out of Time"),
            ("Faith.mp3", "Limp Bizkit", "Faith.mp3", "Faith", "Limp Bizkit", "Three Dollar Bill, Y'all$"),
            ("Flipsyde.mp3", "Flipsyde", "Someday.mp3", "Someday", "Flipsyde", "We the People"),
            ("Spun.mp3", "Flipsyde", "Spun.mp3", "Spun", "Flipsyde", "We the People"),
            ("Fly Away.mp3", "Lenny Kravitz", "Fly Away.mp3", "Fly Away", "Lenny Kravitz", "5"),
            ("Here Without You.mp3", "3 Doors Down", "Here Without You.mp3", "Here Without You", "3 Doors Down", "Away from the Sun"),
            ("Kryptonite.mp3", "3 Doors Down", "Kryptonite.mp3", "Kryptonite", "3 Doors Down", "The Better Life"),
            ("Hotel California.mp3", "Eagles", "Hotel California.mp3", "Hotel California", "Eagles", "Hotel California"),
            ("Already Gone.mp3", "Eagles", "Already Gone.mp3", "Already Gone", "Eagles", "On the Border"),
            ("I Believe.mp3", "Joe Satriani", "I Believe.mp3", "I Believe", "Joe Satriani", "Flying in a Blue Dream"),
            ("Summer Song.mp3", "Joe Satriani", "Summer Song.mp3", "Summer Song", "Joe Satriani", "The Extremist"),
            ("Master Of Puppets.mp3", "Metallica", "Master Of Puppets.mp3", "Master Of Puppets", "Metallica", "Master of Puppets"),
            ("My Own Worst Enemy.mp3", "Lit", "My Own Worst Enemy.mp3", "My Own Worst Enemy", "Lit", "A Place in the Sun"),
            ("No Rain.mp3", "Blind Melon", "No Rain.mp3", "No Rain", "Blind Melon", "Blind Melon"),
            ("Party Starter.mp3", "Will Smith", "Party Starter.mp3", "Party Starter", "Will Smith", "Lost and Found"),
            ("Runaway Train.mp3", "Soul Asylum", "Runaway Train.mp3", "Runaway Train", "Soul Asylum", "Grave Dancers Union"),
            ("She Hates Me.mp3", "Puddle Of Mudd", "She Hates Me.mp3", "She Hates Me", "Puddle Of Mudd", "Come Clean"),
            ("Song 2.mp3", "Blur", "Song 2.mp3", "Song 2", "Blur", "Blur"),
            ("Sorte Diaboli.mp3", "Dimmu Borgir", "The Serpentine Offering.mp3", "The Serpentine Offering", "Dimmu Borgir", "In Sorte Diaboli"),
            ("Streets Of Philadelphia.mp3", "Bruce Springsteen", "Streets Of Philadelphia.mp3", "Streets Of Philadelphia", "Bruce Springsteen", "Philadelphia Soundtrack"),
            ("The Diary Of Jane.mp3", "Breaking Benjamin", "The Diary Of Jane.mp3", "The Diary Of Jane", "Breaking Benjamin", "Phobia"),
            ("The Pretender.mp3", "Foo Fighters", "The Pretender.mp3", "The Pretender", "Foo Fighters", "Echoes, Silence, Patience & Grace"),
            ("The Reason.mp3", "Hoobastank", "The Reason.mp3", "The Reason", "Hoobastank", "The Reason"),
            ("Tubthumping.mp3", "Chumbawamba", "Tubthumping.mp3", "Tubthumping", "Chumbawamba", "Tubthumper"),
            ("Two Princes.mp3", "Spin Doctors", "Two Princes.mp3", "Two Princes", "Spin Doctors", "Pocket Full of Kryptonite"),
            ("Wicked Game.mp3", "Chris Isaak", "Wicked Game.mp3", "Wicked Game", "Chris Isaak", "Heart Shaped World"),
            ("You Oughta Know.mp3", "Alanis Morissette", "You Oughta Know.mp3", "You Oughta Know", "Alanis Morissette", "Jagged Little Pill"),
            ("Your Guardian Angel.mp3", "The Red Jumpsuit Apparatus", "Your Guardian Angel.mp3", "Your Guardian Angel", "The Red Jumpsuit Apparatus", "Don't You Fake It"),
            ("Age Of Loneliness Carly's Song.mp3", "Enigma", "Age Of Loneliness.mp3", "Age Of Loneliness", "Enigma", "The Cross of Changes"),
            ("Baby Feat Ludacris.mp3", "Justin Bieber", "Baby.mp3", "Baby", "Justin Bieber & Ludacris", "My World 2.0"),
            ("Colourblind.mp3", "Counting Crows", "Colorblind.mp3", "Colorblind", "Counting Crows", "This Desert Life"),
            ("Mr. Jones.mp3", "Counting Crows", "Mr. Jones.mp3", "Mr. Jones", "Counting Crows", "August and Everything After"),
            ("Europa.mp3", "Santana", "Europa.mp3", "Europa (Earth's Cry Heaven's Smile)", "Santana", "Amigos"),
            ("Hips Don't Lie.mp3", "Shakira", "Hips Don't Lie.mp3", "Hips Don't Lie", "Shakira & Wyclef Jean", "Oral Fixation, Vol. 2"),
            ("I Call It Love.mp3", "Lionel Richie", "I Call It Love.mp3", "I Call It Love", "Lionel Richie", "Coming Home"),
            ("I'd Love You To Want Me.mp3", "Lobo", "I'd Love You To Want Me.mp3", "I'd Love You To Want Me", "Lobo", "Of a Simple Man"),
            ("Love Stoned.mp3", "Justin Timberlake", "LoveStoned.mp3", "LoveStoned", "Justin Timberlake", "FutureSex/LoveSounds"),
            ("Somebody That I Used To Know.mp3", "Gotye", "Somebody That I Used To Know.mp3", "Somebody That I Used To Know", "Gotye & Kimbra", "Making Mirrors"),
            ("The Air Tonight Wtc Tribute.mp3", "Phil Collins", "In The Air Tonight.mp3", "In The Air Tonight", "Phil Collins", "Face Value"),
            ("The Dark Knight Theme Music.mp3", "Hans Zimmer", "Why So Serious.mp3", "Why So Serious?", "Hans Zimmer", "The Dark Knight"),
            ("The Ketchup Song.mp3", "Las Ketchup", "The Ketchup Song.mp3", "The Ketchup Song (Asereje)", "Las Ketchup", "Hijas del Tomate"),
            ("Tonight Feat. Ludacris.mp3", "Enrique Iglesias", "Tonight.mp3", "Tonight (I'm Lovin' You)", "Enrique Iglesias & Ludacris", "Euphoria"),
            ("Powerless.mp3", "Nelly Furtado", "Powerless.mp3", "Powerless (Say What You Want)", "Nelly Furtado", "Folklore"),
            ("Mother We Just Can't Get Enough.mp3", "New Radicals", "Mother We Just Can't Get Enough.mp3", "Mother We Just Can't Get Enough", "New Radicals", "Maybe You've Been Brainwashed Too"),
            ("One Headlight.mp3", "The Wallflowers", "One Headlight.mp3", "One Headlight", "The Wallflowers", "Bringing Down the Horse"),
            ("Standing Outside A Broken Phone Booth.mp3", "Primitive Radio Gods", "Standing Outside A Broken Phone Booth.mp3", "Standing Outside A Broken Phone Booth", "Primitive Radio Gods", "Rocket"),
        ]
        for old_name, art_folder, new_name, tit, art, alb in pr_mappings:
            src = os.path.join(pop_rock_dir, old_name)
            dst = os.path.join(english_root, art_folder, new_name)
            if os.path.exists(src):
                if safe_move(src, dst):
                    update_tags(dst, title=tit, artist=art, album=alb, genre="Pop/Rock")

    # ---------------------------------------------------------
    # 4. Sweep Empty Directories
    # ---------------------------------------------------------
    print("\n>>> 4. Sweeping Empty Directories...")
    deleted_count = 0
    for root, dirs, files in os.walk(ORGANIZED_ROOT, topdown=False):
        if root == ORGANIZED_ROOT:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
                print(f"[REMOVED EMPTY DIR] {root}")
                deleted_count += 1
            except Exception as e:
                print(f"Error removing {root}: {e}")
    print(f"Total empty directories deleted: {deleted_count}")

    print("\n" + "=" * 80)
    print("ARTIST-CENTRIC REORGANIZATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_artist_centric_reorganization()
