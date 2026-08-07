# Auralis Backlog (v2.1.2)

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

## 🐛 Identified Discrepancies (Hunters)
- **[x] TASK:** fix-002-jose-deprecation | **Spec:** Fix python-jose datetime.datetime.utcnow() deprecation warning in API endpoints/tests. | **Deps:** None | **LOC Estimate:** 10
- **[BLOCKED]**: `src/modules/net/p2p_security.py` is missing implementation.
- **[DONE]**: `CloudSettingsWidget` is not integrated into `main_window.py`.
- **[DONE]**: `prune_play_history` is not scheduled in any lifecycle hook.
- **[x] TASK:** fix-001-bare-exceptions | [DEBT] | **Loc:** Multiple | **Spec:** Resolve bare `except Exception:` blocks across codebase to satisfy flake8 and typing requirements | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 15
- **[ ] TASK:** debt-001-docstrings | **Spec:** Add missing docstrings to 85 functions across the codebase. | **Deps:** None | **LOC Estimate:** 85
- **[x] TASK:** feat-001-coversong | **Spec:** Implement CoverSongDetector logic in src/cli/cli_main.py. | **Deps:** None | **LOC Estimate:** 40

## 🕵️ Bug Hunter Tasks
- **[x] TASK:** hunt-001-scan-modules | [DEBT] | **Loc:** TBD | **Spec:** Perform static analysis scan to identify unhandled exceptions and inject bug tasks | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 20

## 🗂️ Backlog Maintenance
- **[ ] TASK:** ui-002-ux-overhaul | **Spec:** Perform a comprehensive UI/UX overhaul to ensure a zero-glitch, user-friendly interface across all frameworks (PyQt/wxPython). | **Deps:** None | **LOC Estimate:** 300
- **[x] TASK:** ui-001-prune-history-duplicate | **Spec:** Remove duplicate prune_play_history calls in PyQt closeEvent
- **[x] TASK:** audio-006-audio-utils-coverage | **Spec:** Add comprehensive unit tests for src/utils/audio_utils.py to improve coverage | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 140
- **[x] TASK:** data-005-datetime-formatting | **Spec:** Fix Python datetime SQLite formatting to include seconds
- **[x] TASK:** audio-005-dsp-engine | **Spec:** Update DSPEngine.__init__ to mutually resolve sr and sample_rate
- **[x] TASK:** test-002-ai-batch-worker | **Spec:** Implement direct worker loop invocation test in tests/test_ai_batch_processor.py
- **[x] TASK:** test-003-coveragerc-omit | **Spec:** Update .coveragerc to exclude missing plugin test files
- **[x] TASK:** test-004-aggregators-coverage | **Spec:** Remove spotipy mock and write exception simulation tests for aggregators.py
- **[x] AUDIT:** Pattern analysis across all neural modules.
- **[x] VERIFY:** Integration testing for Edge-Cloud data handoff.
- **[x] TASK:** maint-001-grooming | **Spec:** Review and categorize all new issues.

## 🚀 Feature End-to-End Implementations
> - **[BLOCKED] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [TODO] | **LOC Estimate:** 150

### Core Engine & Audio
> - **[x] TASK:** db-003-aggregator-seed | **Loc:** src/services/metadata/aggregators.py | **Spec:** Build batch seed logic for MusicBrainz/Spotify knowledge graph | **Deps:** src/services/metadata/service.py | **Hygiene:** [DONE] | **LOC Estimate:** 120

### Cloud & Synchronization
> - **[x] TASK:** api-002-jwt-auth | **Loc:** src/modules/api/main.py | **Spec:** Implement robust JWT validation and user session management | **Deps:** python-jose | **Hygiene:** [DONE] | **LOC Estimate:** 80
> - **[x] TASK:** api-003-rate-limiting | **Loc:** src/modules/api/main.py | **Spec:** Implement rate limiting for cloud endpoints | **Deps:** slowapi | **Hygiene:** [DONE] | **LOC Estimate:** 60

### Intelligence & AI
- **[ ] TASK:** agent-003-headroom-skill | **Spec:** Add a "Headroom" skill to analyze and optimize existing codebase (reduce, reuse, optimize). | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** agent-004-task-observer | **Spec:** Add a "Task Observer" skill to monitor agent progress and maintain metrics for the project dashboard. | **Deps:** None | **LOC Estimate:** 90
- **[ ] TASK:** feat-002-spectrogram-detection | **Spec:** Implement real-time audio analysis and spectrogram generation for song detection similar to Merlin Bird ID. | **Deps:** librosa, torch | **LOC Estimate:** 150
- **[ ] TASK:** feat-003-batch-song-comparison | **Spec:** Implement efficient batch processing to compare multiple songs simultaneously based on spectrogram features. | **Deps:** feat-002 | **LOC Estimate:** 120
- **[ ] TASK:** feat-004-metadata-extraction | **Spec:** Enhance metadata extraction to gather all possible details and features from audio files, establishing a single source of truth. | **Deps:** None | **LOC Estimate:** 100
- **[ ] TASK:** doc-002-vision-statement | **Spec:** Document the streamlined vision and detailed step-by-step feature prioritization (Merlin app style) in architecture/vision docs. | **Deps:** None | **LOC Estimate:** 50
> - **[x] TASK:** neu-002-raga-clap-enhanced | **Loc:** src/services/ai/raga_classifier.py | **Spec:** Enhance CLAP zero-shot with specialized Indian Classical prompts | **Deps:** transformers | **Hygiene:** [DONE] | **LOC Estimate:** 90
> - **[x] TASK:** neu-004-specialized-instruments | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Train/Fine-tune models for Sitar, Sarod, and Tabla | **Deps:** torch | **Hygiene:** [DONE] | **LOC Estimate:** 150
> - **[x] TASK:** neu-005-drift-correction | **Loc:** src/utils/ai/drift_detector.py | **Spec:** Implement automated drift detection and model retraining trigger | **Deps:** numpy | **Hygiene:** [DONE] | **LOC Estimate:** 110

### Persistence & Metadata Schema
> - **[x] TASK:** data-001-schema-v2 | **Loc:** schema_expansion_v2.sql | **Spec:** Create schema for Gharanas, Instruments, and Vocalist signatures | **Deps:** sqlite3 | **Hygiene:** [DONE] | **LOC Estimate:** 60
> - **[x] TASK:** data-003-metadata-linkage | **Loc:** src/modules/neu/embedding_database.py | **Spec:** Link neural embeddings to the multi-modal knowledge graph | **Deps:** src/utils/db_utils.py | **Hygiene:** [DONE] | **LOC Estimate:** 110

### User Identity & Stats
> - **[x] TASK:** id-004-mfa-support | **Loc:** src/modules/id/auth.py | **Spec:** Support multi-factor authentication for user profiles | **Deps:** pyotp | **Hygiene:** [DONE] | **LOC Estimate:** 90

### System Maintenance
- **[ ] TASK:** sys-004-continuous-audit | **Spec:** Implement scheduled, automated code auditing to proactively find bugs and add them to the backlog. | **Deps:** None | **LOC Estimate:** 80
> - **[x] TASK:** sys-001-audit-pattern | **Loc:** docs/audit_report.md | **Spec:** Perform deep pattern analysis of neural drift and cache efficiency | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 50
- **[x] CLEANUP:** Refactor `src/gui/pyqt/main_window.py` to reduce complexity.
