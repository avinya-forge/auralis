# Auralis Backlog (v2.1.2)

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

## EPIC 1: Acoustic Deduplication & Song ID
- **[ ] TASK:** feat-002-spectrogram-detection | **Spec:** Implement real-time audio analysis and spectrogram generation for song detection similar to Merlin Bird ID. | **Deps:** librosa, torch | **LOC Estimate:** 150
- **[ ] TASK:** feat-003-batch-song-comparison | **Spec:** Implement efficient batch processing to compare multiple songs simultaneously based on spectrogram features. | **Deps:** feat-002 | **LOC Estimate:** 120

## EPIC 2: Multi-source Metadata Aggregation
- **[ ] TASK:** auto-audit-2e44d0a7 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Fix bandit error: [B404:blacklist] Consider possible security implications associated with the subprocess module. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-c89b1f63 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Fix bandit error: [B607:start_process_with_partial_path] Starting a process with a partial executable path | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-4835d481 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Fix bandit error: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-d89bcfa9 | [DEBT] | **Loc:** src/services/metadata_service.py | **Spec:** Fix bandit error: [B105:hardcoded_password_string] Possible hardcoded password: 'ExampleDiscogsToken' | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** feat-004-metadata-extraction | **Spec:** Enhance metadata extraction to gather all possible details and features from audio files, establishing a single source of truth. | **Deps:** None | **LOC Estimate:** 100

## EPIC 4: Real-time Contextual Filtering & Detection
- **[BLOCKED]**: `src/modules/net/p2p_security.py` is missing implementation.

## System Maintenance & Tech Debt
- **[ ] TASK:** auto-audit-2f9bab7a | [DEBT] | **Loc:** src/services/playlist_service.py | **Spec:** Fix bandit error: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-2f9bab7a | [DEBT] | **Loc:** src/services/playlist_service.py | **Spec:** Fix bandit error: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-875306fc | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Fix bandit error: [B113:request_without_timeout] Call to requests without timeout | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-2dc3aa8d | [DEBT] | **Loc:** src/utils/audio_utils.py | **Spec:** Fix bandit error: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-67a56f1d | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit error: [B105:hardcoded_password_string] Possible hardcoded password: 'AmqQvwMQzTJHVhxHtTUVLHlyeKGcldYh' | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-fb22eb48 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit error: [B105:hardcoded_password_string] Possible hardcoded password: 'https://api.discogs.com/oauth/request_token' | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-dcd89a61 | [DEBT] | **Loc:** src/utils/config.py | **Spec:** Fix bandit error: [B105:hardcoded_password_string] Possible hardcoded password: 'https://api.discogs.com/oauth/access_token' | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-b85d40d9 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Fix bandit error: [B404:blacklist] Consider possible security implications associated with the subprocess module. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-d7dbe7b2 | [DEBT] | **Loc:** src/utils/dependency_checker.py | **Spec:** Fix bandit error: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input. | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-cf8c7ee4 | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Fix bandit error: [B324:hashlib] Use of weak MD5 hash for security. Consider usedforsecurity=False | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-c7051bfe | [DEBT] | **Loc:** src/utils/file_utils.py | **Spec:** Fix bandit error: [B324:hashlib] Use of weak SHA1 hash for security. Consider usedforsecurity=False | **Deps:** None | **LOC Estimate:** 10
- **[ ] TASK:** auto-audit-21f58679 | [DEBT] | **Loc:** src/utils/system_utils.py | **Spec:** Fix bandit error: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code. | **Deps:** None | **LOC Estimate:** 10
- **[PARKED] TASK:** debt-001-docstrings | **Spec:** Add missing docstrings to 85 functions across the codebase. | **Deps:** None | **LOC Estimate:** 85
- **[ ] TASK:** ui-002-1 | **Spec:** Migrate hardcoded QSS styles to centralized ThemeManager variables. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-2 | **Spec:** Implement asynchronous loading indicators for all blocking I/O operations. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** ui-002-3 | **Spec:** Conduct cross-platform layout tests (Windows, Linux, macOS). | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** sys-005-1 | **Spec:** Identify and safely remove deprecated modules and unused test scripts. | **Deps:** sys-004 | **LOC Estimate:** 60
- **[ ] TASK:** sys-005-2 | **Spec:** Consolidate redundant utility functions into unified modules. | **Deps:** sys-004 | **LOC Estimate:** 80
- **[ ] TASK:** sys-005-3 | **Spec:** Remove obsolete documentation and unneeded build artifacts. | **Deps:** sys-004 | **LOC Estimate:** 60

