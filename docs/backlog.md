# Auralis Backlog

## 🎯 Current Sprint
**North Star:** Deep Per-File Analysis, Natyasangeet Cultural Heritage Cataloging, Canonical Soundtrack Disambiguation, Quality-Aware Stream Deduplication, 100% Embedded Artwork, 0 Empty Folders, and $\ge 2$ Tracks Per Folder Architecture.

---

## 📊 Backlog Priority Matrix

| Priority | EPIC | Focus Area | Deliverable | Status |
|:---:|:---|:---|:---|:---:|
| **P0** | **EPIC 8: Cross-Drive Incremental Ingest** | Cold Vault Continuous Ingest | Ingest remaining ~7,900 unique tracks from external HDDs via `auto-pipeline` | **READY** |
| **P1** | **EPIC 9: Car USB Synchronization** | Output Delivery | Mirror clean organized library to USB drive with 0 duplicate tracks | **QUEUED** |
| **P0** | **EPIC 21: Security & Dependency Hardening** | Application Security | Remove hardcoded secrets and document cross-repo dependencies | **READY** |

---

## EPIC 8: Cross-Drive Incremental Ingest
- **[ ] TASK:** feat-024-cross-drive-delta-ingest | **Spec:** Compare `master_cross_drive_catalog.db` against `D:\Songs\organized` to ingest remaining ~8,300 unique tracks from `F:\Music` and `J:\Music`. | **Deps:** master_organizer | **LOC Estimate:** 140
- **[ ] TASK:** feat-025-acoustid-chromaprint-fingerprint-validator | **Spec:** Spectrogram & Chromaprint audio fingerprinting verification on remaining generic tracks (`Track 1`). | **Deps:** pyacoustid | **LOC Estimate:** 95

---

## EPIC 9: Car USB Synchronization
- **[ ] TASK:** feat-026-car-usb-sync-mirror | **Spec:** High-speed incremental mirror sync from `D:\Songs\organized` to `E:\BMW-Music`. | **Deps:** feat-024 | **LOC Estimate:** 75

---

## EPIC 21: Security & Dependency Hardening
- **[ ] TASK:** sec-001-remove-hardcoded-api-key | **Spec:** Remove the default fallback `1vOwZtEn` for `ACOUSTID_API_KEY` in `src/utils/config.py`. Enforce strict env var requirement. | **Deps:** none | **LOC Estimate:** 20
- **[ ] TASK:** sec-002-remove-hardcoded-jwt-secret | **Spec:** Remove the default fallback `default-unsafe-secret-for-testing` for `AURALIS_JWT_SECRET` in `src/modules/api/main.py`. Enforce strict env var requirement. | **Deps:** none | **LOC Estimate:** 20
- **[ ] TASK:** doc-001-cross-repo-agent-reach | **Spec:** Document in `release-notes.md` that Auralis belongs to the Avinya Forge ecosystem and future API schema modifications must include cross-repo tasks for sister repositories (e.g., Aetheris, ghost-ops). | **Deps:** none | **LOC Estimate:** 15

---

## 🛑 Parked Items
- **[PARKED]** Libp2p P2P mesh network, LAN mDNS sync, 192kHz spatial audio inspector.
