# Auralis Backlog (v10.0.0 - Multi-Tier Authentic Artwork & Natyasangeet Expansion)

## 🎯 Current Sprint: Multi-Tier Authentic Artwork Resolution, Zero-Cross-Contamination & Natyasangeet Expansion
**North Star:** Deep Per-File Analysis, Deezer 1000x1000 & iTunes 600x600 Authentic Cover Art Integration, Elimination of Cross-Contaminated Placeholder Art, Natyasangeet Expansion (*Sangeet Kanhopatra*, *Sangeet Devbabhali*), Quality-Aware Stream Deduplication, 100% Embedded Artwork, 0 Empty Folders, and $\ge 2$ Tracks Per Folder Architecture.

---

## 📊 Backlog Priority Matrix

| Priority | EPIC | Focus Area | Deliverable | Status |
|:---:|:---|:---|:---|:---:|
| **DONE** | **EPIC 22: Multi-Tier Authentic Artwork Resolution & Natyasangeet Expansion** | Authentic High-Res Art & Cultural Acquisition | Integrated Deezer 1000x1000 API in `ReliableMetadataClient`, enabled `overwrite_artwork` in `MasterOrganizer`, upgraded 1,443+ tracks across 70+ Bollywood soundtracks and artist discographies, purged cross-contamination in Pantera, Ringtones, Indian Rock, and Natyasangeet, acquired *Sangeet Kanhopatra* and *Sangeet Devbabhali* (320kbps MP3, 0 random chars), 5-loop verification 100% pass across 6,800 tracks | **DONE** |
| **DONE** | **EPIC 21: Acoustic Deduplication Engine & Forensic Artist/Noise Sanitization** | Acoustic Deduplication & Path Sanitization | Engineered `AcousticDeduplicationEngine` & enhanced `path_sanitizer.py`, resolved Golmaal/Choti Si Baat multi-copy overlap (*Aane Wala Pal*), resolved artist-named files, stripped rip noise tokens, upgraded Rahat Fateh Ali Khan *Zindagi Ye* to 232kbps master, purged empty directories, 100% 5-loop verification passing | **DONE** |
| **DONE** | **EPIC 20: Rare Marathi Natyasangeet Acquisition & Soundtrack Integration** | Rare Cultural Heritage & Forensics | Automated acquisition pipeline with yt-dlp & FFmpeg (320kbps MP3), expanded Natyasangeet catalog to 61 tracks across 10 canonical Sangeet Natak plays, solved Sachin Barad forensics (*Hum Aapke Hain Koun..!*), downloaded canonical master soundtrack, 0 empty folders, 5-loop verification 100% green | **DONE** |
| **DONE** | **EPIC 19: Artist-Centric Architecture & Category Reduction** | Pure Taxonomy & Artist Directories | Consolidated Hindi non-film into `Hindi\Artists` (44 artists), purged Albums and Ghazals, re-homed misplaced Bollywood tracks, extracted Marathi Natyasangeet artists to root, established `English\Singles`, 0 empty folders, 5-loop verification 100% green | **DONE** |
| **DONE** | **EPIC 18: Directory Streamlining & Synonym Consolidation** | Structural Hygiene & Part Disambiguation | Purged empty folders (0 left), consolidated Devotional & Bhajans, Rock & Pop, Hamrahi/Humrahi, Atif Aslam non-film, eliminated fake Love Story album, resolved all 13 cryptic part files with authentic tags, 5-loop verification 100% green | **DONE** |
| **DONE** | **EPIC 17: Precision Polishing & Marathi Linguistic Resolution** | Forensic Perfection & Typography | Re-homed 26 Lata Mangeshkar Marathi masterpieces to Marathi, stripped 17 soundtrack movie prefixes, solved Windows NTFS case-insensitive typography (161 files renamed, 152 tags updated), 34/34 passing tests | **DONE** |
| **DONE** | **EPIC 16: Multi-Source Reliable Metadata & 100% Embedded Artwork** | Online Discography & Universal Art | Built `ReliableMetadataClient` (iTunes + MusicBrainz WS API + SQLite cache), integrated into `MasterOrganizer`, 100% embedded artwork (6,801/6,801), 5-loop verification passing with 0 flaws, 30/30 unit tests | **DONE** |
| **DONE** | **EPIC 15: Acoustic Waveform Dedupe & Language Architecture** | Spectrum Matching & Pure Taxonomy | Raw PCM waveform hashing, 1,104 acoustic duplicates archived, 0 brackets, 0 Evergreen Classics, P.L. Deshpande in Marathi, The Doors merged, Hotel California deduplicated, 44 GB free space | **DONE** |
| **DONE** | **EPIC 14: Ground-Truth Pravachan & Katha Preservation** | Sequential Day/Session Structure | Preserved Ghaisasi Guruji (Day 01-05, Day 06-10, Artya), Kavishwar Maharaj, Shankar Abhyankar (Gita Adhyays 01-18), Aparna Abhyankar (Gita Pathan 01-18), 0 brackets, 100% dedicated collections | **DONE** |
| **DONE** | **EPIC 13: 4-Pass Taxonomy Refinement & Zero Brackets** | Granular Categorization | 100% elimination of Evergreen Classics (0 tracks), 0 brackets, 0 dirty symbols, 0 repeated prefixes | **DONE** |
| **DONE** | **EPIC 10: Deep Audio Inspection & Disambiguation** | Deep Metadata & Tagging | Multi-threaded per-file inspection, ID3v2.4/ASF embedded tag writing, stream hash dedupe | **DONE** |
| **DONE** | **EPIC 11: Sanskrit Sacred Audio Disambiguation** | Vedic Taxonomy | Separated Vedic Suktas, Stotras & Ashtakams, and Vedic Samhita; resolved Omkara & Nirvana | **DONE** |
| **DONE** | **EPIC 12: AirLLM Architecture & Fallbacks** | Intelligence Integration | AirLLM loader with CPU/CUDA detection and sub-millisecond linguistic classification | **DONE** |
| **DONE** | **EPIC 1: Multi-Drive Inventory & Tier-0 Dedupe** | Multi-Drive Discovery | 50,236 tracks cataloged across D, F, J; 36,363 duplicates mapped | **DONE** |
| **DONE** | **EPIC 2: High-Speed NVMe Staging & Rollback** | NVMe Staging | 5,535 clean tracks staged in 31s; rollback scripts generated | **DONE** |
| **DONE** | **EPIC 3: Master Organizer & Bollywood Consolidation** | Standalone CLI Engine | `python auralis.py organize-nvme` processed 6,116 tracks in 114s | **DONE** |
| **DONE** | **EPIC 4: Universal ID3v2.4 Tag Writer & Permissions** | Universal Metadata | 5,536 ID3v2.4 tags written, Windows NTFS ReadOnly attribute clearing | **DONE** |
| **DONE** | **EPIC 5: 5-Channel Parallel Engine & Uniform 2-Level Hierarchy** | Parallel Processing & Clean Architecture | 5-channel concurrent workers, in-process embedded intelligence (<50MB RAM), uniform 2-level directory structure | **DONE** |
| **DONE** | **EPIC 6: Quality-Aware Bitrate Dedupe & Artist Canonicalization** | Multi-Tier Deduplication | Keep 320kbps over 192kbps, collapse 1,111 duplicates, consolidate artists | **DONE** |
| **DONE** | **EPIC 7: Unified Autonomous Pipeline & AirLLM AutoModel** | End-to-End Autonomous Lifecycle | `python auralis.py auto-pipeline` ingests external chunk, scans, deduplicates, tags, and audits | **DONE** |
| **P0** | **EPIC 8: Cross-Drive Incremental Ingest (F: and J:)** | Cold Vault Continuous Ingest | Ingest remaining ~7,900 unique tracks from external HDDs (`F:\` and `J:\`) via `auto-pipeline` | **READY** |
| **P1** | **EPIC 9: Car USB Synchronization** | Output Delivery | Mirror clean organized library to `E:\BMW-Music` with 0 duplicate tracks | **QUEUED** |

---

## EPIC 22: Multi-Tier Authentic Artwork Resolution & Natyasangeet Expansion (COMPLETED)
- **[x] TASK:** feat-061-deezer-api-integration | **Spec:** Built `query_deezer` and `query_deezer_album` in `src/engine/reliable_metadata_client.py` fetching 1000x1000 master CD cover art. Added browser User-Agent headers to prevent CDN rate limits. | **LOC:** 80
- **[x] TASK:** feat-062-master-organizer-overwrite-artwork | **Spec:** Added `overwrite_artwork: bool = False` to `MasterOrganizer.write_id3_tags()` across MP3, WMA, and M4A tag handlers to replace generic placeholder frames. | **LOC:** 35
- **[x] TASK:** feat-063-bulk-artwork-upgrade-engine | **Spec:** Authored `scripts/upgrade_authentic_artwork.py` and `scripts/finalize_artwork_perfection.py` replacing placeholder and low-res covers for 1,443+ tracks across 70+ soundtracks, Pantera, Indian Rock, Ringtones, and Natyasangeet plays. | **LOC:** 240
- **[x] TASK:** feat-064-natyasangeet-expansion-kanhopatra-devbabhali | **Spec:** Acquired *Sangeet Kanhopatra* and *Sangeet Devbabhali* in pristine 320kbps MP3 fidelity with 1000x1000 front covers, pure `<Song Title>.mp3` filenames, and zero random characters. | **LOC:** 130
- **[x] TASK:** feat-065-verification-and-unit-tests | **Spec:** Expanded `tests/test_reliable_metadata_client.py` covering Deezer and iTunes album methods. Verified 37/37 passing unit tests, 0 flake8 errors, and 100% 5-loop physical verification. | **LOC:** 90

---

## EPIC 21: Acoustic Deduplication Engine & Forensic Artist/Noise Sanitization (COMPLETED)
- **[x] TASK:** feat-055-acoustic-deduplication-engine | **Spec:** Built `AcousticDeduplicationEngine` in `src/engine/embedded_intelligence.py` with phonetic title normalization, acoustic duplicate tolerance, and master track quality scoring. | **LOC:** 125
- **[x] TASK:** feat-056-path-sanitizer-artist-and-noise-stripping | **Spec:** Upgraded `strip_rip_noise_and_suffixes()` and `separate_artist_from_song_title()` in `src/engine/path_sanitizer.py` to strip rip tokens (`720p`, `11 S`, `sihag`, `downloadming`) and embedded artists. | **LOC:** 110
- **[x] TASK:** feat-057-golmaal-choti-si-baat-overlap-resolution | **Spec:** Transferred 256kbps master copies of *Aanewala Pal Jaane Waala Hai* and *Golmaal Hai* from *Choti Si Baat* to *Golmaal*, safely backed up 3 inferior/noisy duplicates, cleaned *Na Jaane Kyon*. | **LOC:** 85
- **[x] TASK:** feat-058-artist-named-files-and-rip-cleanup | **Spec:** Resolved tracks named after artists to true song titles, cleaned rip noise across Baadmaash Company, Dev D, Julie, Barfi, and Dard Bhare Songs. | **LOC:** 180
- **[x] TASK:** feat-059-5-loop-verification-and-zero-empty-sweep | **Spec:** Executed 5-loop physical verification across all 6,796 tracks (100% pass) and audited directory tree (0 empty folders, 0 single-file subfolders). | **LOC:** 50
- **[x] TASK:** feat-060-comprehensive-unit-tests | **Spec:** Authored `tests/test_acoustic_deduplication_and_noise_sanitizer.py` achieving 89% unit test coverage on path sanitization and 100% test pass rate. | **LOC:** 130
