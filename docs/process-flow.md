# Auralis Process Flow

This document outlines the user interaction and internal process flow of the Auralis application.

## 1. Start Application

The user initiates the application via CLI or GUI.

**CLI Mode:**
`python auralis.py [command] [args]` -> Parses arguments -> Executes specific command module (`src.cli.cli_main.py`).

**GUI Mode:**
`python auralis.py` -> Initializes `QApplication` -> Creates `MainWindow` (`src.gui.pyqt.main_window.py`) -> Displays UI.

---

## 2. Stage 1: Scan & Rename (Discovery)

**Goal:** Find music files and extract basic metadata.

**User Interaction (GUI):**
1.  User selects "Stage 1: Scan & Rename" tab.
2.  User adds directories to the list.
3.  User clicks "Start Scan".

**Process Flow:**
```
[User Input: Directories]
       |
       v
[MusicScanner (src/core/scanner.py)]
       |
       +--> [Recursive Directory Walk]
       |       |
       |       v
       |    [Filter Files]
       |       |--> Check Extension (.mp3, .flac, etc.)
       |       |--> Check Exclusions (System folders, hidden files)
       |       v
       |    [Process File]
       |       |--> Calculate File Hash (MD5)
       |       |--> Extract Metadata (Mutagen)
       |       |       |--> ID3 (MP3) / Vorbis (FLAC)
       |       |       |--> Fallback: Parse Filename (Artist - Title)
       |       v
       +--> [Emit 'file_found' Signal]
       |
       v
[Result: List of File Info Dictionaries]
```

---

## 3. Stage 2: Organize (Structure)

**Goal:** Move and rename files based on metadata and user preferences.

**User Interaction (GUI):**
1.  User selects "Stage 2: Organize" tab.
2.  User selects Destination Directory.
3.  User configures options:
    -   "Organize by Language"
    -   "Detect Audio Similarity"
    -   "Handle Duplicates"
4.  User clicks "Start Organize" (or Dry Run).

**Process Flow:**
```
[Input: Scanned Files + Options]
       |
       v
[MusicOrganizer (src/core/organizer.py)]
       |
       +--> [Audio Similarity Check (Optional)]
       |       |--> Analyze Audio Content
       |       |--> Group Similar Files
       |       |--> Keep Best Quality (Bitrate/Format/Size)
       |       v
       +--> [Process Each File]
               |
               v
            [Duplicate Check (Metadata)]
               |--> If Duplicate Found:
               |       |--> Compare Quality
               |       |--> Keep Higher Quality
               |       |--> Mark Lower Quality as Duplicate
               |
               v
            [Determine Destination Path]
               |--> Check Template (e.g., "{artist}/{album}/{title}")
               |       OR
               |--> Default Structure:
               |       |--> [Language Detection] (Optional: Audio/Metadata)
               |       |       |--> "English", "Spanish", "Instrumental", etc.
               |       |       v
               |       |--> /Destination/{Language}/
               |       |
               |       v
               |    [Filename Formatting]
               |       |--> "{Title} - {Artist}.{ext}"
               |
               v
            [Action]
               |--> Move File to Destination
               |       OR
               |--> Copy to "Manual_Review" (if metadata missing)
               |
               v
[Result: Organized Directory Structure]
```

---

## 4. Stage 3: Metadata Enhancement (Enrichment)

**Goal:** Fetch additional metadata (Cover Art, Lyrics, BPM) from online sources.

**User Interaction (GUI):**
1.  User selects "Stage 3: Metadata" tab.
2.  User configures providers (MusicBrainz, Discogs, Spotify, Last.fm).
3.  User enables features:
    -   "Fetch Lyrics"
    -   "Fetch Cover Art"
    -   "Analyze Audio" (BPM/Key)
4.  User clicks "Start Update".

**Process Flow:**
```
[Input: Organized Files + Options]
       |
       v
[MetadataService (src/services/metadata_service.py)]
       |
       v
    [For Each File]
       |
       +--> [Check Cache] (Skip if recent/valid)
       |
       +--> [Query Metadata Sources] (Parallel/Sequential)
       |       |--> MusicBrainz/AcoustID (Fingerprint/Search)
       |       |--> Discogs (Search)
       |       |--> Spotify (Search)
       |       |--> Last.fm (Search)
       |       v
       |    [Merge Metadata] (Update Artist, Album, Title, Year, Genre)
       |
       +--> [Fetch Additional Content]
       |       |--> [Cover Art] (Download from URL -> Embed)
       |       |--> [Lyrics] (Fetch -> Embed)
       |       |--> [Bio] (Fetch -> Embed as Comment)
       |
       +--> [Audio Analysis] (Optional)
       |       |--> Detect BPM
       |       |--> Detect Key
       |       |--> Detect Mood
       |
       v
    [Save to File] (Write Tags using Mutagen)
       |
       v
[Result: Fully Tagged & Enriched Music Files]
```
