# Auralis Backlog (v9.0.0 - Acoustic Deduplication Engine, Forensic Artist/Noise Sanitization & Multi-Copy Resolution)

## 🎯 Current Sprint: Acoustic Deduplication Engine, Forensic Artist/Noise Sanitization & Zero-Defect Library
**North Star:** Deep Per-File Analysis, Acoustic Waveform & Phonetic Deduplication, Forensic Stripping of Artist Suffixes and Rip Junk from Filenames, Canonical Soundtrack Disambiguation (*Golmaal* & *Choti Si Baat*), Quality-Aware Stream Deduplication, 100% Embedded Artwork, 0 Empty Folders, and $\ge 2$ Tracks Per Folder Architecture.

---

## 📊 Backlog Priority Matrix

| Priority | EPIC | Focus Area | Deliverable | Status |
|:---:|:---|:---|:---|:---:|
| **DONE** | **EPIC 21: Acoustic Deduplication Engine & Forensic Artist/Noise Sanitization** | Acoustic Deduplication & Path Sanitization | Engineered `AcousticDeduplicationEngine` & enhanced `path_sanitizer.py`, resolved Golmaal/Choti Si Baat multi-copy overlap (*Aane Wala Pal*), resolved artist-named files (Celine Dion, Westlife, Smashing Pumpkins, Demonic Resurrection, Mohit Chauhan, KK, Shankar Mahadevan, Adnan Sami, Shreya Ghoshal), stripped rip noise tokens (720p, 11 S, sihag, badmaashcompany, devd, dbs), upgraded Rahat Fateh Ali Khan *Zindagi Ye* to 232kbps master, purged empty directories, 100% 5-loop verification passing across 6,796 tracks | **DONE** |
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

## EPIC 21: Acoustic Deduplication Engine & Forensic Artist/Noise Sanitization (COMPLETED)
- **[x] TASK:** feat-055-acoustic-deduplication-engine | **Spec:** Built `AcousticDeduplicationEngine` in `src/engine/embedded_intelligence.py` with phonetic title normalization, acoustic duplicate tolerance, and master track quality scoring. | **LOC:** 125
- **[x] TASK:** feat-056-path-sanitizer-artist-and-noise-stripping | **Spec:** Upgraded `strip_rip_noise_and_suffixes()` and `separate_artist_from_song_title()` in `src/engine/path_sanitizer.py` to strip rip tokens (`720p`, `11 S`, `sihag`, `downloadming`) and embedded artists. | **LOC:** 110
- **[x] TASK:** feat-057-golmaal-choti-si-baat-overlap-resolution | **Spec:** Transferred 256kbps master copies of *Aanewala Pal Jaane Waala Hai* and *Golmaal Hai* from *Choti Si Baat* to *Golmaal*, safely backed up 3 inferior/noisy duplicates, cleaned *Na Jaane Kyon*. | **LOC:** 85
- **[x] TASK:** feat-058-artist-named-files-and-rip-cleanup | **Spec:** Resolved tracks named after artists (Celine Dion, Westlife, Smashing Pumpkins, Demonic Resurrection, Mohit Chauhan, KK, Shankar Mahadevan, Adnan Sami, Shreya Ghoshal) to true song titles, cleaned rip noise across Baadmaash Company, Dev D, Julie, Barfi, and Dard Bhare Songs. | **LOC:** 180
- **[x] TASK:** feat-059-5-loop-verification-and-zero-empty-sweep | **Spec:** Executed 5-loop physical verification across all 6,796 tracks (100% pass) and audited directory tree (0 empty folders, 0 single-file subfolders). | **LOC:** 50
- **[x] TASK:** feat-060-comprehensive-unit-tests | **Spec:** Authored `tests/test_acoustic_deduplication_and_noise_sanitizer.py` achieving 89% unit test coverage on path sanitization and 100% test pass rate. | **LOC:** 130

---

## EPIC 20: Rare Marathi Natyasangeet Acquisition & Soundtrack Integration (COMPLETED)
- **[x] TASK:** feat-050-rare-natyasangeet-downloader | **Spec:** Developed `scripts/download_marathi_natyasangeet.py` and `scripts/download_targeted_natyasangeet.py` utilizing `yt-dlp` and `imageio_ffmpeg` with 320kbps MP3 extraction, cover art conversion, and ID3v2 tag embedding. | **LOC:** 345
- **[x] TASK:** feat-051-natyasangeet-play-restructuring | **Spec:** Reorganized all 18 loose root tracks into classic play collections (*Katyar Kaljat Ghusali*, *Sangeet Manapman*, *Sangeet Saubhadra*, *Sangeet Swayamvar*, *Sangeet Sanshaykallol*, *Sangeet Ekach Pyala*, *Sangeet Sharada*, *Sangeet Matsyagandha*, *Sangeet Shakuntal*, *Evergreen Natyageete*). Library now houses 61 tracks with $\ge 2$ tracks per folder. | **LOC:** 90
- **[x] TASK:** feat-052-sachin-barad-forensics-and-hahk-album | **Spec:** Forensically identified `PehlaPehlaPyarhain-SungbySachinBarad.mp3` as cover version of *Hum Aapke Hain Koun..!*, renamed to `Pehla Pehla Pyar - Cover.mp3`, downloaded canonical master soundtrack into `Hindi\Soundtracks\Hum Aapke Hain Koun`. | **LOC:** 180
- **[x] TASK:** feat-053-credit-pattern-sanitization | **Spec:** Normalized credit patterns (`Ft.`, `feat.`, `sungby`) and purged redundant lower-bitrate duplicates (`State of Shock`, `Tere Liye Unplugged`). | **LOC:** 65
- **[x] TASK:** feat-054-5-loop-verification-and-zero-empty-sweep | **Spec:** Re-ran 5-loop physical verification across all 6,810 tracks with 100.00% pass rate (0 errors, 0 empty folders, 0 single-file subfolders). | **LOC:** 40
