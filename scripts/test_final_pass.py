import sys
sys.path.insert(0, '.')
import json
import re

data = json.load(open('cached_dry_run_results.json', encoding='utf-8'))['tracks']
eg = [v for v in data if not v.get('is_duplicate') and v.get('language') == 'Hindi' and v.get('category') == 'Evergreen Classics']

print(f"Total Evergreen to test: {len(eg)}")

# Additional Bollywood
NEW_BOLLYWOOD = {
    "dil to hai dil": "Muqaddar Ka Sikandar",
    "do pal": "Veer-Zaara",
    "do ghoont maine pee": "Jheel Ke Us Paar",
    "dosti mera to jo bhi kad": "Dosti",
    "dulari suhani raat dhal": "Dulari",
    "ek ajnabee hasina se": "Ajanabee",
    "ek haseen nigah ka mayamemsaab": "Maya Memsaab",
    "hawas teri galiyon mein": "Hawas",
    "hoton pe aisi baat": "Jewel Thief",
    "hui shaam uka khayal": "Mere Hamdam Mere Dost",
    "hum hai mataye kuncha": "Dastak",
    "hum pyar mein jalne walon ko": "Jailor",
    "insaaf ka mandir hai yeh": "Amar",
    "jaata hai tu kahan": "Yes Boss",
    "jabbhikoihaseenaherapheri": "Hera Pheri",
    "jiska joi nahi": "Laawaris",
    "jo unki tamanna": "Intaqam",
    "ka chandmili": "Chaudhvin Ka Chand",
    "kailash kher khosla": "Khosla Ka Ghosla",
    "keh doon tumhen": "Deewaar",
    "kehna hi kya": "Bombay",
    "khali haath shaam aayi hai ijazzat": "Ijaazat",
    "khilona jaankar": "Khilona",
    "khiza ke phool bhi": "Do Raaste",
    "kya hua tera waada": "Hum Kisise Kum Naheen",
    "kya se kya ho gaya": "Guide",
    "laal qilla na kisi ki aa": "Lal Quila",
    "lajja": "Lajja",
    "maheboob ki mehandi apna": "Mehboob Ki Mehndi",
    "main ka karoo ram": "Sangam",
    "mausam hai ashiqana": "Pakeezah",
    "mili khak mein mohabbat": "Chaudhvin Ka Chand",
    "mohabbat ki jhoothi": "Mughal-E-Azam",
    "mohobbat aesi dhadkan": "Anarkali",
    "mujhe dard e dil ka pata": "Aakash Deep",
    "mujhe duniya walo sharabi na samjho": "Leader",
    "mujhe raat din": "Sangharsh",
    "mujhe teri mohobat ka": "Aap Aye Bahaar Ayee",
    "mumbhai": "Bombay Boys",
    "nafrat ki duniya ko": "Haathi Mere Saathi",
    "neele neele ambar par": "Kalaakaar",
    "nile nile amber par": "Kalaakaar",
    "o duniya ke rakhwale": "Baiju Bawra",
    "paise ki pehchan": "Pehchan",
    "pankhon ko": "Rocket Singh: Salesman of the Year",
    "peene walon suno": "Dushman",
    "phir teri kahani yaad aayi": "Dil Diya Dard Liya",
    "pyar ki jeet ek dil ke t": "Pyar Ki Jeet",
    "raahi manwa dukh ki": "Dosti",
    "raat ke andhere main aga": "Raat Aur Din",
    "rahte the kabhi jinke dil": "Mamta",
    "rozana": "Naam Shabana",
    "sathiya": "Saathiya",
    "sau baar janam lenge": "Ustadon Ke Ustad",
    "tum mujhe yun bhulan na paoge": "Pagla Kahin Ka",
    "tumse milke aisa laga": "Parinda",
    "yaad na jaaye": "Dil Ek Mandir",
    "yaar bina chain kahan": "Saaheb",
    "yahan main ajnabee hoon": "Jab Jab Phool Khile",
    "ye raate nayi purani": "Julie",
    "yeh aansoo mere dil ki zub": "Humrahi",
    "yeh dil tum bin kahin lagt": "Izzat",
    "chaand taare": "Yes Boss",
    "dil dance maare": "Tashan",
    "ek din teri raahon": "Naqaab",
    "fitna dil": "Aap Kaa Surroor",
    "jao na": "What's Your Raashee?",
    "rukruk": "Vijaypath",
    "saiyaan re": "Salaam-E-Ishq",
    "socha nahin tha": "Socha Na Tha",
    "tuaashiqehai": "Jhankaar Beats",
    "sunona": "Jhankaar Beats",
    "zaraza": "Jannat"
}

# Additional Marathi
NEW_MARATHI = [
    "disala ga bai", "disala ga baee", "dole kashasathi", "dur rahuni", "erneechya deva",
    "garva", "gele dyayache", "ghanu waje", "gomu sangatina", "gori gori pan", "ha khel savalyancha",
    "haat tujha", "hawas maj tu", "hi pournima", "hi vaat dur", "indrachi kamini", "ishqachi ingali",
    "jambul pikalya", "jeevani adhar", "jevhaan tichi", "jiv rangala", "jivalaga rahile", "ka re durava",
    "kajal ratina", "kalpanecha kunchala", "kashi nashibana", "kay bai sangu", "kevhan tari",
    "koli geet", "konas thauk", "kunya gavacha", "kutha kutha jayacha", "latpat latpat", "lek ladki",
    "magate man", "majhya dadala", "mala lagali", "mana manav", "mazya kapalicha", "mee maj harpun",
    "mi kashala", "mogara phulala", "naadatuniya naad", "naka toodu", "nako devaraya", "nilya ga dolyanchya",
    "om namoji adhya", "pail to ge kaau", "phulanche phool", "premachnahi", "pustak nantar", "ranga yei",
    "rani bole", "runu zunu", "ruperi valut", "saang saang bholanath", "samaichya shubhra",
    "santha wahate krishnamai", "sharad sundar", "shodhisi manawa", "shukratara mandwara",
    "sonuli mazi", "sukha karta", "sur magu tula", "swapnatalya kalyonno", "tarun aahe ratra",
    "thakale re nandlala", "tumhavar keli", "tumhawar keli", "tuzi mazi preet", "vaara gaai",
    "vat pahun nayan", "vishwache aart", "ya janmawar", "ye re ghana", "ye re ye re pawasa",
    "yeu kashi priya", "zalya tinhisanja"
]

resolved = 0
for t in eg:
    fn = t['filename'].lower()
    tit = t.get('tag_title', '').lower()
    
    # Sanskrit Devanagari
    if any(sk in fn for sk in ["देव्या", "कवच", "कीलकम्", "अर्गला", "कुंजिका", "कुञ्चिका", "संथा", "स्तोत्र"]):
        resolved += 1
        continue
        
    # Marathi ISRC
    if re.search(r"\binh\d+", fn) or re.search(r"\binh\d+", t.get('tag_artist', '').lower()):
        resolved += 1
        continue
        
    # When Chai Met Toast
    if "when chai met toast" in fn:
        resolved += 1
        continue
        
    # Marathi
    if any(m in fn or m in tit for m in NEW_MARATHI):
        resolved += 1
        continue
        
    # Bollywood
    if any(k in fn or k in tit for k in NEW_BOLLYWOOD):
        resolved += 1
        continue

print(f"Newly resolved from 359 Evergreen tracks: {resolved} / {len(eg)} ({resolved*100.0/len(eg):.1f}%)")
print(f"Remaining after this pass: {len(eg) - resolved}")
