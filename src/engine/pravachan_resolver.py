import os
import re
from typing import Optional, Dict, Any

GITA_ADHYAY_MAP = {
    "arjunvishad": (1, "Arjunvishadyog"),
    "sankhya": (2, "Sankhyayog"),
    "saankhya": (2, "Sankhyayog"),
    "dnyankarmsanyas": (4, "Dnyankarmsanyasyog"),
    "karmsanyas": (5, "Karmsanyasyog"),
    "karma": (3, "Karmayog"),
    "aatmsanyam": (6, "Aatmsanyamyog"),
    "atmasanyam": (6, "Aatmsanyamyog"),
    "dnyanvidnyan": (7, "Dnyanvidnyanyog"),
    "aksharbramha": (8, "Aksharbramhayog"),
    "aksharbrahma": (8, "Aksharbramhayog"),
    "rajvidya": (9, "Rajvidyarajguhyayog"),
    "vibhuti": (10, "Vibhutiyog"),
    "vishwarup": (11, "Vishwarupdarshanyog"),
    "vishvarup": (11, "Vishwarupdarshanyog"),
    "bhakti": (12, "Bhaktiyog"),
    "kshetra": (13, "Kshetrakshetradnyavibhagyog"),
    "gunatray": (14, "Gunatrayvibhagyog"),
    "guntraya": (14, "Gunatrayvibhagyog"),
    "purushottam": (15, "Purushottamyog"),
    "daivasur": (16, "Daivasursampattibhagyog"),
    "shraddhatray": (17, "Shraddhatrayvibhagyog"),
    "mokshasanyas": (18, "Mokshasanyasyog"),
}

def resolve_pravachan_track(filename: str, source_path: str, tag_title: str = "", tag_artist: str = "", tag_album: str = "") -> Optional[Dict[str, Any]]:
    combined = f"{source_path} | {filename} | {tag_title} | {tag_artist} | {tag_album}".lower()
    
    # 0. Exclude Marathi songs that happen to contain the word 'katha' (bank/story)
    if "raghavachi katha" in combined:
        return {
            "language": "Marathi",
            "category": "Geet Ramayan",
            "artist": "Sudhir Phadke",
            "album": "Geet Ramayan",
            "title": "Raghavachi Katha",
            "confidence": 0.99,
            "decision_source": "Taxonomy: Marathi Song Exception"
        }
    if "swar gangechya katha" in combined or "swara gangechya katha" in combined or "kathawarati" in combined:
        return {
            "language": "Marathi",
            "category": "Arun Date",
            "artist": "Arun Date",
            "album": "Bhavgeet",
            "title": "Swar Gangechya Kathavarti",
            "confidence": 0.99,
            "decision_source": "Taxonomy: Marathi Song Exception"
        }

    # Check if this track is genuinely a Pravachan / Katha / Discourse
    is_prav = False
    if any(k in combined for k in [
        "pravachan", "katha", "kavishwar", "kshwar", "ghaisasi", "abhyankar", 
        "ramdas swami", "gita pathan", "bhagvat gita", "bhagavad-gita", "bhagvadgita"
    ]):
        is_prav = True
    elif re.search(r"\b[a-zA-Z]+yog\b", combined) and not any(ign in combined for ign in ["yoga", "yogesh", "priya", "sahayog"]):
        is_prav = True

    if not is_prav:
        return None

    stem = os.path.splitext(filename)[0]
    # Remove copy indicators like (1), (2), _179223...
    stem_clean = re.sub(r"\s*\(\d+\)", "", stem)
    stem_clean = re.sub(r"_\d{6,}", "", stem_clean).strip()
    
    # 1. Ghaisasi Guruji - Bhagwat Katha
    if "ghaisasi" in combined:
        artist = "Ghaisasi Guruji"
        if "artya" in combined or re.match(r"^(arti|song\s*\d+)", stem_clean, re.I):
            category = "Bhagwat Katha\\Ghaisasi Guruji\\Artya"
            album = "Bhagwat Katha - Ghaisasi Guruji - Artya"
            m = re.match(r"^song\s*0?(\d+)", stem_clean, re.I)
            title = f"Arti - Song {int(m.group(1)):02d}" if m else stem_clean.title()
        else:
            m_day = re.search(r"day\s*0?(\d+)\s*0?(\d+)?\s*([ab])?", stem_clean, re.I)
            if m_day:
                d_num = int(m_day.group(1))
                s_num = m_day.group(2) or "1"
                part_ltr = (m_day.group(3) or "A").upper()
                if d_num <= 5:
                    category = "Bhagwat Katha\\Ghaisasi Guruji\\Day 01-05"
                    album = "Bhagwat Katha - Ghaisasi Guruji - Day 01-05"
                else:
                    category = "Bhagwat Katha\\Ghaisasi Guruji\\Day 06-10"
                    album = "Bhagwat Katha - Ghaisasi Guruji - Day 06-10"
                title = f"Day {d_num:02d} - Session {s_num}{part_ltr}"
            elif "bhajani raam" in stem_clean.lower():
                category = "Bhagwat Katha\\Ghaisasi Guruji"
                album = "Bhagwat Katha - Ghaisasi Guruji"
                title = "Bhajani Raam"
            else:
                category = "Bhagwat Katha\\Ghaisasi Guruji"
                album = "Bhagwat Katha - Ghaisasi Guruji"
                title = stem_clean.title()
        return {
            "language": "Pravachan",
            "category": category,
            "artist": artist,
            "album": album,
            "title": title,
            "confidence": 0.99,
            "decision_source": "Pravachan: Ghaisasi Guruji Bhagwat Katha"
        }

    # 2. Kavishwar Maharaj - Bhagwat Katha
    if "kavish" in combined or "kshwar" in combined:
        artist = "Kavishwar Maharaj"
        category = "Bhagwat Katha\\Kavishwar Maharaj"
        album = "Bhagwat Katha - Kavishwar Maharaj"
        m_k = re.search(r"(?:kshwar|kavishwar)?\s*0?(\d+)\s*([ab])?", stem_clean, re.I)
        if m_k and m_k.group(1):
            k_num = int(m_k.group(1))
            k_ltr = (m_k.group(2) or "").upper()
            title = f"Kavishwar Maharaj - Session {k_num:02d}{k_ltr}".strip()
        else:
            title = stem_clean.title()
        return {
            "language": "Pravachan",
            "category": category,
            "artist": artist,
            "album": album,
            "title": title,
            "confidence": 0.99,
            "decision_source": "Pravachan: Kavishwar Maharaj Bhagwat Katha"
        }

    # 3. Aparna Abhyankar - Gita Pathan
    if "aparna abhyankar" in combined or ("aparna" in combined and any(g in combined for g in ["gita", "pathan", "adhyay", "track"])):
        artist = "Aparna Abhyankar"
        category = "Gita Pathan\\Aparna Abhyankar"
        album = "Bhagavad Gita Pathan"
        m_ad = re.search(r"(?:track|\b)\s*0?(\d{1,2})\b", stem_clean, re.I)
        if m_ad:
            ad_num = int(m_ad.group(1))
            title = f"Bhagavad Gita - Adhyay {ad_num:02d}"
        else:
            title = stem_clean.title()
        return {
            "language": "Pravachan",
            "category": category,
            "artist": artist,
            "album": album,
            "title": title,
            "confidence": 0.99,
            "decision_source": "Pravachan: Aparna Abhyankar Gita Pathan"
        }

    # 4. Shankar Abhyankar - Bhagavad Gita Nirupan & Ramdas Swami
    if "abhyankar" in combined or "bhagvadgita" in combined or "ramdas" in combined or "gita" in combined or re.search(r"\b[a-zA-Z]+yog\b", combined):
        artist = "Dr. Shankar Abhyankar"
        if "ramdas" in combined:
            category = "Shankar Abhyankar\\Ramdas Swami - Nirupan"
            album = "Ramdas Swami - Nirupan"
            m_p = re.search(r"pravachan\s*0?(\d+)\s*([ab])?", stem_clean, re.I)
            if m_p:
                p_num = int(m_p.group(1))
                p_ltr = (m_p.group(2) or "").upper()
                title = f"Ramdas Swami Nirupan - Part {p_num:02d}{p_ltr}".strip()
            else:
                title = stem_clean.title()
        else:
            category = "Shankar Abhyankar\\Bhagavad Gita - Nirupan"
            album = "Bhagavad Gita - Nirupan"
            
            # Match Yog and Part
            matched_adhyay = None
            for key, (adh_no, adh_canonical) in GITA_ADHYAY_MAP.items():
                if key in combined:
                    matched_adhyay = (adh_no, adh_canonical)
                    break
            
            # Determine Part 1 or Part 2
            part_no = "1"
            m_part = re.search(r"(?:part|\b)0?([12])\b", stem_clean, re.I)
            if m_part:
                part_no = m_part.group(1)
            elif "02" in stem_clean or "part 2" in stem_clean.lower():
                part_no = "2"

            if "intro" in stem_clean.lower():
                title = "Bhagavad Gita - Introduction"
            elif stem_clean.lower() in ["bhagavad-gita", "bhagvadgita", "bhagavad gita"]:
                title = "Bhagavad Gita - Sampoorna Nirupan"
            elif matched_adhyay:
                adh_no, adh_canonical = matched_adhyay
                title = f"Adhyay {adh_no:02d} - {adh_canonical} Part {part_no}"
            else:
                m_adh = re.search(r"(\d{1,2})\s*-\s*([a-zA-Z]+yog)\s*0?(\d)?", stem_clean, re.I)
                if m_adh:
                    c_num = int(m_adh.group(1))
                    c_name = m_adh.group(2).title()
                    p_num = m_adh.group(3) or part_no
                    title = f"Adhyay {c_num:02d} - {c_name} Part {p_num}"
                else:
                    m_adh2 = re.search(r"([a-zA-Z]+yog)\s*0?(\d)?", stem_clean, re.I)
                    if m_adh2:
                        c_name = m_adh2.group(1).title()
                        p_num = m_adh2.group(2) or part_no
                        title = f"{c_name} Part {p_num}"
                    else:
                        title = stem_clean.title()

        return {
            "language": "Pravachan",
            "category": category,
            "artist": artist,
            "album": album,
            "title": title,
            "confidence": 0.99,
            "decision_source": "Pravachan: Dr. Shankar Abhyankar Nirupan"
        }

    # 5. Dutta Digambar Guru (Ajit Kadkade)
    if "dutta" in combined or "kadkade" in combined:
        return {
            "language": "Marathi",
            "category": "Abhang & Bhakti\\Ajit Kadkade",
            "artist": "Ajit Kadkade",
            "album": "Dutta Digambar Guru",
            "title": stem_clean.title(),
            "confidence": 0.99,
            "decision_source": "Taxonomy: Ajit Kadkade Dutta Digambar Guru"
        }

    # 6. Aparna Ramtirthakar
    if "aparna ramtirthakar" in combined:
        return {
            "language": "Pravachan",
            "category": "Discourses\\Aparna Ramtirthakar",
            "artist": "Aparna Ramtirthakar",
            "album": "Discourses",
            "title": stem_clean.title(),
            "confidence": 0.99,
            "decision_source": "Pravachan: Aparna Ramtirthakar Discourse"
        }

    # 7. Other general pravachan
    return {
        "language": "Pravachan",
        "category": "Discourses",
        "artist": "Various Speakers",
        "album": "Discourses",
        "title": stem_clean.title(),
        "confidence": 0.90,
        "decision_source": "Pravachan: General Discourse"
    }
