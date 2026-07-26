# Auralis Backlog (v2.1.1)

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

## 🐛 Identified Discrepancies (Hunters)
- **[BLOCKED]**: `src/modules/net/p2p_security.py` is missing implementation.
- **[DONE]**: `CloudSettingsWidget` is not integrated into `main_window.py`.
- **[DONE]**: `prune_play_history` is not scheduled in any lifecycle hook.
- **[x] TASK:** fix-001-bare-exceptions | **Loc:** Multiple | **Spec:** Resolve bare `except Exception:` blocks across codebase to satisfy flake8 and typing requirements | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 15

## 🕵️ Bug Hunter Tasks
- **[x] TASK:** hunt-001-scan-modules | **Loc:** TBD | **Spec:** Perform static analysis scan to identify unhandled exceptions and inject bug tasks | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 20

## 🗂️ Backlog Maintenance
- **[ ] AUDIT:** Pattern analysis across all neural modules.
- **[ ] VERIFY:** Integration testing for Edge-Cloud data handoff.
- **[ ] TASK:** maint-001-grooming | **Spec:** Review and categorize all new issues.

## 🚀 Feature End-to-End Implementations
> - **[BLOCKED] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [TODO] | **LOC Estimate:** 150

### Core Engine & Audio
> - **[x] TASK:** db-003-aggregator-seed | **Loc:** src/services/metadata/aggregators.py | **Spec:** Build batch seed logic for MusicBrainz/Spotify knowledge graph | **Deps:** src/services/metadata/service.py | **Hygiene:** [DONE] | **LOC Estimate:** 120

### Cloud & Synchronization
> - **[x] TASK:** api-002-jwt-auth | **Loc:** src/modules/api/main.py | **Spec:** Implement robust JWT validation and user session management | **Deps:** python-jose | **Hygiene:** [DONE] | **LOC Estimate:** 80
> - **[x] TASK:** api-003-rate-limiting | **Loc:** src/modules/api/main.py | **Spec:** Implement rate limiting for cloud endpoints | **Deps:** slowapi | **Hygiene:** [DONE] | **LOC Estimate:** 60

### Intelligence & AI
> - **[x] TASK:** neu-002-raga-clap-enhanced | **Loc:** src/services/ai/raga_classifier.py | **Spec:** Enhance CLAP zero-shot with specialized Indian Classical prompts | **Deps:** transformers | **Hygiene:** [DONE] | **LOC Estimate:** 90
> - **[x] TASK:** neu-004-specialized-instruments | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Train/Fine-tune models for Sitar, Sarod, and Tabla | **Deps:** torch | **Hygiene:** [DONE] | **LOC Estimate:** 150
> - **[x] TASK:** neu-005-drift-correction | **Loc:** src/utils/ai/drift_detector.py | **Spec:** Implement automated drift detection and model retraining trigger | **Deps:** numpy | **Hygiene:** [DONE] | **LOC Estimate:** 110

### Persistence & Metadata Schema
> - **[x] TASK:** data-001-schema-v2 | **Loc:** schema_expansion_v2.sql | **Spec:** Create schema for Gharanas, Instruments, and Vocalist signatures | **Deps:** sqlite3 | **Hygiene:** [DONE] | **LOC Estimate:** 60
> - **[x] TASK:** data-003-metadata-linkage | **Loc:** src/modules/neu/embedding_database.py | **Spec:** Link neural embeddings to the multi-modal knowledge graph | **Deps:** src/utils/db_utils.py | **Hygiene:** [DONE] | **LOC Estimate:** 110

### User Identity & Stats
> - **[x] TASK:** id-004-mfa-support | **Loc:** src/modules/id/auth.py | **Spec:** Support multi-factor authentication for user profiles | **Deps:** pyotp | **Hygiene:** [DONE] | **LOC Estimate:** 90

### System Maintenance
> - **[x] TASK:** sys-001-audit-pattern | **Loc:** docs/audit_report.md | **Spec:** Perform deep pattern analysis of neural drift and cache efficiency | **Deps:** None | **Hygiene:** [DONE] | **LOC Estimate:** 50
- **[x] CLEANUP:** Refactor `src/gui/pyqt/main_window.py` to reduce complexity.
