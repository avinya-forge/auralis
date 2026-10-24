import sys
sys.path.insert(0, '.')
import sqlite3
import json
import re
from collections import Counter

conn = sqlite3.connect('master_cross_drive_catalog.db')
c = conn.cursor()
c.execute("SELECT file_path, filename, file_size FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
fj_rows = c.fetchall()
conn.close()

def norm(s):
    if not s:
        return ""
    s = re.sub(r"\.[a-zA-Z0-9]+$", "", s)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps|ringtone|webrip)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return s

by_norm = {}
by_size = {}
for fp, fn, sz in fj_rows:
    by_size[sz] = fp
    n = norm(fn)
    if n and len(n) > 3:
        by_norm[n] = fp

# Known Bollywood Movie Track Catalog
BOLLYWOOD_TRACK_MAP = {
    "aaj purani rahon se": ("Soundtracks\\Aadmi", "Mohammed Rafi", "Aadmi"),
    "aaj socha to aansoo": ("Soundtracks\\Hanste Zakhm", "Mohammed Rafi", "Hanste Zakhm"),
    "betaab dil ki tamana": ("Soundtracks\\Hanste Zakhm", "Lata Mangeshkar", "Hanste Zakhm"),
    "aaj ki raat mere": ("Soundtracks\\Ram Aur Shyam", "Mohammed Rafi", "Ram Aur Shyam"),
    "aaj dil pe koi jor chalta": ("Soundtracks\\Milan", "Lata Mangeshkar", "Milan"),
    "aaja tujh ko pukare mera p": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "aaja tujh ko pukare mera pyar": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "mere mitwa": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "aap ki nazron ne samjha": ("Soundtracks\\Anpadh", "Lata Mangeshkar", "Anpadh"),
    "aap ke pahloo mein aa kar": ("Soundtracks\\Mera Saaya", "Mohammed Rafi", "Mera Saaya"),
    "aap jaisa koi": ("Soundtracks\\Qurbani", "Nazia Hassan", "Qurbani"),
    "aankhon ki masti": ("Soundtracks\\Umrao Jaan", "Asha Bhosle", "Umrao Jaan"),
    "aane wala pal": ("Soundtracks\\Golmaal", "Kishore Kumar", "Golmaal"),
    "na tum jano na hum": ("Soundtracks\\Kaho Naa Pyaar Hai", "Lucky Ali", "Kaho Naa Pyaar Hai"),
    "aapki aankhon mein": ("Soundtracks\\Ghar", "Kishore Kumar", "Ghar"),
    "aaya re khilone wala": ("Soundtracks\\Bachpan", "Mohammed Rafi", "Bachpan"),
    "aaye din baharke mere du": ("Soundtracks\\Aaye Din Bahar Ke", "Mohammed Rafi", "Aaye Din Bahar Ke"),
    "aaye jate hue lamhe": ("Soundtracks\\Border", "Roop Kumar Rathod", "Border"),
    "ae kassh ke hum": ("Soundtracks\\Kabhi Haan Kabhi Naa", "Kumar Sanu", "Kabhi Haan Kabhi Naa"),
    "ae nazneen suno na": ("Soundtracks\\Dil Hi Dil Mein", "Abhijeet", "Dil Hi Dil Mein"),
    "ae nazneen suno": ("Soundtracks\\Dil Hi Dil Mein", "Abhijeet", "Dil Hi Dil Mein"),
    "aise na mujhe tum dekho": ("Soundtracks\\Darling Darling", "Kishore Kumar", "Darling Darling"),
    "aise na mujhe tum": ("Soundtracks\\Darling Darling", "Kishore Kumar", "Darling Darling"),
    "ajeeb dastaan hain y": ("Soundtracks\\Dil Apna Aur Preet Parai", "Lata Mangeshkar", "Dil Apna Aur Preet Parai"),
    "ajeeb dastan": ("Soundtracks\\Dil Apna Aur Preet Parai", "Lata Mangeshkar", "Dil Apna Aur Preet Parai"),
    "alag alagdil mein aag la": ("Soundtracks\\Alag Alag", "Kishore Kumar", "Alag Alag"),
    "alagdil mein aag la": ("Soundtracks\\Alag Alag", "Kishore Kumar", "Alag Alag"),
    "bas ik sanam": ("Soundtracks\\Aashiqui", "Kumar Sanu", "Aashiqui"),
    "bas ek sanam": ("Soundtracks\\Aashiqui", "Kumar Sanu", "Aashiqui"),
    "why this kolaveri di": ("Soundtracks\\3", "Dhanush", "3"),
    "movie why this kolaveri di": ("Soundtracks\\3", "Dhanush", "3"),
    "bhari duniya mein aakhir": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "bheegi bheegi": ("Soundtracks\\Gangster", "James", "Gangster"),
    "bhooli bisri yaadon main": ("Soundtracks\\Sanjog", "Mukesh", "Sanjog"),
    "bin tere sanam": ("Soundtracks\\Yaara Dildara", "Udit Narayan", "Yaara Dildara"),
    "chakde phattey": ("Soundtracks\\Khosla Ka Ghosla", "Kailash Kher", "Khosla Ka Ghosla"),
    "chhod aaye hum woh galiyan": ("Soundtracks\\Maachis", "Hariharan", "Maachis"),
    "chalte chalte yun hi koi": ("Soundtracks\\Pakeezah", "Ghulam Mohammed", "Pakeezah"),
    "chalte chalte": ("Soundtracks\\Chalte Chalte", "Kishore Kumar", "Chalte Chalte"),
    "chaudhavin ka chandmili": ("Soundtracks\\Chaudhvin Ka Chand", "Mohammed Rafi", "Chaudhvin Ka Chand"),
    "chhookar mere man ko": ("Soundtracks\\Yaraana", "Kishore Kumar", "Yaraana"),
    "choo kar mere man ko": ("Soundtracks\\Yaraana", "Kishore Kumar", "Yaraana"),
    "chupke chupke raat din": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "chahunga main tujhe": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "chal ud jare panchi": ("Soundtracks\\Bhabhi", "Mohammed Rafi", "Bhabhi"),
    "chal udja re panchi bhabh": ("Soundtracks\\Bhabhi", "Mohammed Rafi", "Bhabhi"),
    "chale aaj tum jahan se": ("Soundtracks\\Uran Khatola", "Mohammed Rafi", "Uran Khatola"),
    "taqdeer ka fasana": ("Soundtracks\\Sehra", "Mohammed Rafi", "Sehra"),
    "awara bhanwere": ("Soundtracks\\Sapnay", "Hema Sardesai", "Sapnay"),
    "aye bekhabar": ("Soundtracks\\Zeher", "KK", "Zeher"),
    "aakhen bhi hoti hai dil ki juba": ("Soundtracks\\Haasil", "Alka Yagnik", "Haasil"),
    "aakhri geet mohobbat ka": ("Soundtracks\\Neela Aakash", "Mohammed Rafi", "Neela Aakash"),
    "aaja soniye": ("Soundtracks\\Mujhse Shaadi Karogi", "Sonu Nigam", "Mujhse Shaadi Karogi"),
    "apni to": ("Soundtracks\\Laawaris", "Kishore Kumar", "Laawaris"),
}

# Known Non-Film Hindi Albums
HINDI_ALBUMS_MAP = {
    "breathless full": ("Albums\\Breathless", "Shankar Mahadevan", "Breathless"),
    "breathless": ("Albums\\Breathless", "Shankar Mahadevan", "Breathless"),
    "bandeh": ("Albums\\Indian Ocean", "Indian Ocean", "Kandisa"),
    "bandeh msg": ("Albums\\Indian Ocean", "Indian Ocean", "Kandisa"),
    "bikra hoon main": ("Albums\\Jal", "Jal", "Aadat"),
    "abhijeet savant": ("Albums\\Abhijeet Sawant", "Abhijeet Sawant", "Aapka Abhijeet Sawant"),
    "aai jo teri yaad": ("Albums\\Aai Jo Teri Yaad", "Pankaj Udhas", "Aai Jo Teri Yaad"),
    "aaj jaane ki zid na karo": ("Ghazals\\Farida Khanum", "Farida Khanum", "Ghazals"),
}

# Known Devotional / Anup Jalota Bhajans
ANUP_JALOTA_TRACKS = [
    "aisi lagi lagan", "chadariya jhini re jhini", "chahe bansi bajaiya bolo",
    "chalo man ganga jamuna teer", "ab ki tek hamari murari", "aaj radhika bano",
    "bhakto apne mukh se"
]

# Known Marathi Classics
MARATHI_TRACKS_MAP = {
    "aabhas ha": ("Marathi", "Soundtracks\\Yanda Kartavya Aahe", "Swapnil Bandodkar", "Yanda Kartavya Aahe"),
    "aaj gokulat rang": ("Marathi", "Bhavgeet & Classics", "Lata Mangeshkar", "Bhavgeet"),
    "aaji soniyacha dinu": ("Marathi", "Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwar Mauli"),
    "aakashi zep ghe re pakhara": ("Marathi", "Sudhir Phadke", "Sudhir Phadke", "Aamhi Jato Aamchya Gava"),
    "aala aala paus aala": ("Marathi", "Balgeet", "Various Artists", "Balgeet"),
    "aala aala vara": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "aala aala vara inh109850150": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "aali thumkat naar lachkat": ("Marathi", "Lavani & Folk", "Various Artists", "Lavani"),
    "aamchimatiaamchimanasa000": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Doordarshan"),
    "ae aai mala pawasat jau dena": ("Marathi", "Balgeet", "Various Artists", "Balgeet"),
    "aika satyanarayanachi": ("Marathi", "Abhang & Bhakti", "Various Artists", "Satyanarayan"),
    "airanichya deva tula inh100336290": ("Marathi", "Lata Mangeshkar", "Lata Mangeshkar", "Sadhi Manasa"),
    "amrutahooni god": ("Marathi", "Abhang & Bhakti", "Bhimsen Joshi", "Abhang"),
    "are are dnyana zalasi pavan": ("Marathi", "Abhang & Bhakti", "Various Artists", "Abhang"),
    "asava sundar chockletcha bungla": ("Marathi", "Balgeet", "Various Artists", "Balgeet"),
    "ashtavinayaka": ("Marathi", "Abhang & Bhakti", "Various Artists", "Ashtavinayak"),
    "avachita parimalu": ("Marathi", "Abhang & Bhakti", "Lata Mangeshkar", "Abhang"),
    "bai bai manmoracha inh100336200": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "bai mi vikat ghetala shyam": ("Marathi", "Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "bala bhaktalagi": ("Marathi", "Abhang & Bhakti", "Various Artists", "Abhang"),
    "bhatukalichya khela madhali": ("Marathi", "Arun Date", "Arun Date", "Bhavgeet"),
    "bugadi mazi sandali inh100154530": ("Marathi", "Lavani & Folk", "Lata Mangeshkar", "Pinjara"),
    "caidra bhage paindhari": ("Marathi", "Abhang & Bhakti", "Various Artists", "Vitthal Bhakti"),
    "chal ga sakhe": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chal sadhaka": ("Marathi", "Abhang & Bhakti", "Various Artists", "Bhakti"),
    "chandane shimpit jashi": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chandanyat phirtana": ("Marathi", "Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chandra bhagechya tiri": ("Marathi", "Abhang & Bhakti", "Various Artists", "Vitthal Bhakti"),
    "chhabidar chhabi mi": ("Marathi", "Lavani & Folk", "Various Artists", "Lavani"),
    "dhund hote shbd sare": ("Marathi", "Saleel Kulkarni", "Saleel Kulkarni", "Ayushyavar Bolu Kahi"),
}

# Known English Tracks & Soundtracks
ENGLISH_TRACKS_MAP = {
    "a beautiful mind": ("English", "Soundtracks\\A Beautiful Mind", "James Horner", "A Beautiful Mind"),
    "all i want is you": ("English", "U2", "U2", "Rattle and Hum"),
    "batman beyond": ("English", "Soundtracks\\Batman", "The Crystal Method", "Batman Beyond"),
    "batman theme": ("English", "Soundtracks\\Batman", "Danny Elfman", "Batman"),
    "comfotably numb lead": ("English", "Pink Floyd", "Pink Floyd", "The Wall"),
    "creep acoustic": ("English", "Radiohead", "Radiohead", "Pablo Honey"),
    "coma black": ("English", "Marilyn Manson", "Marilyn Manson", "Holy Wood"),
    "burn hell": ("English", "Marilyn Manson", "Marilyn Manson", "Holy Wood"),
    "celine dion": ("English", "Celine Dion", "Celine Dion", "Celine Dion Hits"),
    "the wailers so much trouble the world": ("English", "Bob Marley", "Bob Marley & The Wailers", "Survival"),
    "coming from the cold": ("English", "Bob Marley", "Bob Marley & The Wailers", "Uprising"),
    "crazy baldheads": ("English", "Bob Marley", "Bob Marley & The Wailers", "Rastaman Vibration"),
}

# Ringtones / Alerts / Sound Effects
RINGTONE_TRIGGERS = [
    "alarm", "alien phone", "angrycat", "airtel", "arabic ringtone", "ardour", "austin",
    "bacardi blast", "business cell tone", "captain planet", "cartoon", "casino royale",
    "counter strike", "cuppy cake", "d 6", "best guitar", "coinsound", "chic", "ak 47",
    "aaaa", "974 5554341", "but it rained solo", "but it rained start", "c b t l"
]

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Testing comprehensive resolution on {len(eg)} Evergreen tracks:")
res_categories = Counter()

for t in eg:
    fn = t['filename']
    n = norm(fn)
    dur = t.get('duration', 0)
    
    # 1. Friends Soundtrack CD1 / CD2 check
    if re.search(r"\bcd[12]\s*track\d+\b", n):
        res_categories["English: Soundtracks\\Friends - The Ultimate Soundtrack"] += 1
        continue
        
    # 2. Ringtones & Alerts
    if any(rt in n for rt in RINGTONE_TRIGGERS) or (dur > 0 and dur < 40 and "mp3" in fn.lower()):
        res_categories["Ringtones: Ringtones & Alerts"] += 1
        continue
        
    # 3. Known Marathi
    if n in MARATHI_TRACKS_MAP:
        info = MARATHI_TRACKS_MAP[n]
        res_categories[f"Marathi: {info[1]}"] += 1
        continue
        
    # 4. Known Devotional / Anup Jalota
    if any(aj in n for aj in ANUP_JALOTA_TRACKS) or "anup jalota" in t.get('tag_artist', '').lower():
        res_categories["Hindi: Devotional & Bhajans\\Anup Jalota"] += 1
        continue
        
    # 5. Known Non-film Hindi Albums
    if n in HINDI_ALBUMS_MAP:
        info = HINDI_ALBUMS_MAP[n]
        res_categories[f"Hindi: {info[0]}"] += 1
        continue
        
    # 6. Known English Bands & Soundtracks
    if n in ENGLISH_TRACKS_MAP:
        info = ENGLISH_TRACKS_MAP[n]
        res_categories[f"English: {info[1]}"] += 1
        continue
        
    # 7. Known Bollywood Movies
    if n in BOLLYWOOD_TRACK_MAP:
        info = BOLLYWOOD_TRACK_MAP[n]
        res_categories[f"Hindi: {info[0]}"] += 1
        continue
        
    # 8. Check Catalog Normalized Match
    cat_path = by_norm.get(n)
    if cat_path:
        p_lower = cat_path.lower()
        if "ringtone" in p_lower:
            res_categories["Ringtones: Ringtones & Alerts"] += 1
        elif "marathi" in p_lower:
            res_categories["Marathi: Bhavgeet & Classics"] += 1
        elif "vidik" in p_lower or "sanskrit" in p_lower:
            res_categories["Sanskrit: Vedic Suktas"] += 1
        elif "pravachan" in p_lower:
            res_categories["Pravachan: Discourses"] += 1
        elif "old movies" in p_lower:
            res_categories["Hindi: Classic Soundtracks"] += 1
        elif "new" in p_lower:
            res_categories["Hindi: Modern Soundtracks"] += 1
        else:
            res_categories["Catalog Match: Other"] += 1
        continue

    res_categories["Remaining Evergreen"] += 1

print("\nResolution breakdown of 1091 tracks:")
for k, v in res_categories.most_common(25):
    print(f"  {k}: {v} tracks")

resolved = len(eg) - res_categories["Remaining Evergreen"]
print(f"\nTotal newly resolved: {resolved} / {len(eg)} ({resolved*100.0/len(eg):.1f}%)")
print(f"Remaining in generic bucket: {res_categories['Remaining Evergreen']}")
