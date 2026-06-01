# Auralis Backlog

## 🎯 Current Sprint: Phase 7 Hybrid Intelligence

- **MILESTONE M2** | **PHASE 7: HYBRID INTELLIGENCE** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]

### Epic 1: Database Generation & Crowdsourcing
- **SPEC:** Build a self-evolving knowledge graph by ingesting user uploads and validating via gamified crowdsourcing.

> - **[ ] TASK:** db-001-1-upload-handler | **Loc:** src/modules/db/ingestion.py | **Spec:** Implement chunked file upload handler with hash validation | **Deps:** os, hashlib | **Hygiene:** 100% path coverage | **LOC Estimate:** 45
> - **[ ] TASK:** db-001-2-metadata-extractor | **Loc:** src/modules/db/ingestion.py | **Spec:** Extract raw metadata and store in temporary staging table | **Deps:** src/services/metadata_service.py | **Hygiene:** Exception logging | **LOC Estimate:** 40
> - **[ ] TASK:** db-001-verify-ingestion | **Loc:** tests/test_db_ingestion.py | **Spec:** Unit tests for upload handling and metadata extraction | **Deps:** pytest | **Hygiene:** Use temp directories | **LOC Estimate:** 45
> - **[ ] TASK:** db-002-1-validation-view | **Loc:** src/gui/pyqt/tabs/validation_tab.py | **Spec:** Implement base QWidget for validation interface | **Deps:** PyQt6 | **Hygiene:** Atomic UI components | **LOC Estimate:** 50
> - **[ ] TASK:** db-002-2-gamification-logic | **Loc:** src/services/gamification.py | **Spec:** Implement point calculation and achievement logic | **Deps:** src/utils/db_utils.py | **Hygiene:** O(1) score update | **LOC Estimate:** 45
> - **[ ] TASK:** db-002-verify-validation | **Loc:** tests/test_db_validation.py | **Spec:** Unit tests for gamification logic and UI state transitions | **Deps:** pytest-qt | **Hygiene:** Mock DB connection | **LOC Estimate:** 50
> - **[ ] TASK:** db-003-1-musicbrainz-sync | **Loc:** src/services/metadata/aggregators.py | **Spec:** Implement async MusicBrainz seed crawler | **Deps:** musicbrainzngs | **Hygiene:** Exponential backoff | **LOC Estimate:** 50
> - **[ ] TASK:** db-003-2-spotify-sync | **Loc:** src/services/metadata/aggregators.py | **Spec:** Implement async Spotify metadata fetcher | **Deps:** spotipy | **Hygiene:** Rate limit compliance | **LOC Estimate:** 45
> - **[ ] TASK:** db-003-verify-aggregators | **Loc:** tests/test_db_aggregators.py | **Spec:** Mock-based tests for external API sync logic | **Deps:** pytest, responses | **Hygiene:** Verify backoff triggers | **LOC Estimate:** 50
> - **[ ] TASK:** db-004-1-ssl-preprocessing | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement audio-to-tensor normalization for SSL | **Deps:** torch, numpy | **Hygiene:** O(n) streaming | **LOC Estimate:** 50
> - **[ ] TASK:** db-004-2-ssl-dataloader | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement custom PyTorch Dataset for audio tensors | **Deps:** torch | **Hygiene:** Efficient shuffling | **LOC Estimate:** 40
> - **[ ] TASK:** db-004-3-ssl-training-loop | **Loc:** src/modules/neu/training/ssl_pipeline.py | **Spec:** Implement base self-supervised training loop with checkpointing | **Deps:** torch | **Hygiene:** GPU memory management | **LOC Estimate:** 60
> - **[ ] TASK:** db-004-verify-ssl | **Loc:** tests/test_db_ssl.py | **Spec:** Unit tests for preprocessing and training loop state | **Deps:** pytest, torch | **Hygiene:** Mock GPU if missing | **LOC Estimate:** 50
> - **[ ] TASK:** db-audit-ingestion | **Loc:** scripts/audit_ingestion.py | **Spec:** Analyze ingestion success rates and data quality | **Deps:** src/utils/db_utils.py | **Hygiene:** Audit report output | **LOC Estimate:** 35
> - **[ ] TASK:** db-cleanup-stage-1 | **Loc:** scripts/cleanup.sh | **Spec:** Implement cron for orphaned staging record deletion | **Deps:** bash | **Hygiene:** Idempotent | **LOC Estimate:** 20

### Epic 2: Orchestration & Edge-Cloud Gateway
- **SPEC:** Implement the Meta-Agent orchestrator and REST gateway for seamless Edge-Cloud handoff.

> - **[ ] TASK:** agent-001-1-router-logic | **Loc:** src/modules/agent/orchestrator.py | **Spec:** Implement confidence threshold comparison logic | **Deps:** None | **Hygiene:** Atomic comparison | **LOC Estimate:** 35
> - **[ ] TASK:** agent-001-2-task-dispatcher | **Loc:** src/modules/agent/orchestrator.py | **Spec:** Build dispatcher for routing tasks to local vs cloud queues | **Deps:** multiprocessing | **Hygiene:** Thread safety | **LOC Estimate:** 50
> - **[ ] TASK:** agent-002-1-llm-client | **Loc:** src/services/ai/llm_orchestrator.py | **Spec:** Implement generic HTTP client for OpenAI/Anthropic | **Deps:** httpx | **Hygiene:** Error-resilient | **LOC Estimate:** 45
> - **[ ] TASK:** agent-002-2-prompt-factory | **Loc:** src/services/ai/llm_orchestrator.py | **Spec:** Implement dynamic template-based prompt generation | **Deps:** jinja2 | **Hygiene:** Input sanitization | **LOC Estimate:** 40
> - **[ ] TASK:** api-001-1-fastapi-init | **Loc:** src/modules/api/main.py | **Spec:** Bootstrap FastAPI app with middleware | **Deps:** fastapi | **Hygiene:** PEP8 compliant | **LOC Estimate:** 40
> - **[ ] TASK:** api-001-2-endpoints-metadata | **Loc:** src/modules/api/main.py | **Spec:** Implement GET/POST endpoints for metadata CRUD | **Deps:** fastapi | **Hygiene:** Schema validation | **LOC Estimate:** 45
> - **[ ] TASK:** api-001-3-endpoints-file-sync | **Loc:** src/modules/api/main.py | **Spec:** Implement streaming endpoints for audio file sync | **Deps:** fastapi | **Hygiene:** JWT authentication | **LOC Estimate:** 50
> - **[ ] TASK:** agent-analyze-latency | **Loc:** src/utils/perf/latency_logger.py | **Spec:** Implement middleware to track Edge-Cloud roundtrip latency | **Deps:** time | **Hygiene:** Minimal overhead | **LOC Estimate:** 30
> - **[ ] TASK:** agent-verify-gateway | **Loc:** tests/test_agent_gateway.py | **Spec:** Integration test for agent-router-gateway path | **Deps:** pytest | **Hygiene:** 95% coverage | **LOC Estimate:** 50

### Epic 3: Audio Analysis Pipeline (Hybrid)
- **SPEC:** Isolation and structural analysis via Source Separation and DSP modules.

> - **[ ] TASK:** audio-001-1-demucs-wrapper | **Loc:** src/services/audio/demixer.py | **Spec:** Implement process-isolated Demucs wrapper | **Deps:** subprocess | **Hygiene:** Handle OOM errors | **LOC Estimate:** 50
> - **[ ] TASK:** audio-002-1-chroma-features | **Loc:** src/services/audio/dsp_engine.py | **Spec:** Extract CQT-based chroma features | **Deps:** librosa | **Hygiene:** Numerical stability | **LOC Estimate:** 45
> - **[ ] TASK:** audio-002-2-rhythm-extraction | **Loc:** src/services/audio/dsp_engine.py | **Spec:** Implement BPM and onset strength detection | **Deps:** librosa | **Hygiene:** Precision verified | **LOC Estimate:** 40
> - **[ ] TASK:** audio-003-1-mel-spectrogram | **Loc:** src/utils/audio/spectrogram.py | **Spec:** Generate mel-spectrogram tensors from demixed stems | **Deps:** numpy, torchaudio | **Hygiene:** Normalized output | **LOC Estimate:** 50
> - **[ ] TASK:** audio-cleanup-cache | **Loc:** src/utils/audio/cache.py | **Spec:** Implement cache eviction for demixed audio chunks | **Deps:** os | **Hygiene:** LRU policy | **LOC Estimate:** 35
> - **[ ] TASK:** audio-verify-dsp | **Loc:** tests/test_audio_dsp.py | **Spec:** Unit tests for Chroma and Rhythm extraction accuracy | **Deps:** pytest, numpy | **Hygiene:** Use synthetic signals | **LOC Estimate:** 50

### Epic 4: AI Neural Classifiers (Cloud Heavy)
- **SPEC:** Deep classification of instruments, vocalists, and musical characteristics.

> - **[ ] TASK:** neu-001-1-instrument-resnet | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Define ResNet architecture for spectrogram classification | **Deps:** torch | **Hygiene:** Layer-wise typing | **LOC Estimate:** 50
> - **[ ] TASK:** neu-001-2-instrument-inference | **Loc:** src/services/ai/instrument_classifier.py | **Spec:** Implement inference wrapper and label mapping | **Deps:** src/services/ai/inference_engine.py | **Hygiene:** < 100ms inference | **LOC Estimate:** 45
> - **[ ] TASK:** neu-002-1-vocal-stem-interface | **Loc:** src/services/ai/vocalist_analyzer.py | **Spec:** Implement interface to extract vocal stems from demixer stems | **Deps:** numpy | **Hygiene:** Error handling | **LOC Estimate:** 40
> - **[ ] TASK:** neu-002-2-vocal-dvector | **Loc:** src/services/ai/vocalist_analyzer.py | **Spec:** Implement d-vector embedding generation via SpeechBrain | **Deps:** speechbrain | **Hygiene:** 100% privacy | **LOC Estimate:** 55
> - **[ ] TASK:** neu-003-1-clap-raga-prompts | **Loc:** src/services/ai/raga_classifier.py | **Spec:** Design and test 50+ Raga-specific zero-shot prompts | **Deps:** transformers | **Hygiene:** Deterministic | **LOC Estimate:** 40
> - **[ ] TASK:** neu-004-1-singer-id-link | **Loc:** src/modules/neu/singer_id.py | **Spec:** Link voice embeddings to vocalist metadata | **Deps:** src/utils/db_utils.py | **Hygiene:** [BLOCKED] | **LOC Estimate:** 45
> - **[ ] TASK:** neu-analyze-model-drift | **Loc:** src/utils/ai/drift_detector.py | **Spec:** Implement basic KL-divergence tracker for prediction distributions | **Deps:** numpy | **Hygiene:** Periodic trigger | **LOC Estimate:** 50
> - **[ ] TASK:** neu-verify-inference | **Loc:** tests/test_neu_inference.py | **Spec:** Performance benchmark for all neural classifiers | **Deps:** pytest-benchmark | **Hygiene:** Zero-debt audit | **LOC Estimate:** 50

### Epic 5: Persistence & Metadata Schema
- **SPEC:** Structured data persistence for advanced musicological data and offline access.

> - **[ ] TASK:** data-001-1-schema-migration | **Loc:** resources/db/schema_expansion_v2.sql | **Spec:** Implement idempotent SQL migration for v2 tables | **Deps:** src/utils/db_utils.py | **Hygiene:** Backup before run | **LOC Estimate:** 30
> - **[ ] TASK:** data-001-2-orm-update | **Loc:** src/models/music_graph.py | **Spec:** Update ORM/Logic to handle Gharana/Instrument relations | **Deps:** sqlalchemy | **Hygiene:** Typed models | **LOC Estimate:** 50
> - **[ ] TASK:** data-002-1-pack-generator | **Loc:** src/services/cache/pack_manager.py | **Spec:** Implement zlib compression for metadata music packs | **Deps:** zlib | **Hygiene:** High compression ratio | **LOC Estimate:** 45
> - **[ ] TASK:** data-audit-integrity | **Loc:** scripts/audit_db.py | **Spec:** Implement referential integrity check for the music graph | **Deps:** src/utils/db_utils.py | **Hygiene:** Read-only | **LOC Estimate:** 40
> - **[ ] TASK:** data-cleanup-orphans | **Loc:** src/services/cache/cleanup.py | **Spec:** Cleanup track metadata with missing local/cloud files | **Deps:** os | **Hygiene:** Atomic | **LOC Estimate:** 40

### Epic 6: Plugins & Security
> - **[x] TASK:** plg-001-dep-resolver | **Loc:** src/modules/plg/dependency_resolver.py | **Spec:** Implement DependencyResolver via Kahn's Algorithm | **Deps:** importlib | **Hygiene:** [DONE] | **LOC Estimate:** 135
> - **[x] TASK:** plg-002-sandbox | **Loc:** src/modules/plg/plugin_sandbox.py | **Spec:** Implement PluginSandbox using MetaPathFinder | **Deps:** importlib.abc | **Hygiene:** [DONE] | **LOC Estimate:** 100
> - **[ ] TASK:** net-001-p2p-security | **Loc:** src/modules/net/p2p_security.py | **Spec:** Implement P2PNetworkSecurity with libp2p and Noise | **Deps:** libp2p | **Hygiene:** [BLOCKED] | **LOC Estimate:** 150
> - **[ ] TASK:** plg-verify-isolation | **Loc:** tests/test_plg_isolation.py | **Spec:** Verify plugin sandbox prevents unauthorized OS access | **Deps:** pytest | **Hygiene:** Negative testing | **LOC Estimate:** 40

### Epic 7: User Identity & Stats
> - **[ ] TASK:** id-004-stats-aggregator | **Loc:** src/modules/id/stats.py | **Spec:** Personal listening stats aggregation | **Deps:** src/utils/db_utils.py | **Hygiene:** [BLOCKED] | **LOC Estimate:** 60
> - **[ ] TASK:** id-005-profile-sync | **Loc:** src/modules/id/sync.py | **Spec:** Implement profile export/import (json) | **Deps:** json | **Hygiene:** [BLOCKED] | **LOC Estimate:** 80
> - **[ ] TASK:** id-cleanup-history | **Loc:** src/modules/id/cleanup.py | **Spec:** Prune play history older than 1 year | **Deps:** src/utils/db_utils.py | **Hygiene:** Configurable limit | **LOC Estimate:** 30

### Epic 8: Cloud Backing
> - **[ ] TASK:** cld-002-aws-s3 | **Loc:** src/modules/cld/aws.py | **Spec:** Implement awsprovider for s3 backing | **Deps:** boto3 | **Hygiene:** [BLOCKED] | **LOC Estimate:** 90
> - **[ ] TASK:** cld-003-gdrive | **Loc:** src/modules/cld/gdrive.py | **Spec:** Implement googledriveprovider for drive backing | **Deps:** google-api | **Hygiene:** [BLOCKED] | **LOC Estimate:** 110
> - **[ ] TASK:** cld-004-cloud-ui | **Loc:** src/modules/cld/ui.py | **Spec:** Add cloud settings tab to configure provider | **Deps:** PyQt6 | **Hygiene:** [TODO] | **LOC Estimate:** 50
> - **[ ] TASK:** cld-verify-connectivity | **Loc:** src/modules/cld/test_connection.py | **Spec:** Implement ping/validation for cloud providers | **Deps:** requests | **Hygiene:** Secure | **LOC Estimate:** 40

### Epic 9: System Maintenance
> - **[ ] TASK:** resolve-003-skills-sync | **Loc:** scripts/run.sh | **Spec:** Implement integration hooks for run.sh skills | **Deps:** bash | **Hygiene:** Idempotent | **LOC Estimate:** 40
> - **[ ] TASK:** resolve-004-audit-expansions | **Loc:** docs/planning/backlog.md | **Spec:** Audit DB/Auth/API task expansions | **Deps:** None | **Hygiene:** IO_SSOT compliance | **LOC Estimate:** 20
> - **[ ] TASK:** resolve-005-dependency-audit | **Loc:** scripts/audit_deps.sh | **Spec:** Audit requirements.txt for pinned versions and vulnerabilities | **Deps:** safety | **Hygiene:** CI trigger | **LOC Estimate:** 30
> - **[ ] TASK:** resolve-006-complexity-refactor | **Loc:** scripts/check_complexity.sh | **Spec:** Audit src/ for Cyclomatic Complexity > 10 | **Deps:** radon | **Hygiene:** Prevent tech debt | **LOC Estimate:** 25
