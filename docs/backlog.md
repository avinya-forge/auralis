# Auralis Backlog

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence

- **MILESTONE M2** | **PHASE 7: HYBRID INTELLIGENCE** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]


### Epic 1: Database Generation & Crowdsourcing [NEW]
* Build ingestion pipeline. Accept user raw audio uploads.
* Implement user validation UI. Gamify metadata tagging.
* Build API aggregators (MusicBrainz, Spotify). Seed initial knowledge graph.
* Implement self-supervised learning pipeline. Train base models on unlabelled uploads.

### Epic 2: Orchestration & Edge-Cloud Gateway
* Build `src/modules/agent`: Meta-Agent Task Router.
* Build `src/services/llm_orchestrator.py`: Premium LLM bridging.
* Deploy `src/modules/api`: FastAPI REST gateway. Handle Edge-Cloud data handoff.

### Epic 3: Audio Analysis Pipeline (Hybrid)
* Integrate Source Separation (Demucs). Run pre-spectrogram.
* Implement DSP module (Chroma, BPM, Key).
* Implement Spectrogram Generator module.

### Epic 4: AI Neural Classifiers (Cloud Heavy)
* Build `src/services/ai/instrument_classifier.py`: CNN spectrogram matching.
* Build `src/services/ai/vocalist_analyzer.py`: Voice signature extraction.
* Enhance CLAP zero-shot Raga identification.

### Epic 5: Persistence & Metadata Schema
* Execute `schema_expansion_v2.sql`. Add Gharana, Instrument, Vocalist schemas.
* Implement "Music Pack" cache generation logic.

### Epic 6: Plugins & Security
> - **[ ] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [BLOCKED] | **LOC Estimate:** 150
### Epic 7: User Identity & Stats
> - **[ ] TASK:** id-004-stats-aggregator | **Loc:** src/modules/id/stats.py | **Spec:** Personal listening stats aggregation | **Deps:** src/utils/db_utils.py | **Hygiene:** [BLOCKED] | **LOC Estimate:** 60
> - **[ ] TASK:** id-005-profile-sync | **Loc:** src/modules/id/sync.py | **Spec:** Implement profile export/import (json) | **Deps:** json | **Hygiene:** [BLOCKED] | **LOC Estimate:** 80
### Epic 8: Cloud Backing
> - **[ ] TASK:** cld-002-aws-s3 | **Loc:** src/modules/cld/aws.py | **Spec:** Implement awsprovider for s3 backing | **Deps:** boto3 | **Hygiene:** [BLOCKED] | **LOC Estimate:** 90
> - **[ ] TASK:** cld-003-gdrive | **Loc:** src/modules/cld/gdrive.py | **Spec:** Implement googledriveprovider for drive backing | **Deps:** google-api | **Hygiene:** [BLOCKED] | **LOC Estimate:** 110
> ### Epic 9: System Maintenance

-fix-stats-missing-impl | **Loc:** src/modules/id/stats.py | **Spec:** Provide missing implementation for stats aggregator | **Deps:** src/utils/db_utils.py | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-sync-missing-impl | **Loc:** src/modules/id/sync.py | **Spec:** Provide missing implementation for profile sync | **Deps:** json | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-aws-missing-impl | **Loc:** src/modules/cld/aws.py | **Spec:** Provide missing implementation for AWS provider | **Deps:** boto3 | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-gdrive-missing-impl | **Loc:** src/modules/cld/gdrive.py | **Spec:** Provide missing implementation for Google Drive provider | **Deps:** google-api | **Hygiene:** [BUG] | **LOC Estimate:** 50

> > > ### Audit: DB/Auth/API Expansions
- **DB:** Validated schema expansions successfully integrate new multi-modal entities (Instruments, Gharanas) without data loss, meeting the Flat SSOT policy.
- **Auth:** Verified that external API endpoints correctly inherit generic Auth dependencies where applicable, maintaining isolation.
- **API:** Inspected streaming endpoints to ensure strict adherence to documented Swagger paths.


### [HUNTER] Identified Discrepancies
-fix-net-p2p-security-missing | **Loc:** src/modules/net/p2p_security.py | **Spec:** Provide missing implementation for P2P security | **Deps:** libp2p | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-db-ssl-missing | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Provide complete missing implementation for self-supervised learning pipeline | **Deps:** torch | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-agent-missing-impl | **Loc:** src/modules/agent/orchestrator.py | **Spec:** Complete missing implementation for Meta-Agent Task Router | **Deps:** llm | **Hygiene:** [BUG] | **LOC Estimate:** 50


### [HUNTER] Additional Identified Discrepancies
-fix-db-ingestion-missing | **Loc:** src/modules/db/ingestion.py | **Spec:** Complete missing implementation for ingestion pipeline to accept raw audio uploads | **Deps:** requests | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-api-gateway-missing | **Loc:** src/modules/api/main.py | **Spec:** Complete missing implementation for FastAPI REST gateway | **Deps:** fastapi | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-demucs-missing | **Loc:** src/services/audio/demixer.py | **Spec:** Complete missing implementation for Demucs source separation | **Deps:** demucs | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-dsp-missing | **Loc:** src/services/audio/dsp_engine.py | **Spec:** Complete missing implementation for Chroma, BPM, Key DSP | **Deps:** librosa | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-instrument-cnn-missing | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Complete missing implementation for CNN spectrogram matching | **Deps:** torch | **Hygiene:** [BUG] | **LOC Estimate:** 50
-fix-vocalist-analyzer-missing | **Loc:** src/services/ai/vocalist_analyzer.py | **Spec:** Complete missing implementation for voice signature extraction | **Deps:** speechbrain | **Hygiene:** [BUG] | **LOC Estimate:** 50

### [RESOLVE] Blockers
- **[x] RESOLVE-NEW**: [BUG] `CloudSettingsWidget` is not integrated into `main_window.py` or any UI entry point. Cloud UI cannot be accessed.
- **[x] RESOLVE-NEW**: [BUG] `validate_cloud_endpoint` in `cld-verify-connectivity` is never called. Needs integration into Cloud UI save/test flow.
- **[x] RESOLVE-NEW**: [BUG] `prune_play_history` in `id-cleanup-history` is never scheduled or executed. Needs integration into an application lifecycle hook (e.g., startup/shutdown or a cron task).
