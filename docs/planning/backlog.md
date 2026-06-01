# Auralis Backlog

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence

- **MILESTONE M2** | **PHASE 7: HYBRID INTELLIGENCE** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]

### Epic 1: Database Generation & Crowdsourcing [NEW]
- **SPEC:** Build a self-evolving knowledge graph by ingesting user uploads and validating via gamified crowdsourcing.

> - **[ ] TASK:** db-001-ingestion-pipeline | **Loc:** src/modules/db/ingestion.py | **Spec:** Build pipeline to accept and process user raw audio uploads | **Deps:** os, storage | **Hygiene:** Atomic writes | **LOC Estimate:** 80
> - **[ ] TASK:** db-002-validation-ui | **Loc:** src/gui/pyqt/tabs/validation_tab.py | **Spec:** Implement gamified UI for user metadata validation and tagging | **Deps:** PyQt6 | **Hygiene:** Responsive UI | **LOC Estimate:** 120
> - **[ ] TASK:** db-003-api-aggregators | **Loc:** src/services/metadata/aggregators.py | **Spec:** Integrate MusicBrainz/Spotify APIs to seed the initial knowledge graph | **Deps:** musicbrainzngs, spotipy | **Hygiene:** Rate limiting | **LOC Estimate:** 60
> - **[ ] TASK:** db-004-ssl-pipeline | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement self-supervised learning (SSL) pipeline for unlabelled uploads | **Deps:** torch, transformers | **Hygiene:** GPU optimization | **LOC Estimate:** 150

### Epic 2: Orchestration & Edge-Cloud Gateway
- **SPEC:** Implement the Meta-Agent orchestrator and REST gateway for seamless Edge-Cloud handoff.

> - **[ ] TASK:** agent-001-task-router | **Loc:** src/modules/agent/orchestrator.py | **Spec:** Build Meta-Agent Task Router for confidence-based model selection | **Deps:** src/services/ai_service.py | **Hygiene:** < 50ms latency | **LOC Estimate:** 100
> - **[ ] TASK:** agent-002-llm-bridge | **Loc:** src/services/ai/llm_orchestrator.py | **Spec:** Implement premium LLM bridging (OpenAI/Anthropic) for deep analysis | **Deps:** httpx | **Hygiene:** Token budget management | **LOC Estimate:** 80
> - **[ ] TASK:** api-001-fastapi-gateway | **Loc:** src/modules/api/main.py | **Spec:** Deploy FastAPI REST gateway for mobile/edge client sync | **Deps:** fastapi, uvicorn | **Hygiene:** JWT Auth | **LOC Estimate:** 120

### Epic 3: Audio Analysis Pipeline (Hybrid)
- **SPEC:** Isolation and structural analysis via Source Separation and DSP modules.

> - **[ ] TASK:** audio-001-demixing | **Loc:** src/services/audio/demixer.py | **Spec:** Integrate Demucs for mandatory source separation pre-analysis | **Deps:** demucs | **Hygiene:** [HIGH-RISK] Memory heavy | **LOC Estimate:** 90
> - **[ ] TASK:** audio-002-dsp-structural | **Loc:** src/services/audio/dsp_engine.py | **Spec:** Implement DSP module for Chroma, BPM, and Key detection | **Deps:** librosa | **Hygiene:** O(n) complexity | **LOC Estimate:** 70
> - **[ ] TASK:** audio-003-spectrogram-gen | **Loc:** src/utils/audio/spectrogram.py | **Spec:** Implement Spectrogram Generator for CV-based classification | **Deps:** matplotlib, numpy | **Hygiene:** Cache results | **LOC Estimate:** 40

### Epic 4: AI Neural Classifiers (Cloud Heavy)
- **SPEC:** Deep classification of instruments, vocalists, and musical characteristics.

> - **[ ] TASK:** neu-001-instrument-cnn | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Build CNN for spectrogram matching (Sitar, Sarod, etc.) | **Deps:** torch, torchvision | **Hygiene:** 95% accuracy target | **LOC Estimate:** 150
> - **[ ] TASK:** neu-002-vocal-signature | **Loc:** src/services/ai/vocalist_analyzer.py | **Spec:** Implement voice signature extraction and matching | **Deps:** speechbrain | **Hygiene:** Privacy-preserving embeddings | **LOC Estimate:** 120
> - **[ ] TASK:** neu-003-clap-raga-enhance | **Loc:** src/services/ai/raga_classifier.py | **Spec:** Enhance CLAP zero-shot Raga identification with custom prompts | **Deps:** transformers | **Hygiene:** Support 50+ Ragas | **LOC Estimate:** 60
> - **[ ] TASK:** neu-004-singer-id | **Loc:** src/modules/neu/singer_id.py | **Spec:** Singer identification using wavlm-base-plus-sv | **Deps:** microsoft/wavlm | **Hygiene:** [BLOCKED] | **LOC Estimate:** 50
> - **[ ] TASK:** neu-005-live-vs-studio | **Loc:** src/modules/neu/live_classifier.py | **Spec:** Classify Live vs Studio vs Cover via MERT features | **Deps:** m-a-p/MERT | **Hygiene:** [BLOCKED] | **LOC Estimate:** 50

### Epic 5: Persistence & Metadata Schema
- **SPEC:** Structured data persistence for advanced musicological data and offline access.

> - **[ ] TASK:** data-001-schema-v2 | **Loc:** resources/db/schema_expansion_v2.sql | **Spec:** Execute schema expansion for Gharana, Instrument, and Vocalist tables | **Deps:** sqlite3 | **Hygiene:** Zero-loss migration | **LOC Estimate:** 30
> - **[ ] TASK:** data-002-music-packs | **Loc:** src/services/cache/pack_manager.py | **Spec:** Implement "Music Pack" compressed cache generation logic | **Deps:** zipfile, sqlite3 | **Hygiene:** Delta updates | **LOC Estimate:** 80
> - **[x] TASK:** cld-005-sync-tracker | **Loc:** src/modules/cld/sync_state_tracker.py | **Spec:** Create sqlite-based syncstatetracker | **Deps:** sqlite3 | **Hygiene:** [DONE] | **LOC Estimate:** 140
> - **[x] TASK:** mob-001-offline-cache | **Loc:** src/modules/mob/offline_cache.py | **Spec:** Implement OfflineCache SQLite Strategy | **Deps:** sqlite3 | **Hygiene:** [DONE] | **LOC Estimate:** 130

### Epic 6: Plugins & Security
- **SPEC:** Modular extension system and secure network communication.

> - **[x] TASK:** plg-001-dep-resolver | **Loc:** src/modules/plg/dependency_resolver.py | **Spec:** Implement DependencyResolver via Kahn's Algorithm | **Deps:** importlib | **Hygiene:** [DONE] | **LOC Estimate:** 135
> - **[x] TASK:** plg-002-sandbox | **Loc:** src/modules/plg/plugin_sandbox.py | **Spec:** Implement PluginSandbox using MetaPathFinder | **Deps:** importlib.abc | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[ ] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [BLOCKED] | **LOC Estimate:** 150

### Epic 7: User Identity & Stats
- **SPEC:** User profile management and analytics.

> - **[ ] TASK:** id-004-stats-aggregator | **Loc:** src/modules/id/stats.py | **Spec:** Personal listening stats aggregation | **Deps:** sqlite3 | **Hygiene:** [BLOCKED] | **LOC Estimate:** 60
> - **[ ] TASK:** id-005-profile-sync | **Loc:** src/modules/id/sync.py | **Spec:** Implement profile export/import (json) | **Deps:** json | **Hygiene:** [BLOCKED] | **LOC Estimate:** 80

### Epic 8: Cloud Backing
- **SPEC:** Integration with external cloud storage providers.

> - **[ ] TASK:** cld-002-aws-s3 | **Loc:** src/modules/cld/aws.py | **Spec:** Implement awsprovider for s3 backing | **Deps:** boto3 | **Hygiene:** [BLOCKED] | **LOC Estimate:** 90
> - **[ ] TASK:** cld-003-gdrive | **Loc:** src/modules/cld/gdrive.py | **Spec:** Implement googledriveprovider for drive backing | **Deps:** google-api | **Hygiene:** [BLOCKED] | **LOC Estimate:** 110
> - **[ ] TASK:** cld-004-cloud-ui | **Loc:** src/modules/cld/ui.py | **Spec:** Add cloud settings tab to configure provider | **Deps:** PyQt6 | **Hygiene:** [TODO] | **LOC Estimate:** 50

### Epic 9: System Maintenance
> - **[ ] TASK:** resolve-003-skills-sync | **Loc:** scripts/run.sh | **Spec:** Implement integration hooks for run.sh skills | **Deps:** bash | **Hygiene:** Idempotent | **LOC Estimate:** 40
> - **[ ] TASK:** resolve-004-audit-expansions | **Loc:** docs/planning/backlog.md | **Spec:** Audit DB/Auth/API task expansions | **Deps:** None | **Hygiene:** IO_SSOT compliance | **LOC Estimate:** 20
