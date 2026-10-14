# Auralis Backlog (v2.1.2)

## 🌌 6–8 Month Strategic Roadmap & Horizon Plan

| Horizon | Core Strategic Milestone | Lead Focus | Key Deliverables |
|:---:|:---|:---|:---|
| **Month 1–2** | **Acoustic Deduplication & Clean Architecture** | Audio Signal Processing | Spectrogram batch comparisons, Mel-scale feature extraction, Bandit/flake8 hardening |
| **Month 3–4** | **Multi-Source Metadata Aggregation & Neural Fingerprinting** | MusicBrainz & Discogs API | AcousticID extraction, Discogs enrichment, resilient rate-limited HTTP client |
| **Month 5–6** | **Spatial Audio Tagging & Smart Playlist Synthesis** | LLM Playlist Clustering | Local vector clustering for mood/tempo, lossless FLAC/ALAC bit-perfect validator |
| **Month 7–8** | **P2P Decentralized Audio Sync & Edge Streaming** | Libp2p & Local Mesh | P2P node initialization, ed25519 identity, LAN zero-config library syncing |

---

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

## EPIC 1: Acoustic Deduplication & Song ID
- **[x] TASK:** feat-002-spectrogram-detection-core | **Spec:** Implement real-time audio analysis using librosa to generate Mel-spectrograms. | **Deps:** librosa, torch | **LOC Estimate:** 80
- **[x] TASK:** feat-002-spectrogram-detection-fingerprint | **Spec:** Generate unique Song ID based on distinct spectrogram features. | **Deps:** feat-002-spectrogram-detection-core | **LOC Estimate:** 70
- **[x] TASK:** feat-003-batch-song-comparison-engine | **Spec:** Build concurrent batch processing engine for loading multiple audio files simultaneously. | **Deps:** feat-002-spectrogram-detection-fingerprint | **LOC Estimate:** 60
- **[x] TASK:** feat-003-batch-song-comparison-logic | **Spec:** Implement deduplication logic by comparing spectrogram features across batched files. | **Deps:** feat-003-batch-song-comparison-engine | **LOC Estimate:** 60
- **[x] TASK:** feat-003-fast-chroma-hash | **Spec:** Implement fast chromaprint hash comparison to bypass deep spectrogram compute for exact duplicates. | **Deps:** feat-003-batch-song-comparison-logic | **LOC Estimate:** 90

## EPIC 2: Multi-source Metadata Aggregation
- **[x] TASK:** auto-audit-2e44d0a7 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Refactor metadata_service.py to remove subprocess module and replace with secure API calls. | **Deps:** None | **LOC Estimate:** 20
- **[x] TASK:** auto-audit-c89b1f63 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Update subprocess calls to use absolute paths to mitigate PATH-based execution attacks. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-4835d481 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Ensure shell=False is passed and sanitize inputs for subprocess calls to prevent shell injection. | **Deps:** None | **LOC Estimate:** 20
- **[x] TASK:** auto-audit-d89bcfa9 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Remove hardcoded password 'ExampleDiscogsToken', move to environment variables. | **Deps:** None | **LOC Estimate:** 15
- **[ ] TASK:** feat-004-metadata-extraction-audio | **Spec:** Extract baseline metadata directly from audio file headers. | **Deps:** None | **LOC Estimate:** 50
- **[ ] TASK:** feat-004-metadata-extraction-enrich | **Spec:** Enrich extracted metadata by querying external APIs using the generated Song ID. | **Deps:** feat-004-metadata-extraction-audio | **LOC Estimate:** 50
- **[ ] TASK:** feat-005-spotify-metadata-resolver | **Spec:** Integrate Spotify web API client with OAuth2 token caching for rich album art and genre classification. | **Deps:** feat-004-metadata-extraction-enrich | **LOC Estimate:** 110

## EPIC 3: Spatial Audio & High-Resolution Tagging (Months 5–6)
- **[ ] TASK:** feat-006-flac-hi-res-inspector | **Spec:** Validate FLAC sample rate (96kHz/192kHz) and bit depth (24-bit/32-bit float) using mutagen. | **Deps:** None | **LOC Estimate:** 85
- **[ ] TASK:** feat-007-album-art-optimizer | **Spec:** Extract, sanitize, and embed maximum-resolution album covers into audio headers without quality degradation. | **Deps:** None | **LOC Estimate:** 75
- **[ ] TASK:** feat-008-semantic-mood-classifier | **Spec:** Classify audio tracks by valence and energy using lightweight local audio embedding model. | **Deps:** None | **LOC Estimate:** 120

## EPIC 4: Real-time Contextual Filtering & Detection
- **[ ] TASK:** net-001-p2p-security-core | **Spec:** Initialize libp2p node and generate ed25519 keypair for self-sovereign identity. | **Deps:** None | **LOC Estimate:** 50
- **[ ] TASK:** net-002-lan-discovery-mdns | **Spec:** Implement multicast DNS (mDNS) discovery for auto-detecting running Auralis nodes on local network. | **Deps:** net-001-p2p-security-core | **LOC Estimate:** 95
- **[ ] TASK:** net-003-p2p-differential-library-sync | **Spec:** Exchange cryptographic library manifests to synchronize tracks over encrypted stream. | **Deps:** net-002-lan-discovery-mdns | **LOC Estimate:** 140

## System Maintenance & Tech Debt
- **[x] TASK:** auto-audit-2f9bab7a | [DEBT] | **Loc:** src/services/playlist_service.py | **Spec:** Replace standard pseudo-random generators with secrets module for cryptographic safety. | **Deps:** None | **LOC Estimate:** 15
- **[x] TASK:** auto-audit-875306fc | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Add timeouts to all requests module calls to prevent hanging connections. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-2dc3aa8d | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Replace assert statements with ValueError or proper exception handling. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-67a56f1d | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Remove hardcoded 'AmqQvwMQzTJHVhxHtTUVLHlyeKGcldYh', use secure env load. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-fb22eb48 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit B105 warning on Discogs request token URL. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-dcd89a61 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit B105 warning on Discogs access token URL. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-b85d40d9 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Refactor subprocess usage in dependency checker for security implications. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-d7dbe7b2 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Check untrusted inputs in subprocess call inside dependency checker. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-cf8c7ee4 | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Set usedforsecurity=False for MD5 hash in hashlib to suppress B324. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-c7051bfe | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Set usedforsecurity=False for SHA1 hash in hashlib to suppress B324. | **Deps:** None | **LOC Estimate:** 10
- **[x] TASK:** auto-audit-21f58679 | [DEBT] | **Loc:** src/utils/system_utils.py | **Spec:** Replace assert statements in system_utils.py for safe optimized bytecode. | **Deps:** None | **LOC Estimate:** 10
- **[PARKED] TASK:** debt-001-docstrings | **Spec:** Add missing docstrings to 85 functions across the codebase. | **Deps:** None | **LOC Estimate:** 85
- **[ ] TASK:** ui-002-1 | **Spec:** Migrate hardcoded QSS styles to centralized ThemeManager variables for maintainability. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-2 | **Spec:** Implement asynchronous loading indicators for all blocking I/O operations to improve UX flow. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-3 | **Spec:** Conduct cross-platform layout tests (Windows, Linux, macOS) to ensure consistent UI. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** sys-005-1 | **Spec:** Identify and safely remove deprecated modules and unused test scripts. | **Deps:** None | **LOC Estimate:** 60
- **[ ] TASK:** sys-005-2 | **Spec:** Consolidate redundant utility functions into unified modules. | **Deps:** sys-005-1 | **LOC Estimate:** 80
- **[ ] TASK:** sys-005-3 | **Spec:** Remove obsolete documentation and unneeded build artifacts. | **Deps:** None | **LOC Estimate:** 60
