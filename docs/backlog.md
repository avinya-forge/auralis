# Auralis Backlog (v7.0.0 - Deep Audio Analysis, Sanskrit Sukta Disambiguation & AirLLM Engine)

## 🎯 Current Sprint: Deep Per-File Analysis, Vedic Sukta Disambiguation & Full Library Reorganization
**North Star:** Strict 1-File-At-A-Time Analysis Pipeline, Sanskrit Sukta & Stotra Disambiguation, Bollywood Disambiguation (e.g. Omkara), ID3v2.4 & ASF Deep Tagging, Quality-Aware Stream Hashing Deduplication, and AirLLM Architecture Support.

---

## 📊 Backlog Priority Matrix

| Priority | EPIC | Focus Area | Deliverable | Status |
|:---:|:---|:---|:---|:---:|
| **P0** | **EPIC 20: Security & Hardening** | Application Security | Fix hardcoded API password, audit and update weak cryptographic hashing (MD5/SHA1) | **READY** |
| **P0** | **EPIC 8: Cross-Drive Incremental Ingest (F: and J:)** | Cold Vault Continuous Ingest | Ingest remaining ~7,900 unique tracks from external HDDs (`F:\` and `J:\`) via `auto-pipeline` | **READY** |
| **P1** | **EPIC 9: Car USB Synchronization** | Output Delivery | Mirror clean organized library to `E:\BMW-Music` with 0 duplicate tracks | **QUEUED** |
| **P2** | **EPIC 21: Acoustic Deduplication & Song ID** | Phase 1 Foundation | Build the core spectrogram engine to generate unique audio IDs based on distinct acoustic factors for definitive deduplication and accurate metadata matching | **QUEUED** |
| **P2** | **EPIC 22: Multi-source Metadata Aggregation** | Phase 2 Data Aggregation | Integrate external APIs (MusicBrainz, Discogs, Spotify) to create a comprehensive multi-modal knowledge graph for tracks, enriching metadata, lyrics, and biographies | **QUEUED** |
| **P3** | **EPIC 23: Hugging Face Deep Audio Analysis** | Phase 3 Advanced Intelligence | Implement sophisticated AI models for layered audio analysis, including MERT tagging, CLAP zero-shot Raga detection, instrument classification, and Cover Song ID based on voice signatures | **QUEUED** |
| **P3** | **EPIC 24: Real-time Contextual Filtering & Detection** | Phase 4 Real-time & Scale | Enable dynamic filtering of libraries using neural tags and stream input analysis for instant identification using the microphone and batch processing optimizations | **QUEUED** |

---

## EPIC 20: Security & Hardening (NEW)
- **[ ] TASK:** sec-001-fix-hardcoded-api-password | **Spec:** Remove the hardcoded fallback password `admin_pass = os.getenv("AURALIS_ADMIN_PASS", "password")` in `src/modules/api/main.py`. Ensure secrets are not hardcoded. | **Deps:** None
- **[ ] TASK:** sec-002-audit-weak-hashing | **Spec:** Audit usage of `hashlib.md5` and `hashlib.sha1` in `src/modules/agent/headroom_skill.py`, `src/modules/agent/orchestrator.py`, `src/utils/file_utils.py`, `src/core/scanner.py`, and `src/engine/deep_audio_organizer.py`. Use `usedforsecurity=False` where appropriate, or replace with SHA256 where cryptographic security is needed. | **Deps:** None

---

## EPIC 8: Cross-Drive Incremental Ingest (F: and J:)
- **[ ] TASK:** feat-024-cross-drive-delta-ingest | **Spec:** Compare `master_cross_drive_catalog.db` against `D:\Songs\organized` to ingest remaining ~8,300 unique tracks from `F:\Music` and `J:\Music`. | **Deps:** master_organizer | **LOC Estimate:** 140

---

## EPIC 21: Acoustic Deduplication & Song ID (Phase 1)
- **[ ] TASK:** feat-025-acoustid-chromaprint-fingerprint-validator | **Spec:** Spectrogram & Chromaprint audio fingerprinting verification on remaining generic tracks (`Track 1`). Build core spectrogram engine. | **Deps:** pyacoustid | **LOC Estimate:** 95
- **[ ] TASK:** feat-050-unique-audio-id-generation | **Spec:** Generate unique audio IDs based on distinct acoustic factors for definitive deduplication. | **Deps:** feat-025

---

## EPIC 9: Car USB Synchronization
- **[ ] TASK:** feat-026-car-usb-sync-mirror | **Spec:** High-speed incremental mirror sync from `D:\Songs\organized` to `E:\BMW-Music`. | **Deps:** feat-024 | **LOC Estimate:** 75

---

## 🛑 Parked Items
- **[PARKED]** Libp2p P2P mesh network, LAN mDNS sync, 192kHz spatial audio inspector.
