# Operational Playbook: Iterative Dry-Run Music Library Master Engine

## 1. Executive Strategy & Guiding Principles
- **Zero Premature Disk I/O:** No audio file will be moved, renamed, rewritten, or deleted until all decision rules and classification logic have been executed and verified in pure **Dry-Run mode**.
- **Master Backup Immutability:** 
  - `F:\Auralis_Master_Vault` (Cold archive: 10,701 intact raw tracks) and `master_cross_drive_catalog.db` (50,269 cataloged entries) remain untouched as our ultimate recovery baselines.
  - The working pool on NVMe (`D:\Songs`) will be operated on cleanly once the dry-run blueprint is verified.
- **Deterministic & Predictable Decision Making:**
  - Fast-path deterministic logic handles 90%+ of standard tracks.
  - Runtime LLM (AirLLM / Transformers / Local SLM) handles ambiguous tracks (`Track 01`, unknown artist, unclassified sacred chants).
  - Every LLM decision is persisted into a local decision cache (`engine_decision_cache.json` / SQLite) so the system yields the exact same output across runs without variance.
- **Interactive Verification Artifact:**
  - Every dry-run iteration outputs a self-contained, interactive HTML dashboard (`dry_run_review.html`) detailing every track's source, proposed destination, extracted metadata, tag plan, confidence score, and LLM rationale, with a feedback mechanism for user review.

---

## 2. 5-Stage Engine Architecture (Executed 1 Step at a Time in Dry Run)

```
[Raw Audio Pool]
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 1: Physical Inspection & Audio Stream Hashing     │ ──► Compute bitrates, formats, & exact audio stream MD5
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 2: Deep Audio Listening & Acoustic Introspection │ ──► Speech-to-Text Whisper transcription & acoustic lyrics
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 3: Linguistic & Sacred Taxonomy Classification   │ ──► Language detection + Sanskrit Suktas vs Stotras vs Samhita
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 4: AirLLM Disambiguation & Decision Caching      │ ──► Local LLM resolves true song name from lyrics & metadata
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 5: Dynamic Threshold & Canonical Path Generation │ ──► >=3 tracks -> Dedicated Folder; <3 -> Singles Collection
└────────────────────────────────────────────────────────┘
      │
      ▼
[Self-Contained HTML Review Dashboard (dry_run_review.html)]
      │
      ▼ (Only upon user approval)
[Execute Physical Atomic Changes via `auralis.py master-organize`]
```

---

## 3. Detailed Specifications for Each Stage

### Stage 1: Physical Inspection & Stream Hashing
- Multi-format support: MP3, WMA/ASF, FLAC, M4A, OGG.
- Compute raw audio stream MD5 hash (ignoring ID3/ASF tag blocks).
- Quality comparator: Automatically maps duplicate files and marks the highest bitrate (e.g., 320 kbps vs. 128 kbps) as the primary track while marking redundant copies for archival.

### Stage 2: Deep Audio Listening & Acoustic Introspection (Zero "Track 01" Policy)
- **Zero Generic Name Policy:** No file may ever be named or left as `Track 01`, `Track 1`, `Audio 1`, etc.
- **Audio Waveform Listening (Speech-to-Text / Whisper):**
  - When a file has a generic name (`Track 01`, `Track 02`, etc.) or corrupt/missing metadata, the engine loads the audio waveform directly into the local Whisper speech-to-text model.
  - Transcribes vocal segments (e.g., from 30s–90s where the primary chorus/mukhda occurs) to extract spoken or sung lyrics.
  - Extracts the exact song language directly from the audio frequency mel-spectrogram.
- **Discographical Introspection:**
  - Where compilation CD metadata exists (e.g. MCDI table or Album title + Track Number), maps the track to the exact master tracklist (e.g. *Independence Rock XX* Track 9 -> *Ashutosh Pathak - Europa*).
  - Feeds the transcribed lyrics (e.g. *"Hum jee lenge bin tumhare... kyunki tum meri zindagi ho"*) to the intelligence layer to identify the real song title, movie/album, composer, and singers.

### Stage 3: Linguistic & Sacred Taxonomy Classification
- Strict Language separation: `Sanskrit`, `Hindi`, `Marathi`, `English`, `Pravachan`.
- **Sanskrit Deep Taxonomy:**
  - `Sanskrit / Vedic Suktas`: *Purusha Suktam*, *Shree Suktam*, *Shri Rudram / Namakam & Chamakam*, *Pavamana Suktam*, *Ganapati Atharvashirsha*, *Saura Suktam*, *Trisuparna Suktam*, *Ratri Suktam*.
  - `Sanskrit / Stotras & Ashtakams`: *Vishnu Sahasranama*, *Nirvana Shatakam*, *Shiva Tandava*, *Mahishasuramardini*, *Bilvashtakam*, *Madhurashtakam*, *Annapoorna Stotram*, *Bhavani Ashtakam*.
  - `Sanskrit / Vedic Samhita`: *Rigveda*, *Atharva Veda*, *Yajurveda*, *Samaveda*, *Shrimad Bhagawat Samhita*.
  - `Sanskrit / Upanishads`: *Chakshushopanishad*, etc.
- **Bollywood & Western Disambiguation:**
  - Bollywood movie *Omkara* -> `Hindi / Soundtracks / Omkara` (Never Sanskrit).
  - American rock band Nirvana -> `English / Nirvana` (Never Sanskrit).

### Stage 4: AirLLM Disambiguation & Decision Caching
- When confidence is $< 0.85$ or track is ambiguous, invoke the local LLM engine.
- Input prompt: File duration, existing metadata tags, parent directory path, file name.
- Output: Strict JSON schema `{ "language": "...", "category": "...", "title": "...", "artist": "...", "confidence": 0.95 }`.
- **Decision Cache:** Persisted to `engine_decision_cache.json`. Subsequent runs immediately load the cached decision, guaranteeing 100% deterministic predictability.

### Stage 5: Dynamic Threshold & Canonical Path Generation
- **Folder Creation Threshold Rule:**
  - If a category/artist/movie has $\ge 3$ tracks:
    - Path: `D:\Songs\organized\[Language]\[Category]\[Track_Title].mp3`
  - If a category/artist/movie has $< 3$ tracks:
    - Path: `D:\Songs\organized\[Language]\Singles & Compilations\[Artist_or_Category] - [Track_Title].mp3`
  - Eliminates the 850+ single-song folders that cluttered previous runs.

---

## 4. Verification & Feedback Interface: `dry_run_review.html`
- Standalone HTML page with embedded search, category filters, and sample playback links.
- Interactive controls:
  - Table displaying: Current Path, Proposed Organized Path, Detected Language, Category, Clean Artist, Clean Title, Bitrate, Confidence, Decision Source (Rule vs. AirLLM).
  - Status badges: `Approved`, `Flagged for Change`.
  - Export feedback button to JSON so modifications can be fed straight back into the rules engine.

---

## 5. Execution Protocol
1. **Curate and Refine Code** in `src/engine/` step by step.
2. Run Stage 1 & 2 tests + dry run.
3. Run Stage 3 & 4 tests + dry run.
4. Run Stage 5 dry run and generate `dry_run_review.html`.
5. User inspects `dry_run_review.html`.
6. Only upon explicit sign-off, trigger `python auralis.py master-organize --apply`.
