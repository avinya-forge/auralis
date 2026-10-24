"""
Auralis - Catalog-Backed Taxonomy Resolver
Provides instantaneous, deterministic ground-truth lookup for original track locations,
soundtrack movies, non-film albums, and legendary artists across all drives.
"""

import sqlite3
import os
import re
from typing import Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "master_cross_drive_catalog.db")

CULTURAL_NUMBERED_TITLES = {
    "1942 a love story": "1942 A Love Story",
    "1947 earth": "1947 Earth",
    "3 idiots": "3 Idiots",
    "3 movie": "3",
    "taxi no 9211": "Taxi No 9211",
    "shree 420": "Shree 420",
    "420": "Shree 420",
    "u2": "U2",
    "blink 182": "Blink 182",
    "sum 41": "Sum 41",
    "3 doors down": "3 Doors Down"
}

# --------------------------------------------------------------------------
# Curated Ground-Truth Maps for Classic Hindi, Marathi, Ghazals, & English
# --------------------------------------------------------------------------

BOLLYWOOD_TRACK_MAP = {
    "aaj purani rahon se": ("Soundtracks\\Aadmi", "Mohammed Rafi", "Aadmi"),
    "aaj socha to aansoo": ("Soundtracks\\Hanste Zakhm", "Mohammed Rafi", "Hanste Zakhm"),
    "aaj socha to aansoo bhar": ("Soundtracks\\Hanste Zakhm", "Mohammed Rafi", "Hanste Zakhm"),
    "betaab dil ki tamana": ("Soundtracks\\Hanste Zakhm", "Lata Mangeshkar", "Hanste Zakhm"),
    "aaj ki raat mere": ("Soundtracks\\Ram Aur Shyam", "Mohammed Rafi", "Ram Aur Shyam"),
    "aaj dil pe koi jor chalta": ("Soundtracks\\Milan", "Lata Mangeshkar", "Milan"),
    "ham tum yug yug se": ("Soundtracks\\Milan", "Mukesh", "Milan"),
    "aaja tujh ko pukare mera p": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "aaja tujh ko pukare mera pyar": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "mere mitwa": ("Soundtracks\\Geet", "Mohammed Rafi", "Geet"),
    "aap ki nazron ne samjha": ("Soundtracks\\Anpadh", "Lata Mangeshkar", "Anpadh"),
    "aap ke pahloo mein aa kar": ("Soundtracks\\Mera Saaya", "Mohammed Rafi", "Mera Saaya"),
    "tu jahan jahan chalega": ("Soundtracks\\Mera Saaya", "Lata Mangeshkar", "Mera Saaya"),
    "jhumka gira re": ("Soundtracks\\Mera Saaya", "Asha Bhosle", "Mera Saaya"),
    "aap jaisa koi": ("Soundtracks\\Qurbani", "Nazia Hassan", "Qurbani"),
    "aankhon ki masti": ("Soundtracks\\Umrao Jaan", "Asha Bhosle", "Umrao Jaan"),
    "in aankhon ki masti": ("Soundtracks\\Umrao Jaan", "Asha Bhosle", "Umrao Jaan"),
    "dil cheez kya hai": ("Soundtracks\\Umrao Jaan", "Asha Bhosle", "Umrao Jaan"),
    "aane wala pal": ("Soundtracks\\Golmaal", "Kishore Kumar", "Golmaal"),
    "na tum jano na hum": ("Soundtracks\\Kaho Naa Pyaar Hai", "Lucky Ali", "Kaho Naa Pyaar Hai"),
    "aapki aankhon mein": ("Soundtracks\\Ghar", "Kishore Kumar", "Ghar"),
    "tere bina jiya jaye na": ("Soundtracks\\Ghar", "Lata Mangeshkar", "Ghar"),
    "aaya re khilone wala": ("Soundtracks\\Bachpan", "Mohammed Rafi", "Bachpan"),
    "aaye din baharke mere du": ("Soundtracks\\Aaye Din Bahar Ke", "Mohammed Rafi", "Aaye Din Bahar Ke"),
    "aaye din bahar ke": ("Soundtracks\\Aaye Din Bahar Ke", "Mohammed Rafi", "Aaye Din Bahar Ke"),
    "aaye jate hue lamhe": ("Soundtracks\\Border", "Roop Kumar Rathod", "Border"),
    "sandese aate hai": ("Soundtracks\\Border", "Sonu Nigam", "Border"),
    "ae kassh ke hum": ("Soundtracks\\Kabhi Haan Kabhi Naa", "Kumar Sanu", "Kabhi Haan Kabhi Naa"),
    "ae kash ke hum": ("Soundtracks\\Kabhi Haan Kabhi Naa", "Kumar Sanu", "Kabhi Haan Kabhi Naa"),
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
    "ya ali": ("Soundtracks\\Gangster", "Zubeen Garg", "Gangster"),
    "bhooli bisri yaadon main": ("Soundtracks\\Sanjog", "Mukesh", "Sanjog"),
    "bin tere sanam": ("Soundtracks\\Yaara Dildara", "Udit Narayan", "Yaara Dildara"),
    "chakde phattey": ("Soundtracks\\Khosla Ka Ghosla", "Kailash Kher", "Khosla Ka Ghosla"),
    "chhod aaye hum woh galiyan": ("Soundtracks\\Maachis", "Hariharan", "Maachis"),
    "chalte chalte yun hi koi": ("Soundtracks\\Pakeezah", "Ghulam Mohammed", "Pakeezah"),
    "chalte chalte": ("Soundtracks\\Chalte Chalte", "Kishore Kumar", "Chalte Chalte"),
    "chaudhavin ka chandmili": ("Soundtracks\\Chaudhvin Ka Chand", "Mohammed Rafi", "Chaudhvin Ka Chand"),
    "chhookar mere man ko": ("Soundtracks\\Yaraana", "Kishore Kumar", "Yaraana"),
    "choo kar mere man ko": ("Soundtracks\\Yaraana", "Kishore Kumar", "Yaraana"),
    "chahunga main tujhe": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "mera to jo bhi kadam": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "chal ud jare panchi": ("Soundtracks\\Bhabhi", "Mohammed Rafi", "Bhabhi"),
    "chal udja re panchi bhabh": ("Soundtracks\\Bhabhi", "Mohammed Rafi", "Bhabhi"),
    "chale aaj tum jahan se": ("Soundtracks\\Uran Khatola", "Mohammed Rafi", "Uran Khatola"),
    "khatola chale aaj t": ("Soundtracks\\Uran Khatola", "Mohammed Rafi", "Uran Khatola"),
    "taqdeer ka fasana": ("Soundtracks\\Sehra", "Mohammed Rafi", "Sehra"),
    "awara bhanwere": ("Soundtracks\\Sapnay", "Hema Sardesai", "Sapnay"),
    "aye bekhabar": ("Soundtracks\\Zeher", "KK", "Zeher"),
    "aakhen bhi hoti hai dil ki juba": ("Soundtracks\\Haasil", "Alka Yagnik", "Haasil"),
    "aakhri geet mohobbat ka": ("Soundtracks\\Neela Aakash", "Mohammed Rafi", "Neela Aakash"),
    "aaja soniye": ("Soundtracks\\Mujhse Shaadi Karogi", "Sonu Nigam", "Mujhse Shaadi Karogi"),
    "apni to": ("Soundtracks\\Laawaris", "Kishore Kumar", "Laawaris"),
    "apni to jaise taise": ("Soundtracks\\Laawaris", "Kishore Kumar", "Laawaris"),
    "gaata rahe mera dil": ("Soundtracks\\Guide", "Kishore Kumar", "Guide"),
    "din dhal jaaye": ("Soundtracks\\Guide", "Mohammed Rafi", "Guide"),
    "tere mere sapne": ("Soundtracks\\Guide", "Mohammed Rafi", "Guide"),
    "diye jalte hai kishor kumar": ("Soundtracks\\Namak Haraam", "Kishore Kumar", "Namak Haraam"),
    "diye jalte hai": ("Soundtracks\\Namak Haraam", "Kishore Kumar", "Namak Haraam"),
    "dil kya kare jab": ("Soundtracks\\Julie", "Kishore Kumar", "Julie"),
    "dil kya kare": ("Soundtracks\\Julie", "Kishore Kumar", "Julie"),
    "dilbar mere kab tak": ("Soundtracks\\Satte Pe Satta", "Kishore Kumar", "Satte Pe Satta"),
    "do labzo ki hai": ("Soundtracks\\The Great Gambler", "Asha Bhosle", "The Great Gambler"),
    "duniya hasino ka mela": ("Soundtracks\\Gupt", "Udit Narayan", "Gupt"),
    "ek mandir yaad na ja": ("Soundtracks\\Dil Ek Mandir", "Mohammed Rafi", "Dil Ek Mandir"),
    "dil ek mandir hai": ("Soundtracks\\Dil Ek Mandir", "Mohammed Rafi", "Dil Ek Mandir"),
    "yaad na jaye": ("Soundtracks\\Dil Ek Mandir", "Mohammed Rafi", "Dil Ek Mandir"),
    "ham to chale pard": ("Soundtracks\\Sargam", "Mohammed Rafi", "Sargam"),
    "haule haule": ("Soundtracks\\Rab Ne Bana Di Jodi", "Sukhwinder Singh", "Rab Ne Bana Di Jodi"),
    "ho gaya hai tujhko to pyar sajana": ("Soundtracks\\Dilwale Dulhania Le Jayenge", "Udit Narayan", "Dilwale Dulhania Le Jayenge"),
    "mere khabo mein tu": ("Soundtracks\\Dilwale Dulhania Le Jayenge", "Lata Mangeshkar", "Dilwale Dulhania Le Jayenge"),
    "humdum mere dost hu": ("Soundtracks\\Mere Humdum Mere Dost", "Mohammed Rafi", "Mere Humdum Mere Dost"),
    "jab phool khile yanh": ("Soundtracks\\Jab Phool Khile", "Mohammed Rafi", "Jab Phool Khile"),
    "jara si aahat hoti": ("Soundtracks\\Haqeeqat", "Lata Mangeshkar", "Haqeeqat"),
    "jodhaa akbar": ("Soundtracks\\Jodhaa Akbar", "A.R. Rahman", "Jodhaa Akbar"),
    "khilte hain gul": ("Soundtracks\\Sharmilee", "Kishore Kumar", "Sharmilee"),
    "main agar kahoo": ("Soundtracks\\Om Shanti Om", "Sonu Nigam", "Om Shanti Om"),
    "main yeh sochkar ke dar se": ("Soundtracks\\Haqeeqat", "Mohammed Rafi", "Haqeeqat"),
    "maine puchha": ("Soundtracks\\Katha", "Asha Bhosle", "Katha"),
    "majnutere dar pe a": ("Soundtracks\\Laila Majnu", "Mohammed Rafi", "Laila Majnu"),
    "mere jeevan saathi": ("Soundtracks\\Mere Jeevan Saathi", "Kishore Kumar", "Mere Jeevan Saathi"),
    "mere jivan sathi": ("Soundtracks\\Mere Jeevan Saathi", "Kishore Kumar", "Mere Jeevan Saathi"),
    "mere saathi nafar": ("Soundtracks\\Haathi Mere Saathi", "Kishore Kumar", "Haathi Mere Saathi"),
    "mohabbat ke suha": ("Soundtracks\\Maryada", "Mohammed Rafi", "Maryada"),
    "mr x bombay mere ma": ("Soundtracks\\Mr. X In Bombay", "Kishore Kumar", "Mr. X In Bombay"),
    "musafirhoonyaaron": ("Soundtracks\\Parichay", "Kishore Kumar", "Parichay"),
    "musafir hoon yaaron": ("Soundtracks\\Parichay", "Kishore Kumar", "Parichay"),
    "na kajare ki dhar": ("Soundtracks\\Mohra", "Pankaj Udhas", "Mohra"),
    "na tu zameen": ("Soundtracks\\Dastaan", "Mohammed Rafi", "Dastaan"),
    "neela aasman": ("Soundtracks\\Silsila", "Amitabh Bachchan", "Silsila"),
    "dekha ek khwab to": ("Soundtracks\\Silsila", "Kishore Kumar", "Silsila"),
    "pal pal dil ke pass": ("Soundtracks\\Blackmail", "Kishore Kumar", "Blackmail"),
    "panchhi banoo udti phiroo": ("Soundtracks\\Chori Chori", "Lata Mangeshkar", "Chori Chori"),
    "aaja sanam madhur chandni": ("Soundtracks\\Chori Chori", "Manna Dey", "Chori Chori"),
    "patta patta butta butta": ("Soundtracks\\Ek Nazar", "Mohammed Rafi", "Ek Nazar"),
    "piya bina": ("Soundtracks\\Abhimaan", "Lata Mangeshkar", "Abhimaan"),
    "tere mere milan ki yeh": ("Soundtracks\\Abhimaan", "Kishore Kumar", "Abhimaan"),
    "pyar ka mausam": ("Soundtracks\\Pyar Ka Mausam", "Mohammed Rafi", "Pyar Ka Mausam"),
    "raat kali ik khwab mein": ("Soundtracks\\Buddha Mil Gaya", "Kishore Kumar", "Buddha Mil Gaya"),
    "raat kali ik khwab mein07": ("Soundtracks\\Buddha Mil Gaya", "Kishore Kumar", "Buddha Mil Gaya"),
    "rahen na rahe hum maheka": ("Soundtracks\\Mamta", "Lata Mangeshkar", "Mamta"),
    "rahen na rahe hum": ("Soundtracks\\Mamta", "Lata Mangeshkar", "Mamta"),
    "raina beti jaaye": ("Soundtracks\\Amar Prem", "Lata Mangeshkar", "Amar Prem"),
    "chingari koi bhadke": ("Soundtracks\\Amar Prem", "Kishore Kumar", "Amar Prem"),
    "kuch to log kahenge": ("Soundtracks\\Amar Prem", "Kishore Kumar", "Amar Prem"),
    "saya aap ke pahlu m": ("Soundtracks\\Mera Saaya", "Mohammed Rafi", "Mera Saaya"),
    "subah na aayi shaam na aay": ("Soundtracks\\Cha Cha Cha", "Mohammed Rafi", "Cha Cha Cha"),
    "tera mujh se hai": ("Soundtracks\\Aa Gale Lag Jaa", "Kishore Kumar", "Aa Gale Lag Jaa"),
    "tere bina zindagi se": ("Soundtracks\\Aandhi", "Kishore Kumar", "Aandhi"),
    "thodisi bewafai": ("Soundtracks\\Thodisi Bewafai", "Kishore Kumar", "Thodisi Bewafai"),
    "toote hue khwa": ("Soundtracks\\Madhumati", "Mohammed Rafi", "Madhumati"),
    "tum ko hamari umar lag ja": ("Soundtracks\\Ayee Milan Ki Bela", "Mohammed Rafi", "Ayee Milan Ki Bela"),
    "tum saath ho jab apne": ("Soundtracks\\Kaalia", "Kishore Kumar", "Kaalia"),
    "dil ke arman ansuon mein": ("Soundtracks\\Nikaah", "Salma Agha", "Nikaah"),
    "dheere dheere machal": ("Soundtracks\\Anupama", "Lata Mangeshkar", "Anupama"),
    "kuchh dil ne kaha": ("Soundtracks\\Anupama", "Lata Mangeshkar", "Anupama"),
    "ya dil ki suno": ("Soundtracks\\Anupama", "Hemant Kumar", "Anupama"),
    "nagri nagri dware dware": ("Soundtracks\\Mother India", "Lata Mangeshkar", "Mother India"),
    "dukh bhare din beete re bhaiyya": ("Soundtracks\\Mother India", "Mohammed Rafi", "Mother India"),
    "duniya manin hum aaye hain to": ("Soundtracks\\Mother India", "Lata Mangeshkar", "Mother India"),
    "tere pyar ka aasra": ("Soundtracks\\Dhool Ka Phool", "Mahendra Kapoor", "Dhool Ka Phool"),
    "jo tum muskurado": ("Soundtracks\\Dhool Ka Phool", "Mohammed Rafi", "Dhool Ka Phool"),
    "mere mehboob tujhe": ("Soundtracks\\Mere Mehboob", "Mohammed Rafi", "Mere Mehboob"),
    "tere pyar mein dildar": ("Soundtracks\\Mere Mehboob", "Lata Mangeshkar", "Mere Mehboob"),
    "yaad mein teri": ("Soundtracks\\Mere Mehboob", "Mohammed Rafi", "Mere Mehboob"),
    "dil e betaab ko seene se lagana hoga": ("Soundtracks\\Palki", "Mohammed Rafi", "Palki"),
    "kal raat zindagi se mulaqat hogai": ("Soundtracks\\Palki", "Mohammed Rafi", "Palki"),
    "jalte hain jiske liye": ("Soundtracks\\Sujata", "Talat Mahmood", "Sujata"),
    "yeh shaam ki tanhaiyan": ("Soundtracks\\Aah", "Lata Mangeshkar", "Aah"),
    "raja ki aayegi baraat": ("Soundtracks\\Aah", "Lata Mangeshkar", "Aah"),
    "chal kahin door nikal jayen": ("Soundtracks\\Doosra Aadmi", "Kishore Kumar", "Doosra Aadmi"),
    "jidhar dekhoon teri tasvir": ("Soundtracks\\Mahaan", "Kishore Kumar", "Mahaan"),
    "mera jeevan kora kagaz": ("Soundtracks\\Kora Kagaz", "Kishore Kumar", "Kora Kagaz"),
    "aye zindagi gale laga le": ("Soundtracks\\Sadma", "Suresh Wadkar", "Sadma"),
    "apne pyar ke sapne": ("Soundtracks\\Barsaat Ki Ek Raat", "Kishore Kumar", "Barsaat Ki Ek Raat"),
    "nazrana behja kisi ne": ("Soundtracks\\Desh Pardesh", "Kishore Kumar", "Desh Pardesh"),
    "patthar ke sanam": ("Soundtracks\\Patthar Ke Sanam", "Mohammed Rafi", "Patthar Ke Sanam"),
    "o meri mahebooba": ("Soundtracks\\Dharam Veer", "Mohammed Rafi", "Dharam Veer"),
    "meri bhigi bhigi si": ("Soundtracks\\Anamika", "Kishore Kumar", "Anamika"),
    "aaja tujhko pukare": ("Soundtracks\\Neel Kamal", "Mohammed Rafi", "Neel Kamal"),
    "woh chand khila": ("Soundtracks\\Anari", "Lata Mangeshkar", "Anari"),
    "tera jana": ("Soundtracks\\Anari", "Lata Mangeshkar", "Anari"),
    "hum bewafa": ("Soundtracks\\Shalimar", "Kishore Kumar", "Shalimar"),
    "khush rahe tu sada": ("Soundtracks\\Khilona", "Mohammed Rafi", "Khilona"),
    "chandani raat main": ("Soundtracks\\Dil E Nadan", "Talat Mahmood", "Dil E Nadan"),
    "jis gali mein tera ghar": ("Soundtracks\\Kati Patang", "Mukesh", "Kati Patang"),
    "yeh jo mohabbat hai": ("Soundtracks\\Kati Patang", "Kishore Kumar", "Kati Patang"),
    "angreji beat": ("Soundtracks\\Cocktail", "Yo Yo Honey Singh", "Cocktail"),
    "tumhi ho bandhu": ("Soundtracks\\Cocktail", "Neeraj Shridhar", "Cocktail"),
    "adhoore": ("Soundtracks\\Break Ke Baad", "Vishal Dadlani", "Break Ke Baad"),
    "tai tai phish": ("Soundtracks\\Chillar Party", "Amit Trivedi", "Chillar Party"),
    "bhaag dk bose": ("Soundtracks\\Delhi Belly", "Ram Sampath", "Delhi Belly"),
    "mit jaaye gham": ("Soundtracks\\Dum Maaro Dum", "Sunidhi Chauhan", "Dum Maaro Dum"),
    "english vinglish": ("Soundtracks\\English Vinglish", "Amit Trivedi", "English Vinglish"),
    "ainvayi ainvayi": ("Soundtracks\\Band Baaja Baaraat", "Salim Merchant", "Band Baaja Baaraat"),
    "aal izz well": ("Soundtracks\\3 Idiots", "Sonu Nigam", "3 Idiots"),
    "give me some sunshine": ("Soundtracks\\3 Idiots", "Suraj Jagan", "3 Idiots"),
    "zoobi doobi": ("Soundtracks\\3 Idiots", "Sonu Nigam", "3 Idiots"),
    "dil to hai dil": ("Soundtracks\\Muqaddar Ka Sikandar", "Lata Mangeshkar", "Muqaddar Ka Sikandar"),
    "do pal": ("Soundtracks\\Veer-Zaara", "Lata Mangeshkar", "Veer-Zaara"),
    "do ghoont maine pee": ("Soundtracks\\Jheel Ke Us Paar", "Lata Mangeshkar", "Jheel Ke Us Paar"),
    "dulari suhani raat dhal": ("Soundtracks\\Dulari", "Mohammed Rafi", "Dulari"),
    "ek ajnabee hasina se": ("Soundtracks\\Ajanabee", "Kishore Kumar", "Ajanabee"),
    "ek haseen nigah ka mayamemsaab": ("Soundtracks\\Maya Memsaab", "Hridaynath Mangeshkar", "Maya Memsaab"),
    "hawas teri galiyon mein": ("Soundtracks\\Hawas", "Mohammed Rafi", "Hawas"),
    "hoton pe aisi baat": ("Soundtracks\\Jewel Thief", "Lata Mangeshkar", "Jewel Thief"),
    "hui shaam uka khayal": ("Soundtracks\\Mere Humdum Mere Dost", "Mohammed Rafi", "Mere Humdum Mere Dost"),
    "hum hai mataye kuncha": ("Soundtracks\\Dastak", "Lata Mangeshkar", "Dastak"),
    "hum pyar mein jalne walon ko": ("Soundtracks\\Jailor", "Lata Mangeshkar", "Jailor"),
    "insaaf ka mandir hai yeh": ("Soundtracks\\Amar", "Mohammed Rafi", "Amar"),
    "jaata hai tu kahan": ("Soundtracks\\Yes Boss", "Abhijeet", "Yes Boss"),
    "jabbhikoihaseenaherapheri": ("Soundtracks\\Hera Pheri", "Kishore Kumar", "Hera Pheri"),
    "jiska joi nahi": ("Soundtracks\\Laawaris", "Kishore Kumar", "Laawaris"),
    "jo unki tamanna": ("Soundtracks\\Intaqam", "Mohammed Rafi", "Intaqam"),
    "kailash kher khosla": ("Soundtracks\\Khosla Ka Ghosla", "Kailash Kher", "Khosla Ka Ghosla"),
    "keh doon tumhen": ("Soundtracks\\Deewaar", "Kishore Kumar", "Deewaar"),
    "kehna hi kya": ("Soundtracks\\Bombay", "K.S. Chithra", "Bombay"),
    "khali haath shaam aayi hai ijazzat": ("Soundtracks\\Ijaazat", "Asha Bhosle", "Ijaazat"),
    "khilona jaankar": ("Soundtracks\\Khilona", "Mohammed Rafi", "Khilona"),
    "khiza ke phool bhi": ("Soundtracks\\Do Raaste", "Mohammed Rafi", "Do Raaste"),
    "kya hua tera waada": ("Soundtracks\\Hum Kisise Kum Naheen", "Mohammed Rafi", "Hum Kisise Kum Naheen"),
    "kya se kya ho gaya": ("Soundtracks\\Guide", "Mohammed Rafi", "Guide"),
    "laal qilla na kisi ki aa": ("Soundtracks\\Lal Quila", "Mohammed Rafi", "Lal Quila"),
    "lajja": ("Soundtracks\\Lajja", "Anu Malik", "Lajja"),
    "maheboob ki mehandi apna": ("Soundtracks\\Mehboob Ki Mehndi", "Mohammed Rafi", "Mehboob Ki Mehndi"),
    "main ka karoo ram": ("Soundtracks\\Sangam", "Lata Mangeshkar", "Sangam"),
    "mausam hai ashiqana": ("Soundtracks\\Pakeezah", "Lata Mangeshkar", "Pakeezah"),
    "mili khak mein mohabbat": ("Soundtracks\\Chaudhvin Ka Chand", "Mohammed Rafi", "Chaudhvin Ka Chand"),
    "mohabbat ki jhoothi": ("Soundtracks\\Mughal-E-Azam", "Lata Mangeshkar", "Mughal-E-Azam"),
    "mohobbat aesi dhadkan": ("Soundtracks\\Anarkali", "Lata Mangeshkar", "Anarkali"),
    "mujhe dard e dil ka pata": ("Soundtracks\\Aakash Deep", "Mohammed Rafi", "Aakash Deep"),
    "mujhe duniya walo sharabi na samjho": ("Soundtracks\\Leader", "Mohammed Rafi", "Leader"),
    "mujhe raat din": ("Soundtracks\\Sangharsh", "Sonu Nigam", "Sangharsh"),
    "mujhe teri mohobat ka": ("Soundtracks\\Aap Aye Bahaar Ayee", "Mohammed Rafi", "Aap Aye Bahaar Ayee"),
    "mumbhai": ("Soundtracks\\Bombay Boys", "Javed Jaffrey", "Bombay Boys"),
    "nafrat ki duniya ko": ("Soundtracks\\Haathi Mere Saathi", "Mohammed Rafi", "Haathi Mere Saathi"),
    "neele neele ambar par": ("Soundtracks\\Kalaakaar", "Kishore Kumar", "Kalaakaar"),
    "nile nile amber par": ("Soundtracks\\Kalaakaar", "Kishore Kumar", "Kalaakaar"),
    "o duniya ke rakhwale": ("Soundtracks\\Baiju Bawra", "Mohammed Rafi", "Baiju Bawra"),
    "paise ki pehchan": ("Soundtracks\\Pehchan", "Mohammed Rafi", "Pehchan"),
    "pankhon ko": ("Soundtracks\\Rocket Singh", "Salim Merchant", "Rocket Singh"),
    "peene walon suno": ("Soundtracks\\Dushman", "Mohammed Rafi", "Dushman"),
    "phir teri kahani yaad aayi": ("Soundtracks\\Dil Diya Dard Liya", "Mohammed Rafi", "Dil Diya Dard Liya"),
    "raahi manwa dukh ki": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "raat ke andhere main aga": ("Soundtracks\\Raat Aur Din", "Mukesh", "Raat Aur Din"),
    "rahte the kabhi jinke dil": ("Soundtracks\\Mamta", "Mohammed Rafi", "Mamta"),
    "rozana": ("Soundtracks\\Naam Shabana", "Shreya Ghoshal", "Naam Shabana"),
    "sathiya": ("Soundtracks\\Saathiya", "Sonu Nigam", "Saathiya"),
    "sau baar janam lenge": ("Soundtracks\\Ustadon Ke Ustad", "Mohammed Rafi", "Ustadon Ke Ustad"),
    "tum mujhe yun bhulan na paoge": ("Soundtracks\\Pagla Kahin Ka", "Mohammed Rafi", "Pagla Kahin Ka"),
    "tumse milke aisa laga": ("Soundtracks\\Parinda", "Asha Bhosle", "Parinda"),
    "yaad na jaaye": ("Soundtracks\\Dil Ek Mandir", "Mohammed Rafi", "Dil Ek Mandir"),
    "yaar bina chain kahan": ("Soundtracks\\Saaheb", "Bappi Lahiri", "Saaheb"),
    "yahan main ajnabee hoon": ("Soundtracks\\Jab Jab Phool Khile", "Mohammed Rafi", "Jab Jab Phool Khile"),
    "ye raate nayi purani": ("Soundtracks\\Julie", "Lata Mangeshkar", "Julie"),
    "yeh aansoo mere dil ki zub": ("Soundtracks\\Humrahi", "Mukesh", "Humrahi"),
    "yeh dil tum bin kahin lagt": ("Soundtracks\\Izzat", "Mohammed Rafi", "Izzat"),
    "chaand taare": ("Soundtracks\\Yes Boss", "Abhijeet", "Yes Boss"),
    "dil dance maare": ("Soundtracks\\Tashan", "Sukhwinder Singh", "Tashan"),
    "ek din teri raahon": ("Soundtracks\\Naqaab", "Javed Ali", "Naqaab"),
    "fitna dil": ("Soundtracks\\Aap Kaa Surroor", "Himesh Reshammiya", "Aap Kaa Surroor"),
    "jao na": ("Soundtracks\\Whats Your Raashee", "Sohail Sen", "Whats Your Raashee"),
    "rukruk": ("Soundtracks\\Vijaypath", "Alisha Chinai", "Vijaypath"),
    "saiyaan re": ("Soundtracks\\Salaam-E-Ishq", "Shankar Mahadevan", "Salaam-E-Ishq"),
    "socha nahin tha": ("Soundtracks\\Socha Na Tha", "Sandesh Shandilya", "Socha Na Tha"),
    "tuaashiqehai": ("Soundtracks\\Jhankaar Beats", "KK", "Jhankaar Beats"),
    "sunona": ("Soundtracks\\Jhankaar Beats", "Shaan", "Jhankaar Beats"),
    "zaraza": ("Soundtracks\\Jannat", "KK", "Jannat"),
    "aap ke saat jind le gaya": ("Soundtracks\\Aap Aye Bahaar Ayee", "Mohammed Rafi", "Aap Aye Bahaar Ayee"),
    "ke saat jind le gaya": ("Soundtracks\\Aap Aye Bahaar Ayee", "Mohammed Rafi", "Aap Aye Bahaar Ayee"),
    "aur heera nazar aa": ("Soundtracks\\Kanch Aur Heera", "Mohammed Rafi", "Kanch Aur Heera"),
    "kanch aur heera nazar aa": ("Soundtracks\\Kanch Aur Heera", "Mohammed Rafi", "Kanch Aur Heera"),
    "baar mushkara dozaman": ("Soundtracks\\Ek Baar Muskura Do", "Kishore Kumar", "Ek Baar Muskura Do"),
    "ek baar mushkara dozaman": ("Soundtracks\\Ek Baar Muskura Do", "Kishore Kumar", "Ek Baar Muskura Do"),
    "badan bhari duniya me": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "do badan bhari duniya me": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "badan naseeb mein jin": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "do badan naseeb mein jin": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "naseeb main jis ke jo likh": ("Soundtracks\\Do Badan", "Mohammed Rafi", "Do Badan"),
    "dosti mera to jo bhi kad": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "mera to jo bhi kad": ("Soundtracks\\Dosti", "Mohammed Rafi", "Dosti"),
    "ek safara ek lootera hum": ("Soundtracks\\Ek Safar Ek Lootera", "Mohammed Rafi", "Ek Safar Ek Lootera"),
    "safara ek lootera hum": ("Soundtracks\\Ek Safar Ek Lootera", "Mohammed Rafi", "Ek Safar Ek Lootera"),
    "dil ke jharokhe mein": ("Soundtracks\\Brahmachari", "Mohammed Rafi", "Brahmachari"),
    "dil ki awaaz bhi sun": ("Soundtracks\\Humsaya", "Mohammed Rafi", "Humsaya"),
    "din baharke mere du": ("Soundtracks\\Aaye Din Bahar Ke", "Mohammed Rafi", "Aaye Din Bahar Ke"),
    "dono ne kiya tha pyar maga": ("Soundtracks\\Mahal", "Kishore Kumar", "Mahal"),
    "ek dil ke tukde hazar hue": ("Soundtracks\\Pyaar Ki Jeet", "Mohammed Rafi", "Pyaar Ki Jeet"),
    "pyar ki jeet ek dil ke t": ("Soundtracks\\Pyaar Ki Jeet", "Mohammed Rafi", "Pyaar Ki Jeet"),
    "ki jeet ek dil ke t": ("Soundtracks\\Pyaar Ki Jeet", "Mohammed Rafi", "Pyaar Ki Jeet"),
    "falak se tod ke dekho sitare": ("Artists\\Rafi", "Mohammed Rafi", "Great Hits"),
    "haye re hai tera": ("Soundtracks\\Kashmir Ki Kali", "Mohammed Rafi", "Kashmir Ki Kali"),
    "hum tere sanam na hote": ("Soundtracks\\Tere Ghar Ke Samne", "Mohammed Rafi", "Tere Ghar Ke Samne"),
    "humne jafa na seekhi": ("Soundtracks\\Zindagi Aur Khwab", "Mohammed Rafi", "Zindagi Aur Khwab"),
    "jab bhi chum leta hu": ("Soundtracks\\Samjhauta", "Kishore Kumar", "Samjhauta"),
    "jabse tumhen dekha hai sanam": ("Soundtracks\\Gharana", "Mohammed Rafi", "Gharana"),
    "jheel ke paar kya": ("Soundtracks\\Jheel Ke Us Paar", "Lata Mangeshkar", "Jheel Ke Us Paar"),
    "ka chandmili": ("Soundtracks\\Chaudhvin Ka Chand", "Mohammed Rafi", "Chaudhvin Ka Chand"),
    "meine chand": ("Soundtracks\\Chaudhvin Ka Chand", "Mohammed Rafi", "Chaudhvin Ka Chand"),
    "kabhi khud kabhi halat pe rona": ("Soundtracks\\Hum Dono", "Mohammed Rafi", "Hum Dono"),
    "kabhi na kabhi": ("Soundtracks\\Sharabi", "Mohammed Rafi", "Sharabi"),
    "kabhi to khul ke": ("Soundtracks\\Do Raaste", "Kishore Kumar", "Do Raaste"),
    "kahdo koi na kare yahan py": ("Soundtracks\\Kati Patang", "Kishore Kumar", "Kati Patang"),
    "kajrare nainawali": ("Soundtracks\\Suhaag", "Mohammed Rafi", "Suhaag"),
    "kal chaman tha aaj": ("Soundtracks\\Khandan", "Mohammed Rafi", "Khandan"),
    "kehte hain jisko": ("Soundtracks\\Grahasthi", "Mohammed Rafi", "Grahasthi"),
    "ki mehandi apna": ("Soundtracks\\Mehboob Ki Mehndi", "Mohammed Rafi", "Mehboob Ki Mehndi"),
    "kis tarha jeete hain": ("Soundtracks\\Nayi Umar Ki Nayi Fasal", "Mohammed Rafi", "Nayi Umar Ki Nayi Fasal"),
    "lajja 1": ("Soundtracks\\Lajja", "Anu Malik", "Lajja"),
    "mile na phool": ("Soundtracks\\Anokhi Raat", "Mohammed Rafi", "Anokhi Raat"),
    "mohabbat ke dhoke mein koi na aaye": ("Soundtracks\\Badi Bahen", "Mohammed Rafi", "Badi Bahen"),
    "naseeb dar pe tere": ("Soundtracks\\Deedar", "Mohammed Rafi", "Deedar"),
    "raat sabnami": ("Soundtracks\\Sanam Teri Kasam", "R.D. Burman", "Sanam Teri Kasam"),
    "saiyan dil main aana re": ("Soundtracks\\Bahar", "Shamshad Begum", "Bahar"),
    "sanam tu bewafa ke": ("Soundtracks\\Khilona", "Mohammed Rafi", "Khilona"),
    "sangam dost dost": ("Soundtracks\\Sangam", "Mukesh", "Sangam"),
    "tera mera milna": ("Soundtracks\\Aap Kaa Surroor", "Himesh Reshammiya", "Aap Kaa Surroor"),
    "teri zulfon se judaai": ("Soundtracks\\Jab Pyar Kisise Hota Hai", "Mohammed Rafi", "Jab Pyar Kisise Hota Hai"),
    "tukde hai mere dil ke": ("Soundtracks\\Mere Sanam", "Mohammed Rafi", "Mere Sanam"),
    "tumhin ne dard diya tumhin daga": ("Soundtracks\\Begaana", "Mukesh", "Begaana"),
    "dhuan": ("Soundtracks\\Dhuan", "R.D. Burman", "Dhuan"),
    "dil": ("Soundtracks\\Dil", "Anand-Milind", "Dil"),
    "sajan": ("Soundtracks\\Saajan", "Nadeem-Shravan", "Saajan"),
    "teramuskurana": ("Soundtracks\\Tera Muskurna", "Various Artists", "Tera Muskurna"),
    "halo halo remix": ("Soundtracks\\I See You", "Vishal-Shekhar", "I See You"),
    "halo halo": ("Soundtracks\\I See You", "Vishal-Shekhar", "I See You"),
    "left right left": ("Soundtracks\\Left Right Left", "Vishal-Shekhar", "Left Right Left"),
    "splitsvilla": ("Soundtracks\\Splitsvilla", "MTV", "Splitsvilla"),
    "splitsvilla2": ("Soundtracks\\Splitsvilla", "MTV", "Splitsvilla")
}

HINDI_ALBUMS_MAP = {
    "breathless full": ("Albums\\Breathless", "Shankar Mahadevan", "Breathless"),
    "breathless": ("Albums\\Breathless", "Shankar Mahadevan", "Breathless"),
    "bandeh": ("Albums\\Indian Ocean", "Indian Ocean", "Kandisa"),
    "bandeh msg": ("Albums\\Indian Ocean", "Indian Ocean", "Kandisa"),
    "bikra hoon main": ("Albums\\Jal", "Jal", "Aadat"),
    "abhijeet savant": ("Albums\\Abhijeet Sawant", "Abhijeet Sawant", "Aapka Abhijeet Sawant"),
    "aai jo teri yaad": ("Albums\\Aai Jo Teri Yaad", "Pankaj Udhas", "Aai Jo Teri Yaad"),
    "made india": ("Albums\\Made In India", "Alisha Chinai", "Made In India"),
    "kabhi to nazar milao": ("Albums\\Kabhi To Nazar Milao", "Adnan Sami", "Kabhi To Nazar Milao"),
    "dil le gayee": ("Albums\\Jasbir Jassi", "Jasbir Jassi", "Dil Le Gayee"),
    "rdb": ("Albums\\RDB", "RDB", "RDB Hits"),
    "dhoom pichak dhoom": ("Albums\\Euphoria", "Euphoria", "Dhoom"),
    "maaeri": ("Albums\\Euphoria", "Euphoria", "Phir Dhoom"),
    "dooba dooba rehta hoon": ("Albums\\Silk Route", "Silk Route", "Boondein"),
    "dil lutiya": ("Albums\\Jazzy B", "Jazzy B", "Romeo"),
    "gori nal ishq mita": ("Albums\\Bally Sagoo", "Bally Sagoo", "Bally Sagoo Hits"),
    "kya soorat hai": ("Albums\\Bombay Vikings", "Bombay Vikings", "Kya Soorat Hai"),
    "sun re sajanniya": ("Albums\\Ali Zafar", "Ali Zafar", "Huqa Pani"),
    "piya basanti re": ("Albums\\Piya Basanti", "K.S. Chithra", "Piya Basanti"),
    "kangna dr zeus": ("Albums\\Dr Zeus", "Dr. Zeus", "Kangna"),
    "zeus": ("Albums\\Dr Zeus", "Dr. Zeus", "Kangna"),
    "sukhbir": ("Albums\\Sukhbir", "Sukhbir", "Oi"),
    "filhaal": ("Albums\\B Praak", "B Praak", "Filhaal"),
    "emptiness": ("Albums\\Gajendra Verma", "Gajendra Verma", "Emptiness"),
    "hariharan aslam khan chitra sadhana sargam medley at ar rahman": ("Albums\\A R Raheman", "A.R. Rahman", "Live Medley"),
    "hum me he hero ar rahman": ("Albums\\A R Raheman", "A.R. Rahman", "Hero Motocorp Song")
}

GHAZAL_TRACK_MAP = {
    "aaj jaane ki zid na karo": ("Ghazals\\Farida Khanum", "Farida Khanum", "Ghazals"),
    "chupke chupke raat din": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "dil mein ik leher si uthi": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "hum tere saher mein aaye h": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "hoshwalo": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "hoshwalon ko khabar kya": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "tum ko dekha to yeh khayal aaya": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "jhuki jhuki si nazar": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "hothon se chhoo lo tum": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "chitthi na koi sandesh": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "chandi jaisa rang hai tera": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "aur aahista kijiye baatein": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "chitthi aayi hai": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "ektaraf": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "sabkomlm": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "thodipya": ("Ghazals\\Pankaj Udhas", "Pankaj Udhas", "Ghazals"),
    "duniya jise kahte hain": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "woh kagaz ki kashti": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "yeh daulat bhi lelo": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "yeh dil pagal dil mera": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "yeh na thi hamari kismat": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Ghazals"),
    "chamkte chand ko": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "gairon pe karam apnon": ("Ghazals\\Mehdi Hassan", "Mehdi Hassan", "Ghazals"),
    "gham ne hasane na diya": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "gham uthane ko": ("Ghazals\\Mehdi Hassan", "Mehdi Hassan", "Ghazals"),
    "gulon mein rang bharey": ("Ghazals\\Mehdi Hassan", "Mehdi Hassan", "Ghazals"),
    "guzre hain aaj ishq mein": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "hungama hai kyon": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "kisi ranjish ko hawa do": ("Ghazals\\Ghulam Ali", "Ghulam Ali", "Ghazals"),
    "chandni raatein": ("Ghazals\\Noor Jehan", "Noor Jehan", "Evergreen Ghazals"),
    "dama dam mast": ("Ghazals\\Runa Laila", "Runa Laila", "Sufi & Qawwali"),
    "damadammastkalandar": ("Ghazals\\Runa Laila", "Runa Laila", "Sufi & Qawwali"),
    "hotho se choo": ("Ghazals\\Jagjit Singh", "Jagjit Singh", "Prem Geet"),
    "sochta hoon ka di": ("Ghazals\\Nusrat Fateh Ali Khan", "Nusrat Fateh Ali Khan", "Ghazals"),
    "sochta hoon ka dil": ("Ghazals\\Nusrat Fateh Ali Khan", "Nusrat Fateh Ali Khan", "Ghazals"),
    "nfak": ("Ghazals\\Nusrat Fateh Ali Khan", "Nusrat Fateh Ali Khan", "Ghazals")
}

DEVOTIONAL_TRACK_MAP = {
    "aisi lagi lagan": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "chadariya jhini re jhini": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "chahe bansi bajaiya bolo": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "chalo man ganga jamuna teer": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "ab ki tek hamari murari": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "aaj radhika bano": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "bhakto apne mukh se": ("Devotional & Bhajans\\Anup Jalota", "Anup Jalota", "Bhajan Sandhya"),
    "vaishnav jan": ("Devotional & Bhajans\\Pandit Jasraj", "Pandit Jasraj", "Vaishnav Jan To"),
    "vraje vasantam": ("Devotional & Bhajans\\Jagjit Singh", "Jagjit Singh", "Krishna Bhajans")
}

MARATHI_TRACK_MAP = {
    "aabhas ha": ("Soundtracks\\Yanda Kartavya Aahe", "Swapnil Bandodkar", "Yanda Kartavya Aahe"),
    "aaj gokulat rang": ("Bhavgeet & Classics", "Lata Mangeshkar", "Bhavgeet"),
    "aaji soniyacha dinu": ("Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwar Mauli"),
    "aakashi zep ghe re pakhara": ("Sudhir Phadke", "Sudhir Phadke", "Aamhi Jato Aamchya Gava"),
    "aala aala paus aala": ("Balgeet", "Various Artists", "Balgeet"),
    "aala aala vara": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "aali thumkat naar lachkat": ("Lavani & Folk", "Various Artists", "Lavani"),
    "aamchimatiaamchimanasa000": ("Bhavgeet & Classics", "Various Artists", "Doordarshan"),
    "ae aai mala pawasat jau dena": ("Balgeet", "Various Artists", "Balgeet"),
    "aika satyanarayanachi": ("Abhang & Bhakti", "Various Artists", "Satyanarayan"),
    "airanichya deva tula": ("Lata Mangeshkar", "Lata Mangeshkar", "Sadhi Manasa"),
    "amrutahooni god": ("Abhang & Bhakti", "Bhimsen Joshi", "Abhang"),
    "are are dnyana zalasi pavan": ("Abhang & Bhakti", "Various Artists", "Abhang"),
    "asava sundar chockletcha bungla": ("Balgeet", "Various Artists", "Balgeet"),
    "ashtavinayaka": ("Abhang & Bhakti", "Various Artists", "Ashtavinayak"),
    "avachita parimalu": ("Abhang & Bhakti", "Lata Mangeshkar", "Abhang"),
    "bai bai manmoracha": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "bai mi vikat ghetala shyam": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "bala bhaktalagi": ("Abhang & Bhakti", "Various Artists", "Abhang"),
    "bhatukalichya khela madhali": ("Arun Date", "Arun Date", "Bhavgeet"),
    "bugadi mazi sandali": ("Lavani & Folk", "Lata Mangeshkar", "Pinjara"),
    "caidra bhage paindhari": ("Abhang & Bhakti", "Various Artists", "Vitthal Bhakti"),
    "chal ga sakhe": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chal sadhaka": ("Abhang & Bhakti", "Various Artists", "Bhakti"),
    "chandane shimpit jashi": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chandanyat phirtana": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "chandra bhagechya tiri": ("Abhang & Bhakti", "Various Artists", "Vitthal Bhakti"),
    "chhabidar chhabi mi": ("Lavani & Folk", "Various Artists", "Lavani"),
    "dhund hote shbd sare": ("Saleel Kulkarni", "Saleel Kulkarni", "Ayushyavar Bolu Kahi"),
    "dhagala lagli": ("Lavani & Folk", "Various Artists", "Lavani"),
    "gagan sadan tejomay": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "khel mandala": ("Ajay-Atul", "Ajay-Atul", "Natarang"),
    "pt bhimsen joshi": ("Bhimsen Joshi", "Bhimsen Joshi", "Abhang"),
    "tu sukhi raha": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "disala ga bai": ("Lavani & Folk", "Lata Mangeshkar", "Pinjara"),
    "disala ga baee": ("Lavani & Folk", "Lata Mangeshkar", "Pinjara"),
    "dole kashasathi": ("Bhavgeet & Classics", "Lata Mangeshkar", "Sanjyeti"),
    "dur rahuni": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "erneechya deva": ("Lata Mangeshkar", "Lata Mangeshkar", "Sadhi Manasa"),
    "garva": ("Bhavgeet & Classics", "Milind Ingle", "Garva"),
    "gele dyayache": ("Bhavgeet & Classics", "Lata Mangeshkar", "Bhavgeet"),
    "ghanu waje": ("Bhavgeet & Classics", "Lata Mangeshkar", "Bhavgeet"),
    "gomu sangatina": ("Bhavgeet & Classics", "Hemant Kumar", "Bhavgeet"),
    "gori gori pan": ("Balgeet", "Various Artists", "Balgeet"),
    "ha khel savalyancha": ("Soundtracks\\Ha Khel Savalyancha", "Mahendra Kapoor", "Ha Khel Savalyancha"),
    "haat tujha": ("Arun Date", "Arun Date", "Bhavgeet"),
    "hi pournima": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "hi vaat dur": ("Arun Date", "Arun Date", "Bhavgeet"),
    "indrachi kamini": ("Lavani & Folk", "Various Artists", "Lavani"),
    "ishqachi ingali": ("Lavani & Folk", "Various Artists", "Lavani"),
    "jambul pikalya": ("Lavani & Folk", "Asha Bhosle", "Lavani"),
    "jevhaan tichi": ("Saleel Kulkarni", "Saleel Kulkarni", "Ayushyavar Bolu Kahi"),
    "jivalaga rahile": ("Asha Bhosle", "Asha Bhosle", "Bhavgeet"),
    "ka re durava": ("Asha Bhosle", "Asha Bhosle", "Bhavgeet"),
    "kajal ratina": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "kalpanecha kunchala": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "kashi nashibana": ("Lavani & Folk", "Various Artists", "Lavani"),
    "kay bai sangu": ("Lavani & Folk", "Various Artists", "Lavani"),
    "kevhan tari": ("Suresh Wadkar", "Suresh Wadkar", "Bhavgeet"),
    "koli geet": ("Lavani & Folk", "Various Artists", "Koli Geet"),
    "konas thauk": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "kunya gavacha": ("Lavani & Folk", "Various Artists", "Lavani"),
    "kutha kutha jayacha": ("Lavani & Folk", "Various Artists", "Lavani"),
    "latpat latpat": ("Lavani & Folk", "Various Artists", "Amar Bhoopali"),
    "lek ladki": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "magate man": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "majhya dadala": ("Lavani & Folk", "Various Artists", "Lokgeet"),
    "mala lagali": ("Lavani & Folk", "Various Artists", "Pinjara"),
    "mana manav": ("Natyasangeet", "Various Artists", "Natyasangeet"),
    "mazya kapalicha": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "mee maj harpun": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "mi kashala": ("Lavani & Folk", "Various Artists", "Lavani"),
    "mogara phulala": ("Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwar Mauli"),
    "naadatuniya naad": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "naka toodu": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "nako devaraya": ("Abhang & Bhakti", "Various Artists", "Abhang"),
    "nilya ga dolyanchya": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "om namoji adhya": ("Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwari"),
    "pail to ge kaau": ("Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwar Mauli"),
    "phulanche phool": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "premachnahi": ("Saleel Kulkarni", "Sandeep Khare", "Ayushyavar Bolu Kahi"),
    "pustak nantar": ("Balgeet", "Various Artists", "Balgeet"),
    "ranga yei": ("Abhang & Bhakti", "Lata Mangeshkar", "Dnyaneshwar Mauli"),
    "rani bole": ("Natyasangeet", "Various Artists", "Natyasangeet"),
    "runu zunu": ("Bhavgeet & Classics", "Lata Mangeshkar", "Bhavgeet"),
    "ruperi valut": ("Asha Bhosle", "Asha Bhosle", "Bhavgeet"),
    "saang saang bholanath": ("Balgeet", "Various Artists", "Balgeet"),
    "samaichya shubhra": ("Arun Date", "Arun Date", "Bhavgeet"),
    "santha wahate krishnamai": ("Sudhir Phadke", "Sudhir Phadke", "Bhavgeet"),
    "sharad sundar": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "shodhisi manawa": ("Abhang & Bhakti", "Various Artists", "Abhang"),
    "shukratara mandwara": ("Arun Date", "Arun Date", "Bhavgeet"),
    "sonuli mazi": ("Balgeet", "Various Artists", "Balgeet"),
    "sukha karta": ("Ganpati Geete", "Various Artists", "Aarti"),
    "sur magu tula": ("Arun Date", "Arun Date", "Bhavgeet"),
    "swapnatalya kalyonno": ("Asha Bhosle", "Asha Bhosle", "Balgeet"),
    "tarun aahe ratra": ("Asha Bhosle", "Asha Bhosle", "Bhavgeet"),
    "thakale re nandlala": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhajan"),
    "tumhavar keli": ("Lavani & Folk", "Various Artists", "Lavani"),
    "tumhawar keli": ("Lavani & Folk", "Various Artists", "Lavani"),
    "tuzi mazi preet": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "vaara gaai": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "vat pahun nayan": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "vishwache aart": ("Abhang & Bhakti", "Various Artists", "Abhang"),
    "ya janmawar": ("Arun Date", "Arun Date", "Bhavgeet"),
    "ye re ghana": ("Asha Bhosle", "Asha Bhosle", "Bhavgeet"),
    "ye re ye re pawasa": ("Balgeet", "Various Artists", "Balgeet"),
    "yeu kashi priya": ("Bhavgeet & Classics", "Various Artists", "Bhavgeet"),
    "zalya tinhisanja": ("Lata Mangeshkar", "Lata Mangeshkar", "Bhavgeet"),
    "damlelyababanchikahani": ("Saleel Kulkarni", "Saleel Kulkarni", "Damlelya Babanchi Kahani"),
    "namanjur": ("Saleel Kulkarni", "Saleel Kulkarni", "Namanjur"),
    "garva": ("Albums\\Garva", "Milind Ingle", "Garva"),
    "disala ga bai disala": ("Soundtracks\\Pinjra", "Usha Mangeshkar", "Pinjra"),
    "kashi nashibana thatta aaj mandli": ("Soundtracks\\Pinjra", "Various Artists", "Pinjra"),
    "mala lagali kunachi uchaki": ("Soundtracks\\Pinjra", "Usha Mangeshkar", "Pinjra"),
    "gomu sangatina majhya tu": ("Soundtracks\\Ha Khel Savalyancha", "Hemant Kumar", "Ha Khel Savalyancha"),
    "ha khel savalyancha": ("Soundtracks\\Ha Khel Savalyancha", "Hemant Kumar", "Ha Khel Savalyancha"),
    "jiv rangala": ("Ajay-Atul", "Ajay-Atul", "Jogwa"),
    "de re kanha choli un lugdi": ("Abhang & Bhakti", "Various Artists", "Krishna Bhaktigeet"),
    "dhaaga dhaaga akhand vinuya": ("Sudhir Phadke", "Sudhir Phadke", "Bhavgeet"),
    "dhuke daatale udas udas": ("Arun Date", "Arun Date", "Bhavgeet"),
    "gele dyayache rahun": ("Arun Date", "Arun Date", "Bhavgeet"),
    "ghanu waje ghuna ghuna": ("Lata Mangeshkar", "Lata Mangeshkar", "Sant Dnyaneshwar"),
    "latpat latpat": ("Lata Mangeshkar", "Lata Mangeshkar", "Amar Bhoopali"),
    "kirtana": ("Abhang & Bhakti", "Various Artists", "Kirtan")
}

ENGLISH_TRACK_MAP = {
    "a beautiful mind": ("Soundtracks\\A Beautiful Mind", "James Horner", "A Beautiful Mind"),
    "all i want is you": ("U2", "U2", "Rattle and Hum"),
    "batman beyond": ("Soundtracks\\Batman", "The Crystal Method", "Batman Beyond"),
    "batman theme": ("Soundtracks\\Batman", "Danny Elfman", "Batman"),
    "comfotably numb lead": ("Pink Floyd", "Pink Floyd", "The Wall"),
    "creep acoustic": ("Radiohead", "Radiohead", "Pablo Honey"),
    "coma black": ("Marilyn Manson", "Marilyn Manson", "Holy Wood"),
    "burn hell": ("Marilyn Manson", "Marilyn Manson", "Holy Wood"),
    "celine dion": ("Celine Dion", "Celine Dion", "Celine Dion Hits"),
    "the wailers so much trouble the world": ("Bob Marley", "Bob Marley & The Wailers", "Survival"),
    "coming from the cold": ("Bob Marley", "Bob Marley & The Wailers", "Uprising"),
    "crazy baldheads": ("Bob Marley", "Bob Marley & The Wailers", "Rastaman Vibration"),
    "waiting vain": ("Bob Marley", "Bob Marley", "Exodus"),
    "war": ("Bob Marley", "Bob Marley", "Rastaman Vibration"),
    "enrique": ("Enrique Iglesias", "Enrique Iglesias", "Hits"),
    "guns n roses": ("Guns N' Roses", "Guns N' Roses", "Hits"),
    "here without you": ("3 Doors Down", "3 Doors Down", "Away From The Sun"),
    "if i let you go": ("Westlife", "Westlife", "Westlife"),
    "i get knocked down": ("Chumbawamba", "Chumbawamba", "Tubthumper"),
    "matt nathanson": ("Matt Nathanson", "Matt Nathanson", "Some Mad Hope"),
    "paradise city": ("Guns N' Roses", "Guns N' Roses", "Appetite For Destruction"),
    "james bond": ("Soundtracks\\James Bond", "Monty Norman", "007 Theme"),
    "when chai met toast": ("When Chai Met Toast", "When Chai Met Toast", "When Chai Met Toast"),
    "ghost busters": ("Soundtracks\\Ghostbusters", "Ray Parker Jr", "Ghostbusters"),
    "dont be shy": ("Kulcha Joshi", "Kulcha Joshi", "Dont Be Shy"),
    "emptiness": ("Rohan Rathore", "Rohan Rathore", "Emptiness"),
    "murders the rue morgue": ("Iron Maiden", "Iron Maiden", "Killers"),
    "pieces": ("Sum 41", "Sum 41", "Chuck"),
    "sayonee": ("Junoon", "Junoon", "Azadi"),
    "sexy eyes": ("Dr Hook", "Dr. Hook", "Rising"),
    "wham": ("Wham", "Wham", "Make It Big"),
    "dangerous": ("Michael Jackson -- Discography", "Michael Jackson", "Dangerous"),
    "nothing gonna change": ("Rock & Pop", "Glenn Medeiros", "Glenn Medeiros"),
    "nothings gonna change my love for you": ("Rock & Pop", "Glenn Medeiros", "Glenn Medeiros"),
    "bloom": ("Rock & Pop", "Various Artists", "Rock & Pop"),
    "all one": ("Rock & Pop", "Various Artists", "Rock & Pop"),
    "ambush the night": ("Rock & Pop", "Various Artists", "Rock & Pop")
}

RINGTONE_TRIGGERS = [
    "alarm", "alien phone", "angrycat", "airtel", "arabic ringtone", "ardour", "austin",
    "bacardi blast", "business cell tone", "captain planet", "cartoon", "casino royale",
    "counter strike", "cuppy cake", "d 6", "best guitar", "coinsound", "chic", "ak 47",
    "aaaa", "974 5554341", "but it rained solo", "but it rained start", "c b t l", "slip",
    "mclaren", "flipside", "frost", "toy box", "here comes the boom"
]

_CATALOG_CACHE = None

def normalize_title(name: str) -> str:
    if not name:
        return ""
    # Strip extension
    s = re.sub(r"\.[a-zA-Z0-9]+$", "", name)
    # Strip leading numbers e.g. "01 - ", "001 ", "32 "
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    # Strip brackets & parentheses
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    # Strip rip / quality / website badges
    s = re.sub(r"(downloadming|songs\.pk|djluv|mp3|320kbps|128kbps|ringtone|webrip|fmw11|pakheaven|apniisp)", "", s, flags=re.IGNORECASE)
    # Strip trailing single-letter rip flags e.g. ".M", ".Mp", "11!S", "!S"
    s = re.sub(r"(\.[a-z]|\d+!s|!s)+$", "", s, flags=re.IGNORECASE)
    # Strip Marathi ISRC code e.g. "INH100607702"
    s = re.sub(r"\binh\d+", "", s, flags=re.IGNORECASE)
    # Clean non-alphanumeric
    s = re.sub(r"[^a-zA-Z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def clean_catalog_folder_name(folder: str) -> str:
    """Cleans a folder name into a canonical title without brackets or stray numbers."""
    if not folder:
        return ""
    raw_lower = folder.strip().lower()
    for k, v in CULTURAL_NUMBERED_TITLES.items():
        k_re = r"\b" + r"[-\s]*".join(re.escape(w) for w in k.split()) + r"\b"
        if re.search(k_re, raw_lower):
            return v
    s = re.sub(r"\[.*?\]|\(.*?\)", "", folder)
    s = re.sub(r"^\s*\d+[\s\.\-_]*", "", s)
    s = re.sub(r"[^a-zA-Z0-9\s\-&']", " ", s)
    # Filter non-cultural digits
    tokens = s.split()
    clean_toks = []
    for tok in tokens:
        if tok.isdigit():
            if tok in ["9211", "1942", "420", "36", "84", "2", "3"]:
                clean_toks.append(tok)
        else:
            clean_toks.append(tok)
    s = " ".join(clean_toks)
    return re.sub(r"\s+", " ", s).strip(" .-_/\\").title()

def get_catalog_index() -> Dict[str, Tuple[str, str, str]]:
    """
    Returns index mapping normalized track title -> (language, category, album/movie).
    Built on first invocation in ~0.2s from master_cross_drive_catalog.db.
    """
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    _CATALOG_CACHE = {}
    if not os.path.exists(DB_PATH):
        return _CATALOG_CACHE

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT file_path, filename FROM master_audio_catalog WHERE file_path NOT LIKE '%organized%'")
        rows = c.fetchall()
        conn.close()
    except Exception:
        return _CATALOG_CACHE

    for path, fname in rows:
        p_lower = path.lower()
        parts = path.split("\\")
        clean_fstem = re.sub(r"\.[a-zA-Z0-9]+$", "", fname)
        found_info = None
        song_part = None

        # 1. Ringtones
        if "ringtone" in p_lower:
            found_info = ("Ringtones", "Ringtones & Alerts", "Ringtones")

        # 2. Sanskrit
        elif any(k in p_lower for k in ["vidik sukta", "vaidik sukta", "sanskrit"]):
            if "samhita" in p_lower:
                found_info = ("Sanskrit", "Vedic Samhita", "Vedic Samhita")
            elif any(st in p_lower for st in ["stotra", "ashtak"]):
                found_info = ("Sanskrit", "Stotras & Ashtakams", "Stotras & Ashtakams")
            else:
                found_info = ("Sanskrit", "Vedic Suktas", "Vedic Suktas")

        # 3. Pravachan
        elif "pravachan" in p_lower or "katha" in p_lower:
            if "ghaisasi" in p_lower:
                if "artya" in p_lower or re.match(r"^(arti|song\s*\d+)", clean_fstem, re.I):
                    found_info = ("Pravachan", "Bhagwat Katha\\Ghaisasi Guruji\\Artya", "Bhagwat Katha - Ghaisasi Guruji - Artya")
                elif any(d in p_lower for d in ["day 01-05", "day 1", "day 2", "day 3", "day 4", "day 5"]):
                    found_info = ("Pravachan", "Bhagwat Katha\\Ghaisasi Guruji\\Day 01-05", "Bhagwat Katha - Ghaisasi Guruji - Day 01-05")
                elif any(d in p_lower for d in ["day 06-10", "day 6", "day 7", "day 8", "day 9", "day 10"]):
                    found_info = ("Pravachan", "Bhagwat Katha\\Ghaisasi Guruji\\Day 06-10", "Bhagwat Katha - Ghaisasi Guruji - Day 06-10")
                else:
                    found_info = ("Pravachan", "Bhagwat Katha\\Ghaisasi Guruji", "Bhagwat Katha - Ghaisasi Guruji")
            elif "kavishwar" in p_lower or "kshwar" in p_lower:
                found_info = ("Pravachan", "Bhagwat Katha\\Kavishwar Maharaj", "Bhagwat Katha - Kavishwar Maharaj")
            elif "aparna" in p_lower and any(g in p_lower for g in ["gita", "pathan", "abhyankar"]):
                found_info = ("Pravachan", "Gita Pathan\\Aparna Abhyankar", "Bhagavad Gita Pathan")
            elif "abhyankar" in p_lower or "gita" in p_lower:
                if "ramdas" in p_lower:
                    found_info = ("Pravachan", "Shankar Abhyankar\\Ramdas Swami - Nirupan", "Ramdas Swami - Nirupan")
                else:
                    found_info = ("Pravachan", "Shankar Abhyankar\\Bhagavad Gita - Nirupan", "Bhagavad Gita - Nirupan")
            else:
                found_info = ("Pravachan", "Discourses", "Discourses")

        # 4. Marathi
        elif "marathi" in p_lower:
            if "ajay" in p_lower and "atul" in p_lower:
                found_info = ("Marathi", "Ajay-Atul", "Ajay-Atul Hits")
            elif "geet ramayan" in p_lower or "g d malgulkar" in p_lower:
                found_info = ("Marathi", "Geet Ramayan", "Geet Ramayan")
            elif "natya sangeet" in p_lower:
                found_info = ("Marathi", "Natyasangeet", "Natyasangeet")
            elif "ganpati song" in p_lower:
                found_info = ("Marathi", "Ganpati Geete", "Ganpati Geete")
            elif "devachya charani" in p_lower or "abhang" in p_lower:
                found_info = ("Marathi", "Abhang & Bhakti", "Abhang & Bhakti")
            else:
                for i, p in enumerate(parts):
                    if p.lower() == "marathi" and i + 1 < len(parts) - 1:
                        cand = clean_catalog_folder_name(parts[i+1])
                        if cand and cand.lower() not in ["marathi songs", "random", "artist"]:
                            found_info = ("Marathi", cand, cand)
                            break
                if not found_info:
                    found_info = ("Marathi", "Bhavgeet & Classics", "Bhavgeet & Classics")

        # 5. English
        elif "english" in p_lower:
            if "friends" in p_lower:
                found_info = ("English", "Soundtracks\\Friends - The Ultimate Soundtrack", "Friends - The Ultimate Soundtrack")
            else:
                for b in ["metallica", "megadeth", "nirvana", "nickelback", "opeth", "coldplay", "iron maiden", "pink floyd", "the beatles", "beatles", "linkin park", "u2", "green day"]:
                    if b in p_lower:
                        canon_b = "The Beatles" if "beatles" in b else b.title()
                        found_info = ("English", canon_b, canon_b)
                        break
                if not found_info:
                    for i, p in enumerate(parts):
                        if p.lower() == "english" and i + 1 < len(parts) - 1:
                            cand = clean_catalog_folder_name(parts[i+1])
                            if cand and cand.lower() == "discography" and i + 2 < len(parts) - 1:
                                cand = clean_catalog_folder_name(parts[i+2])
                            if cand and cand.lower() not in ["singles", "random", "discography"]:
                                found_info = ("English", cand, cand)
                                break
                if not found_info:
                    clean_fstem = re.sub(r"\.[a-zA-Z0-9]+$", "", fname)
                    if " - " in clean_fstem:
                        dash_parts = clean_fstem.split(" - ")
                        for dp in dash_parts:
                            p_cand = clean_catalog_folder_name(dp)
                            if p_cand and len(p_cand) > 2 and p_cand.lower() not in ["greatest guitar solos", "track", "disc", "single", "various artists"]:
                                found_info = ("English", p_cand, p_cand)
                                break
                if not found_info:
                    found_info = ("English", "Rock & Pop", "Rock & Pop")

        # 6. Hindi
        elif "hindi" in p_lower or "old" in p_lower:
            # Check Old Movies
            if "old movies" in p_lower:
                for i, p in enumerate(parts):
                    if p.lower() == "old movies" and i + 1 < len(parts) - 1:
                        mov = clean_catalog_folder_name(parts[i+1])
                        if mov:
                            found_info = ("Hindi", f"Soundtracks\\{mov}", mov)
                            break
            # Check Hindi New Movies
            elif "new" in p_lower:
                for i, p in enumerate(parts):
                    if p.lower() == "new" and i + 1 < len(parts) - 1:
                        mov = clean_catalog_folder_name(parts[i+1])
                        if mov and mov.lower() not in ["albums", "new folder", "sama"]:
                            found_info = ("Hindi", f"Soundtracks\\{mov}", mov)
                            break
                        elif mov.lower() == "albums" and i + 2 < len(parts) - 1:
                            alb = clean_catalog_folder_name(parts[i+2])
                            if alb:
                                found_info = ("Hindi", f"Albums\\{alb}", alb)
                                break
            # Check Artist subfolder under Old or Hindi
            if not found_info:
                for art_kw in ["lata", "kishore", "rafi", "mukesh", "asha", "pankaj udhas", "pankaj udas", "jagjit", "yesudas", "manna dey"]:
                    if art_kw in p_lower:
                        clean_art = "Pankaj Udhas" if "pankaj" in art_kw else clean_catalog_folder_name(art_kw)
                        found_info = ("Hindi", f"Artists\\{clean_art}", clean_art)
                        break

            # Check filename pattern e.g. "052_AMARPREM___CHINGARI_KOI.MP3" or "001 DOOSRA AADMI = CHAL KAHIN DOOR.mp3"
            if not found_info:
                clean_fstem = re.sub(r"\.[a-zA-Z0-9]+$", "", fname)
                if "=" in clean_fstem:
                    parts_eq = clean_fstem.split("=", 1)
                    m_cand = clean_catalog_folder_name(parts_eq[0])
                    song_part = parts_eq[1]
                    if m_cand and len(m_cand) > 2:
                        found_info = ("Hindi", f"Soundtracks\\{m_cand}", m_cand)
                elif "___" in clean_fstem or "__" in clean_fstem:
                    sep = "___" if "___" in clean_fstem else "__"
                    parts_und = clean_fstem.split(sep, 1)
                    m_cand = clean_catalog_folder_name(parts_und[0])
                    song_part = parts_und[1]
                    if m_cand and len(m_cand) > 2:
                        found_info = ("Hindi", f"Soundtracks\\{m_cand}", m_cand)

        if found_info:
            fn_norm = normalize_title(fname)
            if fn_norm and len(fn_norm) > 3:
                # Do not overwrite specific with generic
                if fn_norm not in _CATALOG_CACHE or _CATALOG_CACHE[fn_norm][1] in ["Rock & Pop", "Evergreen Classics", "Bhavgeet & Classics", "General"]:
                    _CATALOG_CACHE[fn_norm] = found_info
            if song_part:
                sp_norm = normalize_title(song_part)
                if sp_norm and len(sp_norm) > 3:
                    if sp_norm not in _CATALOG_CACHE or _CATALOG_CACHE[sp_norm][1] in ["Rock & Pop", "Evergreen Classics", "Bhavgeet & Classics", "General"]:
                        _CATALOG_CACHE[sp_norm] = found_info

    return _CATALOG_CACHE

def lookup_catalog_track(
    filename: str,
    tag_title: str = "",
    tag_artist: str = "",
    duration: float = 0.0
) -> Optional[Tuple[str, str, str]]:
    """
    Comprehensive ground-truth lookup across:
    1. Direct master catalog indexed cache
    2. Curated Bollywood soundtrack map
    3. Curated Non-film Hindi albums map
    4. Curated Ghazals & Devotional maps
    5. Curated Marathi & English classics
    6. Ringtones & short audio trigger detection
    """
    fn_norm = normalize_title(filename)
    title_norm = normalize_title(tag_title)

    # 0. Sanskrit Devanagari Stotras
    if any(sk in filename for sk in ["देव्या", "कवच", "कीलकम्", "अर्गला", "कुंजिका", "कुञ्चिका", "संथा", "स्तोत्र"]):
        return ("Sanskrit", "Stotras & Ashtakams", "Devi Mahatmyam")

    # 0.01 Sukt / Vedic Suktas
    if fn_norm in ["sukt", "sukta", "suktam"]:
        return ("Sanskrit", "Vedic Suktas", "Vedic Suktas")

    # 0.02 Pravachan: Aparna Ramtirthakar
    if "aparna ramtirthakar" in filename.lower() or "aparna ramtirthakar" in tag_artist.lower():
        return ("Pravachan", "Discourses\\Aparna Ramtirthakar", "Aparna Ramtirthakar")

    # 0.03 Personal voice notes / Astrology
    if any(k in filename.lower() for k in ["leaf astro", "nilesh hapse"]):
        return ("Personal Recordings", "Voice Notes & Astrology", "Voice Notes")

    # 0.1 When Chai Met Toast English Band
    if "when chai met toast" in filename.lower() or "when chai met toast" in tag_title.lower():
        clean_tit = clean_catalog_folder_name(re.sub(r"when chai met toast", "", filename, flags=re.I))
        return ("English", "When Chai Met Toast", clean_tit or "When Chai Met Toast")

    # 0.2 Marathi ISRC Code check (Saregama India Marathi catalog codes)
    if re.search(r"inh\d+", filename, re.IGNORECASE) or re.search(r"inh\d+", tag_artist, re.IGNORECASE):
        clean_tit = clean_catalog_folder_name(re.sub(r"inh\d+", "", filename, flags=re.I))
        return ("Marathi", "Bhavgeet & Classics", clean_tit or "Bhavgeet")

    # 1. Friends Soundtrack CD1 / CD2 check
    if re.search(r"\bcd[12]\s*track\d+\b", fn_norm):
        return ("English", "Soundtracks\\Friends - The Ultimate Soundtrack", "Friends - The Ultimate Soundtrack")

    # 2. Ringtones & Sound Effects
    if any(rt in fn_norm for rt in RINGTONE_TRIGGERS) or any(rt in title_norm for rt in RINGTONE_TRIGGERS) or (0 < duration < 40 and any(ext in filename.lower() for ext in [".mp3", ".ogg", ".wav", ".wma"])):
        return ("Ringtones", "Ringtones & Alerts", "Ringtones")

    # 3. Check Curated Bollywood Soundtracks
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in BOLLYWOOD_TRACK_MAP:
            cat, art, alb = BOLLYWOOD_TRACK_MAP[cand]
            return ("Hindi", cat, alb)
        for k, (cat, art, alb) in BOLLYWOOD_TRACK_MAP.items():
            if len(k) > 5 and k in cand:
                return ("Hindi", cat, alb)

    # 4. Check Curated Non-film Hindi Albums
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in HINDI_ALBUMS_MAP:
            cat, art, alb = HINDI_ALBUMS_MAP[cand]
            return ("Hindi", cat, alb)
        for k, (cat, art, alb) in HINDI_ALBUMS_MAP.items():
            if len(k) > 5 and k in cand:
                return ("Hindi", cat, alb)

    # 5. Check Ghazals
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in GHAZAL_TRACK_MAP:
            cat, art, alb = GHAZAL_TRACK_MAP[cand]
            return ("Hindi", cat, alb)
        for k, (cat, art, alb) in GHAZAL_TRACK_MAP.items():
            if len(k) > 5 and k in cand:
                return ("Hindi", cat, alb)

    # 6. Check Devotional & Bhajans
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in DEVOTIONAL_TRACK_MAP or "anup jalota" in tag_artist.lower():
            if cand in DEVOTIONAL_TRACK_MAP:
                cat, art, alb = DEVOTIONAL_TRACK_MAP[cand]
                return ("Hindi", cat, alb)
            return ("Hindi", "Devotional & Bhajans\\Anup Jalota", "Anup Jalota")

    # 7. Check Marathi Classics
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in MARATHI_TRACK_MAP:
            cat, art, alb = MARATHI_TRACK_MAP[cand]
            return ("Marathi", cat, alb)
        for k, (cat, art, alb) in MARATHI_TRACK_MAP.items():
            if len(k) > 5 and k in cand:
                return ("Marathi", cat, alb)

    # 8. Check English Classics
    for cand in [fn_norm, title_norm]:
        if not cand:
            continue
        if cand in ENGLISH_TRACK_MAP:
            cat, art, alb = ENGLISH_TRACK_MAP[cand]
            return ("English", cat, alb)
        for k, (cat, art, alb) in ENGLISH_TRACK_MAP.items():
            if len(k) > 5 and k in cand:
                return ("English", cat, alb)

    # 9. Check Master Catalog In-Memory Cache
    index = get_catalog_index()
    if fn_norm and fn_norm in index:
        return index[fn_norm]
    if title_norm and title_norm in index:
        return index[title_norm]

    # Partial substring search in catalog index
    if fn_norm and len(fn_norm) > 6:
        for k, v in index.items():
            if len(k) > 6 and (k in fn_norm or fn_norm in k):
                if v[1] not in ["Rock & Pop", "Evergreen Classics", "Bhavgeet & Classics", "General"]:
                    return v

    return None
