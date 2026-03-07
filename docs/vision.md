# Auralis Vision

## North Star
**The Autonomous, High-Fidelity Music Neural Network.**
Auralis is not just a music player; it is an intelligent, self-organizing system that understands your music library at a deep, structural level. It bridges the gap between local high-fidelity archives and the metadata-rich world of streaming, providing a "best of both worlds" experience.

## Pipeline Laws (The "Iron Triangle")
1.  **Test Fortress:** All code (Core, GUI, CLI, Utils) must be covered by tests. Target coverage: 95%. Mocking is mandatory for UI components. No regression is acceptable.
2.  **Lint Zero:** Zero tolerance for linting errors. `flake8` and `mypy` (strict mode, `disallow_untyped_defs = True`, no global ignores) must pass clean.
3.  **Complexity Cap:** No function shall exceed a Cyclomatic Complexity of 10. Refactor ruthlessly.
4.  **Latest Stable Env Only:** Always use the latest stable environment and dependencies unless strictly impossible.

## Definition of Done (DoD)
A task is only "Done" when it meets the following atomic criteria:
-   [ ] **Tested:** Unit tests added/updated covering happy paths and edge cases.
-   [ ] **Linted:** Passes all static analysis checks.
-   [ ] **Optimized:** O(n) or better complexity verified.
-   [ ] **Secured:** Input sanitized, dependencies checked.
-   [ ] **Documented:** Docstrings and relevant markdown updated.

## Ideal State
-   **Zero-Touch Organization:** Drop a folder of chaotic MP3s, and Auralis sorts, tags, and artworks them instantly.
-   **Neural Audio Understanding:** Identifies Ragas, Cover Songs, and Moods using Zero-Shot Transformers (CLAP/MERT) without relying on external databases.
-   **Universal Playback:** Plays FLAC, MP3, WAV, OGG, and streams seamlessly.
-   **Deep Metadata:** Lyrics, artist bios, and similar tracks are fetched automatically.
-   **Fluid UI:** A responsive, modern interface (PyQt6/wxPython) that feels native on every OS.


## Phase 5 Expansion Laws
- **Modularity First**: All new ecosystem features must be built as optional modules.
- **Performance Budget**: Background services (Sync, DJ Tools, AI) must not degrade main UI thread responsiveness.
- **Offline Fallback**: Cloud and Social features must fail gracefully without internet.

## AI Feasibility Report
### Advanced Music Analysis with Hugging Face

This report analyzes the feasibility of integrating Hugging Face (HF) models into Auralis for advanced audio analysis, including Raga identification, Cover Song Identification (CSI), and detailed music tagging.

**Executive Summary:** High for General Tagging; Moderate for Raga/Cover Identification.
Integrating Hugging Face `transformers` models is technically feasible and would significantly enhance Auralis's capabilities. However, it introduces substantial dependencies (`torch`, `transformers`) and resource requirements (memory/CPU).

**1. General Music Tagging & Classification**
**Goal:** Identify genre, mood, instruments, and other details.
**Recommended Model:** `m-a-p/MERT-v1-95M` or `laion/clap-htsat-unfused`
*   **MERT (Music Understanding):** A powerful model trained on large-scale music datasets. It can extract robust features for downstream tasks like genre classification, mood detection, and instrument identification.
*   **CLAP (Contrastive Language-Audio Pretraining):** Allows **Zero-Shot Classification**. You can provide a list of arbitrary text tags (e.g., "Happy Rock", "Sad Jazz", "Sitar Solo") and the model will predict the most likely match for the audio. This is extremely flexible.
**Implementation:**
-   Use `transformers.pipeline("audio-classification", model="m-a-p/MERT-v1-95M")` (if supported directly) or use the model to extract embeddings and classify with a lightweight head.
-   For CLAP: Pass audio + list of candidate tags -> Get probabilities.

**2. Raga Identification (Indian Classical Music)**
**Goal:** Identify the Raga of a song.
**Feasibility:**
-   **Direct Model:** There is currently no "plug-and-play" pre-trained Raga classifier on Hugging Face.
-   **Approach 1 (Zero-Shot):** Use **CLAP** (`laion/clap-htsat-unfused`). Provide raga names as text prompts (e.g., "Indian Classical Raga Bhairav", "Raga Yaman", "Raga Todi"). The model's training data likely includes some Indian Classical Music, so it may work for popular ragas.
-   **Approach 2 (Fine-Tuning):** Use **MERT** embeddings and train a small classifier (Random Forest or simple Neural Net) on the **CompMusic Carnatic/Hindustani dataset**. This requires a training pipeline but yields high accuracy (88-97% as per recent research).
**Recommendation:** Start with **CLAP Zero-Shot** as a proof-of-concept. If accuracy is low, proceed with fine-tuning MERT.

**3. Cover Song Identification (CSI) & Original/Singer Verification**
**Goal:** Determine if a song is an Original or a Cover.
**Challenges:**
-   "Original" is a semantic concept (who released it first?).
-   "Cover" implies same composition, different performance.
**Approaches:**
1.  **Audio Similarity (Embeddings):**
    -   Use **MERT** to generate an embedding vector for the track.
    -   Compare this vector against a known database of "Original" embeddings (if available).
    -   *Limitation:* Requires a reference database.
2.  **Singer Identification:**
    -   Use a **Speaker/Singer Identification** model (e.g., `speechbrain/spkrec-ecapa-voxceleb` or `microsoft/wavlm-base-plus-sv`).
    -   If metadata says "Artist: Queen", verify if the voice matches the known voice embedding of "Freddie Mercury".
    -   *Feasibility:* High complexity. Requires a database of artist voice signatures.
3.  **Live vs. Studio Classification:**
    -   Train a classifier (using MERT features) to distinguish "Studio Recording" vs "Live Performance" vs "Cover/Acoustic".
**Recommendation:**
-   Implement **Audio Similarity** checking using MERT embeddings. If you have the "Original" file (e.g., in your library), you can detect duplicates/covers by high semantic similarity but low acoustic fingerprint match (AcoustID would fail, MERT would succeed).

**Technical Architecture Proposal:**
-   **New Module:** `src/services/ai_service.py` with `AIService` class for lazy loading and analysis.
-   **Dependencies:** `torch`, `transformers`, `librosa`, `numpy`.
-   **Performance Considerations:** CPU inference (1-5s per song), RAM usage ~1GB active. Keep as optional plugin.
-   **Next Steps:** Implement `analyze_raga_zero_shot`, `analyze_mood_genre` in `prototypes/ai_demo.py`.

## Process Flow

### 1. Start Application
**CLI Mode:** `python auralis.py [command] [args]` -> Parses arguments -> Executes specific command module (`src.cli.cli_main.py`).
**GUI Mode:** `python auralis.py` -> Initializes `QApplication` -> Creates `MainWindow` (`src.gui.pyqt.main_window.py`) -> Displays UI.

### 2. Stage 1: Scan & Rename (Discovery)
**Goal:** Find music files and extract basic metadata.
**Process:** User Input (Directories) -> MusicScanner (`src/core/scanner.py`) -> Recursive Directory Walk -> Filter Files (.mp3, .flac) -> Process File (MD5 Hash, Mutagen ID3/Vorbis Metadata, Fallback Filename Parse) -> Emit 'file_found' Signal -> Result (List of File Info Dictionaries).

### 3. Stage 2: Organize (Structure)
**Goal:** Move and rename files based on metadata and user preferences.
**Process:** Input (Scanned Files + Options) -> MusicOrganizer (`src/core/organizer.py`) -> Audio Similarity Check (Optional: Analyze Content, Group Similar, Keep Best Quality) -> Duplicate Check (Metadata: Keep Higher Quality) -> Determine Destination Path (Template or Default Language/Filename) -> Action (Move or Manual_Review) -> Result (Organized Directory Structure).

### 4. Stage 3: Metadata Enhancement (Enrichment)
**Goal:** Fetch additional metadata (Cover Art, Lyrics, BPM) from online sources.
**Process:** Input (Organized Files + Options) -> MetadataService (`src/services/metadata_service.py`) -> For Each File: Check Cache -> Query Sources (MusicBrainz, Discogs, Spotify, Last.fm) -> Merge Metadata -> Fetch Additional (Cover Art, Lyrics, Bio) -> Audio Analysis (Optional: BPM, Key, Mood) -> Save to File (Mutagen) -> Result (Fully Tagged & Enriched Music Files).

## User Guide

### Installation
1.  Clone repository: `git clone https://github.com/patternseekers/auralis.git && cd auralis`
2.  Install dependencies: `pip install -r requirements.txt` (or `pip install -e .[all]` for optional features).
3.  Run application: `python auralis.py`

### Library Scanning
1.  Navigate to the **Scan** tab.
2.  Click **Select Folder** to choose your music directory.
3.  Click **Start Scan** to index your files.

### Metadata Enhancement
1.  Select files in the library view.
2.  Click **Update Metadata**. Configure options (Force Update, Fetch Lyrics). Click **Start**.
3.  Supported Sources: MusicBrainz, Discogs, Spotify, Last.fm.

### Organization
1.  Go to the **Organize** tab. Select source files and destination directory.
2.  Select naming pattern and click **Organize Files**.

### Audio Similarity
1.  Go to the **Similarity** tab. Select folder to analyze.
2.  Choose **Find Duplicates** or **Group by Similarity**.

### Lyrics
1.  Providers: Genius, AZLyrics, Tekstowo.
2.  Saving: Embedded by default. Enable **Save LRC File** to save separately.

### Configuration
Settings are stored in `~/.auralis/config.json`. You can use a `.env` file for secrets (`SPOTIPY_CLIENT_ID`, `LASTFM_API_KEY`, `DISCOGS_TOKEN`).

### Troubleshooting
-   **"FPcalc not found"**: Install `fpcalc` via AcoustID (Windows) or package manager (macOS/Linux).
-   **Metadata Updates Fail**: Check connection, API keys, and file permissions.
-   **GUI Freezes**: Background processes may cause lag on large libraries; test with smaller sub-folders.
-   **Lyrics Not Found**: Verify tags, search manually, enable fuzzy matching.

## API Documentation (Swagger)
```yaml
openapi: 3.0.0
info:
  title: Auralis Remote API
  version: 1.0.0
  description: API for Auralis Remote Control and Data Access
paths:
  /status:
    get:
      summary: Get system status
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatusResponse'
  /scan:
    post:
      summary: Trigger a media scan
      responses:
        '202':
          description: Scan accepted
  /organize:
    post:
      summary: Trigger media organization
      responses:
        '202':
          description: Organize accepted
  /library:
    get:
      summary: Get library contents with pagination
      parameters:
        - in: query
          name: page
          schema:
            type: integer
            default: 1
        - in: query
          name: limit
          schema:
            type: integer
            default: 50
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Track'
  /track/{id}:
    get:
      summary: Get track by ID
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Track'
components:
  schemas:
    StatusResponse:
      type: object
      properties:
        status:
          type: string
        uptime:
          type: integer
    Track:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        artist:
          type: string
        album:
          type: string
```
