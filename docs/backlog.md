# Auralis Backlog (v8.0.0 - Rare Marathi Natyasangeet, Soundtrack Integration & Forensics)

## 🎯 Current Sprint: Rare Marathi Natyasangeet, Canonical Soundtrack Albums & Library Perfection
**North Star:** Deep Per-File Analysis, Natyasangeet Cultural Heritage Cataloging, Canonical Soundtrack Disambiguation (*Hum Aapke Hain Koun..!*), Quality-Aware Stream Deduplication, 100% Embedded Artwork, 0 Empty Folders, and $\ge 2$ Tracks Per Folder Architecture.

---

## 📊 Backlog Priority Matrix

| Priority | EPIC | Focus Area | Deliverable | Status |
|:---:|:---|:---|:---|:---:|
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

## EPIC 20: Rare Marathi Natyasangeet Acquisition & Soundtrack Integration (COMPLETED)
- **[x] TASK:** feat-050-rare-natyasangeet-downloader | **Spec:** Developed `scripts/download_marathi_natyasangeet.py` and `scripts/download_targeted_natyasangeet.py` utilizing `yt-dlp` and `imageio_ffmpeg` with 320kbps MP3 extraction, cover art conversion, and ID3v2 tag embedding. | **LOC:** 345
- **[x] TASK:** feat-051-natyasangeet-play-restructuring | **Spec:** Reorganized all 18 loose root tracks into classic play collections (*Katyar Kaljat Ghusali*, *Sangeet Manapman*, *Sangeet Saubhadra*, *Sangeet Swayamvar*, *Sangeet Sanshaykallol*, *Sangeet Ekach Pyala*, *Sangeet Sharada*, *Sangeet Matsyagandha*, *Sangeet Shakuntal*, *Evergreen Natyageete*). Library now houses 61 tracks with $\ge 2$ tracks per folder. | **LOC:** 90
- **[x] TASK:** feat-052-sachin-barad-forensics-and-hahk-album | **Spec:** Forensically identified `PehlaPehlaPyarhain-SungbySachinBarad.mp3` as cover version of *Hum Aapke Hain Koun..!*, renamed to `Pehla Pehla Pyar - Cover.mp3`, downloaded canonical master soundtrack into `Hindi\Soundtracks\Hum Aapke Hain Koun`. | **LOC:** 180
- **[x] TASK:** feat-053-credit-pattern-sanitization | **Spec:** Normalized credit patterns (`Ft.`, `feat.`, `sungby`) and purged redundant lower-bitrate duplicates (`State of Shock`, `Tere Liye Unplugged`). | **LOC:** 65
- **[x] TASK:** feat-054-5-loop-verification-and-zero-empty-sweep | **Spec:** Re-ran 5-loop physical verification across all 6,810 tracks with 100.00% pass rate (0 errors, 0 empty folders, 0 single-file subfolders). | **LOC:** 40

---

## EPIC 19: Artist-Centric Architecture & Category Reduction (COMPLETED)
- **[x] TASK:** feat-045-hindi-artist-consolidation | **Spec:** Consolidated non-film artists from `Hindi\Albums`, `Hindi\Ghazals`, and `Devotional\Anup Jalota` into `Hindi\Artists` (44 artists). Purged empty Albums and Ghazals folders. | **LOC:** 120
- **[x] TASK:** feat-046-bollywood-track-rehoming | **Spec:** Re-homed misplaced Bollywood songs in English Trance and Assorted Pop & Rock to their authentic movie soundtracks in `Hindi\Soundtracks`. | **LOC:** 80
- **[x] TASK:** feat-047-marathi-artist-restructuring | **Spec:** Extracted Natyasangeet artists to `Marathi\<Artist>` and re-homed vocal masterworks to Pt. Bhimsen Joshi, Asha Bhosle, Suman Kalyanpur, and Pt. Vasantrao Deshpande. | **LOC:** 95
- **[x] TASK:** feat-048-english-artist-and-singles-architecture | **Spec:** Re-homed English tracks to canonical artists and established `English\Singles` for single-track releases, strictly enforcing $\ge 2$ tracks per folder. | **LOC:** 150
- **[x] TASK:** feat-049-5-loop-verification-and-zero-empty-sweep | **Spec:** Executed bottom-up directory sweep (71 empty folders purged, 0 left) and confirmed 100% pass across all 5 verification loops over 6,784 files. | **LOC:** 50

---

## EPIC 18: Directory Streamlining & Synonym Consolidation (COMPLETED)
- **[x] TASK:** feat-041-synonym-folder-consolidator | **Spec:** Built `scripts/consolidate_synonyms_and_parts.py` consolidating synonymous directories: `Hindi\Devotional` + `Devotional & Bhajans`, `English\Rock & Pop` + `Assorted Pop & Rock`, `Hamrahi` + `Humrahi` (192kbps upgrade), `Atif Aslam` non-film albums. | **LOC:** 215
- **[x] TASK:** feat-042-empty-dir-and-junk-sweeper | **Spec:** Built `scripts/audit_empty_and_synonym_folders.py` to recursively sweep and verify 0 empty directories, 0 junk files, and 0 single-file subfolders ($\ge 2$ tracks per folder). | **LOC:** 102
- **[x] TASK:** feat-043-part-tracks-forensic-resolution | **Spec:** Forensically matched all 13 cryptic part tracks against `auralis_inventory.db` ingest records and updated with authentic ID3 tags and canonical filenames. | **LOC:** 80
- **[x] TASK:** feat-044-multi-loop-verification-audit | **Spec:** Re-executed comprehensive 5-loop verification across all 6,786 physical files with 100.00% pass rate. | **LOC:** 40

---

## EPIC 17: Precision Polishing & Marathi Linguistic Resolution (COMPLETED)
- **[x] TASK:** feat-037-precision-polisher-engine | **Spec:** Built `src/engine/precision_polisher.py` executing 6-pass perfection pipeline across 6,794 files. | **LOC:** 440
- **[x] TASK:** feat-038-marathi-linguistic-rehoming | **Spec:** Re-homed 26 immortal Marathi Bhavgeet tracks from `Hindi\Artists\Lata Mangeshkar` to `Marathi\Lata Mangeshkar` with authentic tags. | **LOC:** 65
- **[x] TASK:** feat-039-soundtrack-prefix-liquidation | **Spec:** Eliminated 17 redundant movie title prefixes across Dum Maaro Dum, Ek Deewana Tha, Choti Si Baat, Jism 2, etc. | **LOC:** 55
- **[x] TASK:** feat-040-windows-ntfs-case-renamer | **Spec:** Engineered two-step temporary rename protocol (`__tmp_ren_`) to fix 161 English contraction and ordinal capitalizations on Windows NTFS. | **LOC:** 45

---

## EPIC 16: Multi-Source Reliable Metadata & 100% Embedded Artwork (COMPLETED)
- **[x] TASK:** feat-033-reliable-metadata-client | **Spec:** Built `src/engine/reliable_metadata_client.py` with iTunes Search API, MusicBrainz Web Service API, and SQLite local caching (`data/reliable_metadata_cache.db`). Integrated into `MasterOrganizer` in `src/engine/master_organizer.py`. | **LOC:** 220
- **[x] TASK:** feat-034-multi-pass-reiteration-pipeline | **Spec:** Implemented `scripts/reiterate_reliable_metadata_sync.py` executing multi-pass discography enrichment and artwork embedding across library tracks. | **LOC:** 140
- **[x] TASK:** feat-035-universal-embedded-artwork-coverage | **Spec:** Integrated Pillow 12.1.1 to achieve 100.0% embedded cover art coverage across all 6,801 audio tracks (ID3v2.4 `APIC`, MP4 `covr`, ASF `WM/Picture`). | **LOC:** 180
- **[x] TASK:** feat-036-comprehensive-5-loop-verifier | **Spec:** Built `scripts/verify_organized_files.py` auditing stream integrity, path sanitization, tag quality, categorical placement, and stream deduplication. All 5 loops pass with 0 flaws. | **LOC:** 362

---

## EPIC 10 & 11: Deep Audio Inspection & Vedic Sukta Disambiguation (COMPLETED)
- **[x] TASK:** feat-030-deep-audio-organizer-engine | **Spec:** Built `src/engine/deep_audio_organizer.py` with multi-threading, physical tag extraction, Windows path sanitization, audio stream hashing, and embedded tag writing (ID3v2.4/ASF). | **LOC:** 350
- **[x] TASK:** feat-031-sanskrit-sukta-stotra-disambiguation | **Spec:** Refactored `pattern_classifier.py` to prevent Omkara substring traps, cleanly disambiguate Purusha Suktam, Shree Suktam, Shri Rudram, and Nirvana Shatakam into separate Vedic Suktas vs Stotras & Ashtakams vs Vedic Samhita. | **LOC:** 120
- **[x] TASK:** feat-032-airllm-integration-and-hardware-audit | **Spec:** Audited environment (PyTorch 2.6.0 CPU, airllm 4.0.0), implemented `load_airllm_model` with CUDA/CPU handling and fallback in `embedded_intelligence.py`. | **LOC:** 45

---

## EPIC 6: Quality-Aware Bitrate Dedupe & Artist Canonicalization (COMPLETED)
- **[x] TASK:** feat-027-quality-bitrate-deduplication | **Spec:** Compare song titles within same artist/collection; keep highest bitrate (e.g. 320kbps), route lower bitrates to `_duplicates_backup`. | **LOC:** 65
- **[x] TASK:** feat-028-canonical-artist-alias-folding | **Spec:** Resolve aliases and inverted `Song - Artist` patterns into single canonical artist directories. | **LOC:** 90
- **[x] TASK:** feat-029-airllm-library-integration | **Spec:** Installed and verified `airllm` with PyTorch CPU runtime, Accelerate, and Transformers. | **LOC:** 35

---

## EPIC 5: Next Sprint Tasks (In Priority Order)
- **[ ] TASK:** feat-024-cross-drive-delta-ingest | **Spec:** Compare `master_cross_drive_catalog.db` against `D:\Songs\organized` to ingest remaining ~8,300 unique tracks from `F:\Music` and `J:\Music`. | **Deps:** master_organizer | **LOC Estimate:** 140
- **[ ] TASK:** feat-025-acoustid-chromaprint-fingerprint-validator | **Spec:** Spectrogram & Chromaprint audio fingerprinting verification on remaining generic tracks (`Track 1`). | **Deps:** pyacoustid | **LOC Estimate:** 95
- **[ ] TASK:** feat-026-car-usb-sync-mirror | **Spec:** High-speed incremental mirror sync from `D:\Songs\organized` to `E:\BMW-Music`. | **Deps:** feat-024 | **LOC Estimate:** 75

---

## 🛑 Parked Items
- **[PARKED]** Libp2p P2P mesh network, LAN mDNS sync, 192kHz spatial audio inspector.
