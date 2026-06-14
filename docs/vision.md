# Auralis Vision: Hybrid Edge-Cloud Neural Network

## North Star
- **Hybrid Edge-Cloud Polyphonic Music Identification & Knowledge Graph.**
- The Autonomous, High-Fidelity Music Neural Network.
- Bridges the gap between local high-fidelity archives and the metadata-rich world of crowdsourced intelligence.

## Core Pillars
1.  **Audio Demixing**: Force Source Separation (Demucs) before analysis. Fix polyphonic overlap by isolating instruments and vocals.
2.  **DSP + CV Hybrid**: Use Computer Vision (CV) on spectrograms for instrument/vocal classification. Use Digital Signal Processing (DSP) (Chroma features, BPM, Key) for chords/key structural analysis. Fixes harmonic distortion.
3.  **Edge-Cloud Split**: Execute lightweight DSP, fingerprinting, and spectrogram generation on device (Edge). Offload heavy neural classification and LLM orchestration to cloud. Prevents mobile battery drain and optimizes resource usage.
4.  **Crowdsource Database**: Build ingestion pipeline. Accept user raw audio uploads and validation. Gamify user metadata validation/tagging. AI trains on unlabelled data (self-supervised learning) to fix missing database coverage.
5.  **Dynamic Caches**: Implement region or genre-specific "Music Packs". Cache compressed metadata persistence locally for high-performance retrieval.

## Pipeline Laws (The "Iron Triangle")
- **Test Fortress:** All code (Core, GUI, CLI, Utils, API) must be covered by tests. Target coverage: 95%.
- **Lint Zero:** Strict `flake8` and `mypy` adherence.
- **Edge-First DSP:** All local processing must prioritize O(1) or O(n log n) efficiency.
- **Cloud-Second Neural:** Heavy models must be gated by the Meta-Agent Orchestrator.

## Definition of Done (DoD)
- [ ] **Tested:** Unit/Integration tests added covering demixing and hybrid paths.
- [ ] **Linted:** Passes all strict static analysis checks.
- [ ] **Optimized:** Verified performance budget for Edge execution.
- [ ] **Secured:** API endpoints authenticated and input sanitized.
- [ ] **Sync'd:** Knowledge Graph nodes updated and documentation reflects live state.

## Current Backlog Tasks Mapped
- db-001-1-upload-handler
- db-001-2-metadata-extractor
- db-001-verify-ingestion
- db-002-1-validation-view
- db-002-2-gamification-logic
- db-002-verify-validation
- db-003-1-musicbrainz-sync
- db-003-2-spotify-sync
- db-003-verify-aggregators
- db-004-1-ssl-preprocessing
- db-004-2-ssl-dataloader
- db-004-3-ssl-training-loop
- db-004-verify-ssl
- db-audit-ingestion
- db-cleanup-stage-1
- agent-001-1-router-logic
- agent-001-2-task-dispatcher
- agent-002-1-llm-client
- agent-002-2-prompt-factory
- api-001-1-fastapi-init
- api-001-2-endpoints-metadata
- api-001-3-endpoints-file-sync
- agent-analyze-latency
- agent-verify-gateway
- api-cleanup-routes
- plg-001-dep-resolver
- plg-002-sandbox
- neu-cleanup-models
- plg-verify-isolation
- resolve-003-skills-sync

## Ideal State
- **Zero-Touch Organization**: Instant sorting via demixed-audio fingerprints.
- **Polyphonic Understanding**: Perfect identification of concurrent instruments.
- **Universal Knowledge**: A global, crowdsourced graph of Ragas, Gharanas, and Artists.
- **Fluid Ecosystem**: Seamless handoff between mobile Edge devices and Neural Cloud nodes.

- Implemented data audit integrity, schema migration logic, and data cleanup orphans
