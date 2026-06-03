# Auralis Vision: Hybrid Edge-Cloud Neural Network

## North Star
- **Hybrid Edge-Cloud Polyphonic Music Identification & Knowledge Graph.**
- The Autonomous, High-Fidelity Music Neural Network.
- Bridges the gap between local high-fidelity archives and the metadata-rich world of crowdsourced intelligence.

## Core Pillars
1.  **Audio Demixing (Zero-Overlap)**: Mandatory source separation (via Demucs or similar) prior to analysis. Solves the polyphonic overlap flaw by isolating instruments and vocals.
2.  **DSP + CV Hybrid (Harmonic Precision)**:
    - **Computer Vision (CV)**: Analyzes spectrograms for instrument/vocal classification.
    - **Digital Signal Processing (DSP)**: Uses Chroma features, BPM, and Key detection for structural analysis.
    - Result: Fixes harmonic distortion and improves identification accuracy.
3.  **Edge-Cloud Split (Power Efficiency)**:
    - **Edge (Local)**: Executes lightweight DSP, fingerprinting, and spectrogram generation.
    - **Cloud**: Offloads heavy neural classification and LLM orchestration.
    - Result: Prevents mobile battery drain and optimizes resource usage.
4.  **Crowdsource Database (Self-Evolving Knowledge)**:
    - Ingestion pipeline for user raw audio uploads and validation.
    - Gamified metadata tagging and verification.
    - Self-supervised learning (SSL) trained on unlabelled data to fix missing database coverage.
5.  **Dynamic Caches (Global/Local Sync)**:
    - Region or genre-specific "Music Packs" for offline metadata access.
    - Compressed metadata persistence for high-performance retrieval.

## Pipeline Laws (The "Iron Triangle")
- **Test Fortress:** All code (Core, GUI, CLI, Utils, API) must be covered by tests. Target coverage: 95%.
- **Lint Zero:** Strict `flake8` and `mypy` (disallow_untyped_defs = True) adherence.
- **Edge-First DSP:** All local processing must prioritize O(1) or O(n log n) efficiency.
- **Cloud-Second Neural:** Heavy models must be gated by the Meta-Agent Orchestrator.

## Definition of Done (DoD)
- [ ] **Tested:** Unit/Integration tests added covering demixing and hybrid paths.
- [ ] **Linted:** Passes all strict static analysis checks.
- [ ] **Optimized:** Verified performance budget for Edge execution.
- [ ] **Secured:** API endpoints authenticated and input sanitized.
- [ ] **Sync'd:** Knowledge Graph nodes updated and documentation reflects live state.

## Ideal State
- **Zero-Touch Organization**: Instant sorting via demixed-audio fingerprints.
- **Polyphonic Understanding**: Perfect identification of concurrent instruments.
- **Universal Knowledge**: A global, crowdsourced graph of Ragas, Gharanas, and Artists.
- **Fluid Ecosystem**: Seamless handoff between mobile Edge devices and Neural Cloud nodes.
