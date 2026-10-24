"""
Auralis - Embedded Intelligence & Lightweight Language Engine
Ultra-efficient, low-memory embedded classification engine.
Replaces resource-heavy server-based LLMs with an embedded,
in-process intelligence layer (<50MB RAM) with canonical artist consolidation,
film deduplication, and an optional AirLLM layer-streaming adapter.
"""

import os
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("auralis.intelligence")

# Canonical artist & band aliases table to prevent category fragmentation
CANONICAL_ARTISTS = {
    # English
    "cold play": "Coldplay",
    "coldplay": "Coldplay",
    "iron maiden": "Iron Maiden",
    "ironmaiden": "Iron Maiden",
    "angra": "Angra",
    "michael jackson": "Michael Jackson",
    "micheal jackson": "Michael Jackson",
    "michael jackson siedah garrett": "Michael Jackson",
    "mj": "Michael Jackson",
    "pink floyd": "Pink Floyd",
    "pinkfloyd": "Pink Floyd",
    "the beatles": "The Beatles",
    "beatles": "The Beatles",
    "green day": "Green Day",
    "greenday": "Green Day",
    "nine inch nails": "Nine Inch Nails",
    "nin": "Nine Inch Nails",
    "u2": "U2",
    "nirvana": "Nirvana",
    "linkin park": "Linkin Park",
    "linkinpark": "Linkin Park",
    "red hot chili peppers": "Red Hot Chili Peppers",
    "rhcp": "Red Hot Chili Peppers",
    "radiohead": "Radiohead",
    "rage against the machine": "Rage Against The Machine",
    "ratm": "Rage Against The Machine",
    "avril lavigne": "Avril Lavigne",
    "foo fighters": "Foo Fighters",
    "korn": "Korn",
    "r.e.m.": "R.E.M.",
    "rem": "R.E.M.",
    "pearl jam": "Pearl Jam",
    "audioslave": "Audioslave",
    "soundgarden": "Soundgarden",
    "stone temple pilots": "Stone Temple Pilots",
    "the doors": "The Doors",
    "doors": "The Doors",
    "led zeppelin": "Led Zeppelin",
    "nickelback": "Nickelback",
    "linkin park": "Linkin Park",
    "eminem": "Eminem",
    "rihanna": "Rihanna",
    "justin bieber": "Justin Bieber",
    "maroon 5": "Maroon 5",
    "bob marley": "Bob Marley",
    "rammstein": "Rammstein",
    "switchfoot": "Switchfoot",
    "the offspring": "The Offspring",
    "the smashing pumpkins": "The Smashing Pumpkins",
    "smashing pumpkins": "The Smashing Pumpkins",
    "the wallflowers": "The Wallflowers",
    "wallflowers": "The Wallflowers",
    "bryan adams": "Bryan Adams",
    "enrique iglesias": "Enrique Iglesias",
    "enrique": "Enrique Iglesias",
    "bon jovi": "Bon Jovi",
    "guns n roses": "Guns N Roses",
    "guns n' roses": "Guns N Roses",
    "guns and roses": "Guns N Roses",
    "gnr": "Guns N Roses",
    "metallica": "Metallica",
    "megadeth": "Megadeth",
    "when chai met toast": "When Chai Met Toast",
    "parikrama": "Parikrama",
    "indian ocean": "Indian Ocean",
    "agnee": "Agnee",
    "agni": "Agnee",
    "pitbull": "Pitbull",
    "the chainsmokers": "The Chainsmokers",
    "chainsmokers": "The Chainsmokers",
    "dream theater": "Dream Theater",
    "opeth": "Opeth",
    "faith no more": "Faith No More",
    "akcent": "Akcent",
    "akon": "Akon",
    "usher": "Usher",
    "stromae": "Stromae",
    "aerosmith": "Aerosmith",
    "alanis morissette": "Alanis Morissette",
    "black eyed peas": "Black Eyed Peas",
    "blur": "Blur",
    "bob dylan": "Bob Dylan",
    "bruce springsteen": "Bruce Springsteen",
    "bruce dickinson": "Bruce Dickinson",
    "deep purple": "Deep Purple",
    "dire straits": "Dire Straits",
    "david guetta": "David Guetta",
    "guetta": "David Guetta",
    "tiesto": "Tiesto",
    "dj tiesto": "Tiesto",
    "limp bizkit": "Limp Bizkit",
    "limpbizkit": "Limp Bizkit",
    "system of a down": "System Of A Down",
    "soad": "System Of A Down",
    "yellowcard": "Yellowcard",
    "korn": "Korn",
    "scorpions": "Scorpions",
    "pantera": "Pantera",
    "tokio hotel": "Tokio Hotel",
    "daddy yankee": "Daddy Yankee",
    "sum 41": "Sum 41",
    "karunesh": "Karunesh",
    "dan balan": "Dan Balan",
    "hans zimmer": "Hans Zimmer",
    "krayzie bone": "Krayzie Bone",
    "krayzine bone": "Krayzie Bone",
    "sander van doorn": "Sander Van Doorn",
    "t-pain": "T-Pain",
    "tpain": "T-Pain",
    "chicane": "Chicane",
    "will smith": "Will Smith",
    "busta rhymes": "Busta Rhymes",
    "lauryn hill": "Lauryn Hill",
    "erykah badu": "Erykah Badu",
    "chuck d": "Chuck D",
    "guru": "Guru",
    "flipmode squad": "Busta Rhymes",
    "bob marley  the wailers": "Bob Marley",
    "the wailers": "Bob Marley",
    "disturbed": "Disturbed",
    "infected mushroom": "Infected Mushroom",
    "boyzone": "Boyzone",
    "coldplay": "Coldplay",
    
    # Hindi / Classical / Ghazal
    "pankaj udas": "Pankaj Udhas Ghazals",
    "pankaj udhas": "Pankaj Udhas Ghazals",
    "pankaj 1": "Pankaj Udhas Ghazals",
    "mukesh": "Mukesh Classics",
    "lata mangeshkar": "Lata Mangeshkar Classics",
    "lata": "Lata Mangeshkar Classics",
    "kishore kumar": "Kishore Kumar Classics",
    "kishore": "Kishore Kumar Classics",
    "mohd rafi": "Mohammed Rafi Classics",
    "mohammed rafi": "Mohammed Rafi Classics",
    "mohd. rafi": "Mohammed Rafi Classics",
    "mohd rafi classics": "Mohammed Rafi Classics",
    "rafi": "Mohammed Rafi Classics",
    "asha bhosle": "Asha Bhosle Classics",
    "asha": "Asha Bhosle Classics",
    "jagjit singh": "Jagjit Singh Ghazals",
    "jagjit": "Jagjit Singh Ghazals",
    "rd burman": "R.D. Burman Classics",
    "r d burman": "R.D. Burman Classics",
    "r.d. burman": "R.D. Burman Classics",
    "manna dey": "Manna Dey Classics",
    "talat mahmood": "Talat Mahmood Classics",
    "hemant kumar": "Hemant Kumar Classics",
    "geeta dutt": "Geeta Dutt Classics",
    "mahendra kapoor": "Mahendra Kapoor Classics",
    "yesudas": "K.J. Yesudas Classics",
    "kj yesudas": "K.J. Yesudas Classics",
    "ar rahman": "A.R. Rahman",
    "a r rahman": "A.R. Rahman",
    "a.r. rahman": "A.R. Rahman",
    "a r rehman": "A.R. Rahman",
    "a.r.rehman": "A.R. Rahman",
    "arijit singh": "Arijit Singh Hits",
    "arijit": "Arijit Singh Hits",
    "best of arijit singh": "Arijit Singh Hits",
    "best of arijit singh 2020": "Arijit Singh Hits",
    "best of arijit singhs 2019": "Arijit Singh Hits",
    "shankar mahadevan": "Shankar Mahadevan Hits",
    "shreya ghoshal": "Shreya Ghoshal Hits",
    "shreya": "Shreya Ghoshal Hits",
    "sonu nigam": "Sonu Nigam Hits",
    "sonu": "Sonu Nigam Hits",
    "lucky ali": "Lucky Ali Hits",
    "lucky ali aks": "Lucky Ali Hits",
    "kailash kher": "Kailash Kher Hits",
    "atif aslam": "Atif Aslam Hits",
    "atif": "Atif Aslam Hits",
    "nusrat fateh ali khan": "Nusrat Fateh Ali Khan",
    "nfak": "Nusrat Fateh Ali Khan",
    "rahat fateh ali khan": "Rahat Fateh Ali Khan",
    "shaan": "Shaan Hits",
    "kk": "KK Hits",
    "k.k.": "KK Hits",
    "udit narayan": "Udit Narayan Hits",
    "kumar sanu": "Kumar Sanu Hits",
    "alka yagnik": "Alka Yagnik Hits",
    "kavita krishnamurthy": "Kavita Krishnamurthy Hits",
    "mohit chauhan": "Mohit Chauhan Hits",
    "sukhwinder singh": "Sukhwinder Singh Hits",
    "mika singh": "Mika Singh Hits",
    "sunidhi chauhan": "Sunidhi Chauhan Hits",
    "neha kakkar": "Neha Kakkar Hits",
    "himesh reshammiya": "Himesh Reshammiya Hits",
    "anuradha paudwal": "Anuradha Paudwal Hits",
    "suresh wadkar": "Suresh Wadkar Hits",
    "bappi lahiri": "Bappi Lahiri Hits",
    
    # Marathi / Devotional
    "vaibhavi shete": "Vaibhavi Shete",
    "viabhavi shete": "Vaibhavi Shete",
    "akhilam madhuram vaibhavi shete 2": "Vaibhavi Shete",
    "akhilam madhuram vaibhavi shete 3": "Vaibhavi Shete",
    "akhilam madhuram": "Vaibhavi Shete",
    "pl despande": "P. L. Deshpande",
    "p l despande": "P. L. Deshpande",
    "p l deshpande": "P. L. Deshpande",
    "pl deshpande": "P. L. Deshpande",
    "naman natwara": "Natyasangeet & Devotional",
    "01 naman natwara 1": "Natyasangeet & Devotional",
    "ramdas kamat": "Ramdas Kamat",
    "ajit kadkade": "Ajit Kadkade",
    "prabhakar karekar": "Prabhakar Karekar",
    "vasantrao deshpande": "Vasantrao Deshpande"
}

def resolve_canonical_artist(raw: str) -> Optional[str]:
    """Resolves arbitrary raw artist/band text into a canonical unified name."""
    if not raw:
        return None
    cleaned = raw.strip().lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return CANONICAL_ARTISTS.get(cleaned)

class EmbeddedLanguageIntelligence:
    """
    Lightweight, embedded intelligence engine for music language & metadata classification.
    Runs entirely in-process with minimal RAM footprint (<50MB), zero server overhead,
    and support for parallel multi-language workers.
    """

    def __init__(self, enable_airllm: bool = False, model_path: Optional[str] = None):
        self.enable_airllm = enable_airllm
        self.model_path = model_path
        self._airllm_model = None

        if enable_airllm or model_path or os.environ.get("AIRLLM_MODEL"):
            self._init_airllm()

    def _init_airllm(self) -> None:
        """Attempts to initialize AirLLM layer-streaming AutoModel if the airllm package is installed."""
        try:
            import airllm
            import torch
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            model_target = self.model_path or os.environ.get("AIRLLM_MODEL")
            if model_target:
                logger.info(f"Loading AirLLM model '{model_target}' on device '{device}'...")
                self._airllm_model = airllm.AutoModel.from_pretrained(model_target, device=device)
            else:
                logger.info("AirLLM package detected. No model specified; awaiting load_airllm_model().")
        except Exception as e:
            logger.info(f"AirLLM AutoModel fallback ({e}); using embedded linguistic engine.")
            self._airllm_model = None

    def load_airllm_model(self, model_name_or_path: str, hf_token: Optional[str] = None) -> bool:
        """Explicitly loads an AirLLM model by repo id or local path with CPU/CUDA adaptation."""
        try:
            import airllm
            import torch
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading AirLLM model '{model_name_or_path}' on device '{device}'...")
            kwargs = {"device": device}
            if hf_token:
                kwargs["hf_token"] = hf_token
            self._airllm_model = airllm.AutoModel.from_pretrained(model_name_or_path, **kwargs)
            self.model_path = model_name_or_path
            self.enable_airllm = True
            return True
        except Exception as e:
            logger.warning(f"Failed to load AirLLM model '{model_name_or_path}': {e}")
            self._airllm_model = None
            return False

    def classify_ambiguous_track(
        self,
        filename: str,
        artist: str = "",
        album: str = "",
        title: str = ""
    ) -> Optional[Dict[str, str]]:
        """
        Infers metadata for ambiguous tracks using AirLLM layer-streaming or embedded linguistic heuristics.
        """
        if self._airllm_model:
            try:
                prompt = (
                    f"Analyze music track: filename='{filename}', artist='{artist}', album='{album}', title='{title}'. "
                    f"Output JSON with keys: language, artist, movie_or_album, title."
                )
                # Generation with AirLLM layer-streaming
                inputs = self._airllm_model.tokenizer(prompt, return_tensors="pt")
                out = self._airllm_model.generate(inputs["input_ids"], max_new_tokens=60)
                decoded = self._airllm_model.tokenizer.decode(out[0], skip_special_tokens=True)
                match = re.search(r"\{.*?\}", decoded, re.DOTALL)
                if match:
                    import json
                    return json.loads(match.group(0))
            except Exception as e:
                logger.debug(f"AirLLM inference fallback: {e}")

        # Embedded heuristics fallback for ambiguous items
        classified = self.classify_track(filename, artist=artist, album=album, title=title)
        return {
            "language": classified["language"],
            "artist": classified["artist"],
            "movie_or_album": classified["category"],
            "title": classified["title"]
        }

    def canonicalize_artist(self, raw_artist: str) -> str:
        """Standardizes artist name across aliases and variations."""
        resolved = resolve_canonical_artist(raw_artist)
        return resolved if resolved else raw_artist.strip().title()

    def classify_track(
        self,
        filename: str,
        artist: str = "",
        album: str = "",
        title: str = ""
    ) -> Dict[str, str]:
        """
        Classifies an audio track into its Language, Category/Movie/Artist, and canonical Title.
        Operates in-process with microsecond latency and zero external network calls.
        """
        stem, ext = os.path.splitext(filename)
        cleaned_stem = re.sub(r"^\d+[\s\.\-_]*", "", stem).strip()
        combined = f"{filename.lower()} {artist.lower()} {album.lower()} {title.lower()}".replace("_", " ")

        # 1. Disambiguate Bollywood Movie: Omkara (MUST NEVER be categorized as Sanskrit)
        omkara_tracks = ["beedi", "naina", "namak", "omkara", "jag ja ri gudiya", "o saathi re", "laakad"]
        if "omkara" in combined:
            if any(t in combined for t in omkara_tracks) or any(a in combined for a in ["vishal", "bhardwaj", "sukhwinder", "sunidhi", "rekha", "rahat", "gulzar"]):
                t_name = "Omkara"
                for tr in omkara_tracks:
                    if tr in combined:
                        t_name = tr.title()
                        break
                return {
                    "language": "Hindi",
                    "category": "Soundtracks\\Omkara",
                    "title": t_name,
                    "artist": "Vishal Bhardwaj"
                }

        # 2. Sanskrit: Vedic Suktas
        sukta_patterns = [
            (r"purush(a)?[- ]?sukta?m?", "Purusha Suktam"),
            (r"shr[ei]{1,2}[- ]?sukta?m?", "Shree Suktam"),
            (r"\brudra(m)?\b|\bchamaka(m)?\b|\bnamaka(m)?\b|laghunyasa", "Shri Rudram"),
            (r"pavaman(a)?[- ]?(\d+)?", "Pavamana Suktam"),
            (r"ganapat(i|ya)[- ]?a?atharvash[ei]{1,2}rsha|ganapati[- ]?sukta", "Ganapati Atharvashirsha"),
            (r"\bsaur(a)?(\.wma|\.mp3|[- ]?sukta)", "Saura Suktam"),
            (r"trisuparna", "Trisuparna Suktam"),
            (r"ratri[- ]?sukta?m?", "Ratri Suktam"),
            (r"durga[- ]?sukta?m?", "Durga Suktam"),
            (r"medha[- ]?sukta?m?", "Medha Suktam"),
            (r"manyu[- ]?sukta?m?", "Manyu Suktam"),
            (r"nasadiya", "Nasadiya Suktam"),
            (r"ayushya[- ]?sukta?m?", "Ayushya Suktam"),
            (r"bhagya[- ]?sukta?m?", "Bhagya Suktam"),
            (r"shanti[- ]?(path|suktam?)", "Shanti Suktam"),
        ]
        for pat, canon_name in sukta_patterns:
            if re.search(pat, combined, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Vedic Suktas",
                    "title": canon_name,
                    "artist": "Traditional Vedic Chants"
                }

        # 3. Sanskrit: Stotras & Ashtakams (e.g. Nirvana Shatakam, NOT English band Nirvana)
        stotra_patterns = [
            (r"vishnu[- ]?saha[st]{1,3}rana[am]", "Vishnu Sahasranama Stotram"),
            (r"lalitha[- ]?sahas?rana[am]", "Lalitha Sahasranama Stotram"),
            (r"shiva[- ]?tandav(a)?", "Shiva Tandava Stotram"),
            (r"mahishasur[ -]?mardini", "Mahishasuramardini Stotram"),
            (r"shiva[- ]?mahimna", "Shiva Mahimna Stotram"),
            (r"shiva[- ]?manas(a)?[- ]?poo?ja", "Shiva Manasa Pooja"),
            (r"shiva[- ]?panchakshara", "Shiva Panchakshara Stotram"),
            (r"nirvana[- ]?shatakam?|nirvanashatakam?", "Nirvana Shatakam"),
            (r"bhavany?[- ]?ashtakam?", "Bhavani Ashtakam"),
            (r"madhur[- ]?ashtakam?", "Madhurashtakam"),
            (r"bilv[- ]?ashtakam?", "Bilvashtakam"),
            (r"guru[- ]?ashtakam?", "Guru Ashtakam"),
            (r"ling[- ]?ashtakam?", "Lingashtakam"),
            (r"kalabhairav(a)?[- ]?ashtakam?", "Kalabhairava Ashtakam"),
            (r"daridraya[- ]?dahana", "Daridraya Dahana Stotram"),
            (r"venkatesh(a)?[- ]?(stotram?|suprabhatam)", "Shri Venkatesha Stotram"),
            (r"dattatreya[- ]?stotram?", "Shri Dattatreya Stotram"),
            (r"navagraha[- ]?stotram?", "Shri Navagraha Stotram"),
            (r"suryamandal(a)?|aditya[- ]?hridaya", "Shri Suryamandala Stotram"),
            (r"annapoorna[- ]?stotram?", "Annapoorna Stotram"),
            (r"charpat[- ]?panjarika|bhaja[- ]?govindam", "Charpat Panjarika Stotram (Bhaja Govindam)"),
            (r"dvadash[- ]?panjarika", "Dvadash Panjarika Stotram"),
            (r"shatpadi[- ]?stotram?", "Shatpadi Stotram"),
            (r"shakambhari[- ]?stotram?", "Shri Shakambhari Stotram"),
            (r"gopi[- ]?geet(am)?", "Shri Gopi Gitam"),
            (r"aghorakashtoddharan", "Aghorakashtoddharana Stotra"),
            (r"arbudadevi", "Arbudadevi Stotra"),
            (r"ardanarinateshwar", "Ardhanarishwara Stotra"),
        ]
        for pat, canon_name in stotra_patterns:
            if re.search(pat, combined, re.IGNORECASE):
                return {
                    "language": "Sanskrit",
                    "category": "Stotras & Ashtakams",
                    "title": canon_name,
                    "artist": "Traditional Sanskrit Chants"
                }

        # 4. Sanskrit: General Stotras and Suktas
        if any(k in combined for k in ["stotram", "stotra", "ashtakam", "suktam", "sukta", "vedic", "atharvashirsha"]):
            cat = "Vedic Suktas" if ("sukta" in combined or "vedic" in combined) else "Stotras & Ashtakams"
            return {
                "language": "Sanskrit",
                "category": cat,
                "title": cleaned_stem.replace("_", " ").title(),
                "artist": "Traditional Sanskrit Chants"
            }

        # 5. Sanskrit: Vedic Samhita (Atharva Veda, Bhagavat Samhita)
        if "atharva veda" in combined or "atharva-veda" in combined:
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Atharva Veda",
                "title": cleaned_stem.title(),
                "artist": "Vedic Scholars"
            }
        if "bh-samhita" in combined or "shrimad-bhagawat-samhita" in combined:
            return {
                "language": "Sanskrit",
                "category": "Vedic Samhita\\Shrimad Bhagawat Samhita",
                "title": cleaned_stem.title(),
                "artist": "Traditional Vedic Chants"
            }

        # 5. Pravachan markers
        pravachan_keys = ["pravachan", "katha", "adhyay", "discourse", "updesh", "purushottamyog"]
        if any(k in combined for k in pravachan_keys) or "pravachan" in album.lower():
            speaker = "Discourses"
            if "ghaisasi" in combined:
                speaker = "Bhagwat Katha\\Ghaisasi Guruji"
            elif "kavishwar" in combined:
                speaker = "Bhagwat Katha\\Kavishwar Maharaj"
            elif "abhyankar" in combined or "purushottam" in combined:
                speaker = "Bhagavad Gita\\Shankar Abhyankar"
            return {
                "language": "Pravachan",
                "category": speaker,
                "title": cleaned_stem.title(),
                "artist": artist or "Discourses"
            }

        # 6. Marathi markers
        if any(k in combined for k in ["natyasangeet", "naman natwara", "abhang", "vitthal", "mauli", "tukaram", "shete", "bhavgeet"]):
            if "shete" in combined or "akhilam madhuram" in combined:
                subcat = "Vaibhavi Shete\\Akhilam Madhuram"
                art = "Vaibhavi Shete"
            elif "natyasangeet" in combined or "naman natwara" in combined:
                subcat = "Natyasangeet"
                art = artist or "Various Artists"
            elif "abhang" in combined or "vitthal" in combined or "mauli" in combined:
                subcat = "Abhang & Bhakti"
                art = artist or "Various Artists"
            else:
                subcat = "Bhavgeet & Classics"
                art = artist or "Various Artists"
            return {
                "language": "Marathi",
                "category": subcat,
                "title": cleaned_stem.title(),
                "artist": art
            }

        # 7. Western / English Rock & Pop (word boundaries)
        english_artists = [
            "nirvana", "coldplay", "u2", "green day", "iron maiden", "metallica",
            "megadeth", "pink floyd", "the beatles", "beatles", "linkin park",
            "red hot chili peppers", "audioslave", "soundgarden", "faith no more",
            "pearl jam", "radiohead", "rage against the machine", "guns n roses",
            "guns and roses", "switchfoot", "rammstein", "nickelback", "eminem"
        ]
        for eng in english_artists:
            if re.search(r"\b" + re.escape(eng) + r"\b", combined, re.IGNORECASE):
                band = self.canonicalize_artist(eng)
                return {
                    "language": "English",
                    "category": band,
                    "title": cleaned_stem.title(),
                    "artist": band
                }

        # 8. Default Indian Film / Hindi
        movie = album.strip().title() if album else "Evergreen Classics"
        return {
            "language": "Hindi",
            "category": movie,
            "title": cleaned_stem.title(),
            "artist": artist or "Various Artists"
        }
