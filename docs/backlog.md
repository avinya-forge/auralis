# Auralis Backlog (v2.1.2)

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

## EPIC 1: Acoustic Deduplication & Song ID
- **[ ] TASK:** feat-002-spectrogram-detection-core | **Spec:** Implement real-time audio analysis using librosa to generate Mel-spectrograms. | **Deps:** librosa, torch | **LOC Estimate:** 80
- **[ ] TASK:** feat-002-spectrogram-detection-fingerprint | **Spec:** Generate unique Song ID based on distinct spectrogram features. | **Deps:** feat-002-spectrogram-detection-core | **LOC Estimate:** 70
- **[ ] TASK:** feat-003-batch-song-comparison-engine | **Spec:** Build concurrent batch processing engine for loading multiple audio files simultaneously. | **Deps:** feat-002-spectrogram-detection-fingerprint | **LOC Estimate:** 60
- **[ ] TASK:** feat-003-batch-song-comparison-logic | **Spec:** Implement deduplication logic by comparing spectrogram features across batched files. | **Deps:** feat-003-batch-song-comparison-engine | **LOC Estimate:** 60

## EPIC 2: Multi-source Metadata Aggregation
- **[ ] TASK:** auto-audit-2e44d0a7 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Refactor metadata_service.py to remove subprocess module and replace with secure API calls. | **Deps:** None | **LOC Estimate:** 20
- **[ ] TASK:** auto-audit-c89b1f63 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Update subprocess calls to use absolute paths to mitigate PATH-based execution attacks. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-4835d481 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Ensure shell=False is passed and sanitize inputs for subprocess calls to prevent shell injection. | **Deps:** None | **LOC Estimate:** 20
- **[ ] TASK:** auto-audit-d89bcfa9 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Remove hardcoded password 'ExampleDiscogsToken', move to environment variables. | **Deps:** None | **LOC Estimate:** 15
- **[ ] TASK:** feat-004-metadata-extraction-audio | **Spec:** Extract baseline metadata directly from audio file headers. | **Deps:** None | **LOC Estimate:** 50
- **[ ] TASK:** feat-004-metadata-extraction-enrich | **Spec:** Enrich extracted metadata by querying external APIs using the generated Song ID. | **Deps:** feat-004-metadata-extraction-audio | **LOC Estimate:** 50

## EPIC 4: Real-time Contextual Filtering & Detection
- **[BLOCKED] TASK:** net-001-p2p-security-core | **Spec:** Initialize libp2p node and generate ed25519 keypair for self-sovereign identity (blocked by missing src/modules/net/p2p_security.py). | **Deps:** None | **LOC Estimate:** 50

## System Maintenance & Tech Debt
- **[ ] TASK:** auto-audit-2f9bab7a | [DEBT] | **Loc:** src/services/playlist_service.py | **Spec:** Replace standard pseudo-random generators with secrets module for cryptographic safety. | **Deps:** None | **LOC Estimate:** 15
- **[ ] TASK:** auto-audit-875306fc | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Add timeouts to all requests module calls to prevent hanging connections. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-2dc3aa8d | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Replace assert statements with ValueError or proper exception handling. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-67a56f1d | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Remove hardcoded 'AmqQvwMQzTJHVhxHtTUVLHlyeKGcldYh', use secure env load. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-fb22eb48 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit B105 warning on Discogs request token URL. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-dcd89a61 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit B105 warning on Discogs access token URL. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-b85d40d9 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Refactor subprocess usage in dependency checker for security implications. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-d7dbe7b2 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Check untrusted inputs in subprocess call inside dependency checker. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-cf8c7ee4 | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Set usedforsecurity=False for MD5 hash in hashlib to suppress B324. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-c7051bfe | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Set usedforsecurity=False for SHA1 hash in hashlib to suppress B324. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-21f58679 | [DEBT] | **Loc:** src/utils/system_utils.py | **Spec:** Replace assert statements in system_utils.py for safe optimized bytecode. | **Deps:** None | **LOC Estimate:** 10
- **[PARKED] TASK:** debt-001-docstrings | **Spec:** Add missing docstrings to 85 functions across the codebase. | **Deps:** None | **LOC Estimate:** 85
- **[ ] TASK:** ui-002-1 | **Spec:** Migrate hardcoded QSS styles to centralized ThemeManager variables for maintainability. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-2 | **Spec:** Implement asynchronous loading indicators for all blocking I/O operations to improve UX flow. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-3 | **Spec:** Conduct cross-platform layout tests (Windows, Linux, macOS) to ensure consistent UI. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** sys-005-1 | **Spec:** Identify and safely remove deprecated modules and unused test scripts. | **Deps:** None | **LOC Estimate:** 60
- **[ ] TASK:** sys-005-2 | **Spec:** Consolidate redundant utility functions into unified modules. | **Deps:** sys-005-1 | **LOC Estimate:** 80
- **[ ] TASK:** sys-005-3 | **Spec:** Remove obsolete documentation and unneeded build artifacts. | **Deps:** None | **LOC Estimate:** 60
