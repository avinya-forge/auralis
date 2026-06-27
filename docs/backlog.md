# Auralis Backlog (v2.1.0)

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence
**North Star:** The Autonomous, High-Fidelity Music Neural Network.

---

### Epic 1: Database Generation & Crowdsourcing
> - **[x] TASK:** db-001-ingestion-handler | **Loc:** src/modules/db/ingestion.py | **Spec:** Implement ChunkedUploadHandler and StagingMetadataExtractor | **Deps:** hashlib, os | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[ ] TASK:** db-002-validation-ui | **Loc:** src/gui/pyqt/tabs/validation_tab.py | **Spec:** Implement UI for crowdsourced metadata validation and gamification | **Deps:** PyQt6 | **Hygiene:** [TODO] | **LOC Estimate:** 150
> - **[ ] TASK:** db-003-aggregator-seed | **Loc:** src/services/metadata/aggregators.py | **Spec:** Build batch seed logic for MusicBrainz/Spotify knowledge graph | **Deps:** src/services/metadata/service.py | **Hygiene:** [TODO] | **LOC Estimate:** 120
> - **[x] TASK:** db-004-ssl-pipeline | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement SSL training loop and audio dataset stubs | **Deps:** torch | **Hygiene:** [DONE] | **LOC Estimate:** 130
> - **[ ] TASK:** db-005-ssl-refinement | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement actual contrastive loss and data augmentation logic | **Deps:** torch, numpy | **Hygiene:** [TODO] | **LOC Estimate:** 100

### Epic 2: Orchestration & Edge-Cloud Gateway
> - **[x] TASK:** agent-001-meta-router | **Loc:** src/modules/agent/orchestrator.py | **Spec:** Implement Meta-Agent Task Router with LLM fallback | **Deps:** src/services/ai/llm_orchestrator.py | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[x] TASK:** agent-002-llm-orchestrator | **Loc:** src/services/ai/llm_orchestrator.py | **Spec:** Implement LLMClient and PromptFactory for GPT-4/Claude | **Deps:** httpx, jinja2 | **Hygiene:** [DONE] | **LOC Estimate:** 120
> - **[x] TASK:** api-001-rest-gateway | **Loc:** src/modules/api/main.py | **Spec:** Implement FastAPI REST gateway for Edge-Cloud sync | **Deps:** fastapi | **Hygiene:** [DONE] | **LOC Estimate:** 150
> - **[ ] TASK:** api-002-jwt-auth | **Loc:** src/modules/api/main.py | **Spec:** Implement robust JWT validation and user session management | **Deps:** python-jose | **Hygiene:** [TODO] | **LOC Estimate:** 80
> - **[ ] TASK:** api-003-rate-limiting | **Loc:** src/modules/api/main.py | **Spec:** Implement rate limiting for cloud endpoints | **Deps:** slowapi | **Hygiene:** [TODO] | **LOC Estimate:** 60

### Epic 3: Audio Analysis Pipeline (Hybrid)
> - **[x] TASK:** audio-001-demucs-wrapper | **Loc:** src/services/audio/demixer.py | **Spec:** Implement Demucs source separation wrapper | **Deps:** demucs | **Hygiene:** [DONE] | **LOC Estimate:** 80
> - **[x] TASK:** audio-002-dsp-engine | **Loc:** src/services/audio/dsp_engine.py | **Spec:** Implement Chroma, BPM, and Key extraction logic | **Deps:** librosa | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[x] TASK:** audio-003-spec-gen | **Loc:** src/utils/audio/spectrogram.py | **Spec:** Implement normalized mel-spectrogram generator | **Deps:** torch, torchaudio | **Hygiene:** [DONE] | **LOC Estimate:** 70

### Epic 4: AI Neural Classifiers (Cloud Heavy)
> - **[x] TASK:** neu-001-instrument-resnet | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Implement ResNet for spectrogram-based instrument classification | **Deps:** torch | **Hygiene:** [DONE] | **LOC Estimate:** 140
> - **[ ] TASK:** neu-002-raga-clap-enhanced | **Loc:** src/services/ai/raga_classifier.py | **Spec:** Enhance CLAP zero-shot with specialized Indian Classical prompts | **Deps:** transformers | **Hygiene:** [TODO] | **LOC Estimate:** 90
> - **[x] TASK:** neu-003-vocalist-analyzer | **Loc:** src/services/ai/vocalist_analyzer.py | **Spec:** Implement SpeechBrain-based voice signature extraction | **Deps:** speechbrain | **Hygiene:** [DONE] | **LOC Estimate:** 130
> - **[ ] TASK:** neu-004-specialized-instruments | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Train/Fine-tune models for Sitar, Sarod, and Tabla | **Deps:** torch | **Hygiene:** [TODO] | **LOC Estimate:** 150
> - **[ ] TASK:** neu-005-drift-correction | **Loc:** src/utils/ai/drift_detector.py | **Spec:** Implement automated drift detection and model retraining trigger | **Deps:** numpy | **Hygiene:** [TODO] | **LOC Estimate:** 110

### Epic 5: Persistence & Metadata Schema
> - **[ ] TASK:** data-001-schema-v2 | **Loc:** schema_expansion_v2.sql | **Spec:** Create schema for Gharanas, Instruments, and Vocalist signatures | **Deps:** sqlite3 | **Hygiene:** [TODO] | **LOC Estimate:** 60
> - **[x] TASK:** data-002-pack-manager | **Loc:** src/services/cache/pack_manager.py | **Spec:** Implement "Music Pack" zlib compression and management | **Deps:** zlib | **Hygiene:** [DONE] | **LOC Estimate:** 90
> - **[ ] TASK:** data-003-metadata-linkage | **Loc:** src/modules/neu/embedding_database.py | **Spec:** Link neural embeddings to the multi-modal knowledge graph | **Deps:** src/utils/db_utils.py | **Hygiene:** [TODO] | **LOC Estimate:** 110

### Epic 6: Plugins & Security
> - **[ ] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [TODO] | **LOC Estimate:** 150
> - **[x] TASK:** plg-001-sandbox | **Loc:** src/modules/plg/plugin_sandbox.py | **Spec:** Implement secure execution environment for plugins | **Deps:** RestrictedPython | **Hygiene:** [DONE] | **LOC Estimate:** 120

### Epic 7: User Identity & Stats
> - **[x] TASK:** id-001-stats-aggregator | **Loc:** src/modules/id/stats.py | **Spec:** Implement personal listening stats aggregation | **Deps:** src/utils/db_utils.py | **Hygiene:** [DONE] | **LOC Estimate:** 60
> - **[x] TASK:** id-002-profile-sync | **Loc:** src/modules/id/sync.py | **Spec:** Implement profile export/import (json) | **Deps:** json | **Hygiene:** [DONE] | **LOC Estimate:** 80
> - **[x] TASK:** id-003-history-pruning | **Loc:** src/modules/id/cleanup.py | **Spec:** Implement retention-based play history pruning | **Deps:** src/utils/db_utils.py | **Hygiene:** [DONE] | **LOC Estimate:** 50
> - **[ ] TASK:** id-004-mfa-support | **Loc:** src/modules/id/auth.py | **Spec:** Support multi-factor authentication for user profiles | **Deps:** pyotp | **Hygiene:** [TODO] | **LOC Estimate:** 90

### Epic 8: Cloud Backing
> - **[x] TASK:** cld-001-provider-interface | **Loc:** src/services/cloud/provider_interface.py | **Spec:** Define abstract base class for cloud storage providers | **Deps:** abc | **Hygiene:** [DONE] | **LOC Estimate:** 40
> - **[x] TASK:** cld-002-aws-s3 | **Loc:** src/modules/cld/aws.py | **Spec:** Implement AWSProvider for S3 backing | **Deps:** boto3 | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[x] TASK:** cld-003-gdrive | **Loc:** src/modules/cld/gdrive.py | **Spec:** Implement GoogleDriveProvider for Drive backing | **Deps:** google-api-python-client | **Hygiene:** [DONE] | **LOC Estimate:** 120

### Epic 9: System Maintenance
> - **[ ] TASK:** sys-001-audit-pattern | **Loc:** docs/audit_report.md | **Spec:** Perform deep pattern analysis of neural drift and cache efficiency | **Deps:** None | **Hygiene:** [TODO] | **LOC Estimate:** 50
> - **[ ] TASK:** sys-002-cleanup-orphans | **Loc:** src/modules/db/cleanup.py | **Spec:** Implement database cleanup for orphaned metadata entries | **Deps:** src/utils/db_utils.py | **Hygiene:** [TODO] | **LOC Estimate:** 70
> - **[ ] TASK:** sys-003-automated-backups | **Loc:** src/modules/db/backup.py | **Spec:** Implement automated SQLite database backups to cloud | **Deps:** src/modules/cld/aws.py | **Hygiene:** [TODO] | **LOC Estimate:** 80

---

## 🛠️ Maintenance & Hygiene Tasks
- **[ ] AUDIT:** Pattern analysis across all neural modules.
- **[ ] VERIFY:** Integration testing for Edge-Cloud data handoff.
- **[ ] CLEANUP:** Refactor `src/gui/pyqt/main_window.py` to reduce complexity.

## 🐛 Identified Discrepancies (Hunters)
- **[BUG]**: `src/modules/net/p2p_security.py` is missing implementation.
- **[BUG]**: `CloudSettingsWidget` is not integrated into `main_window.py`.
- **[BUG]**: `prune_play_history` is not scheduled in any lifecycle hook.
