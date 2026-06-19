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
> > > ### Audit: DB/Auth/API Expansions
- **DB:** Validated schema expansions successfully integrate new multi-modal entities (Instruments, Gharanas) without data loss, meeting the Flat SSOT policy.
- **Auth:** Verified that external API endpoints correctly inherit generic Auth dependencies where applicable, maintaining isolation.
- **API:** Inspected streaming endpoints to ensure strict adherence to documented Swagger paths.

### [RESOLVE] Blockers
- **RESOLVE-NEW**: [RESOLVED] `CloudSettingsWidget` integrated into `main_window.py`.
- **RESOLVE-NEW**: [RESOLVED] `validate_cloud_endpoint` integrated into Cloud UI test flow.
- **RESOLVE-NEW**: [RESOLVED] `prune_play_history` scheduled in `main_window.py` on closeEvent.
