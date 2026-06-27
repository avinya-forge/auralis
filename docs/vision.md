# Auralis Vision: Hybrid Edge-Cloud Neural Network

## North Star
**The Autonomous, High-Fidelity Music Neural Network.**
Bridges the gap between local high-fidelity archives and the metadata-rich world of crowdsourced intelligence using a hybrid Edge-Cloud architecture.

## Core Pillars
1.  **Audio Demixing (The Isotope Pillar):** Force Source Separation (Demucs) before analysis to fix polyphonic overlap by isolating instruments and vocals.
2.  **DSP + CV Hybrid (The Spectral Pillar):** Use Computer Vision (CV) on spectrograms for instrument/vocal classification and Digital Signal Processing (DSP) for structural analysis (Chroma, BPM, Key).
3.  **Edge-Cloud Split (The Efficiency Pillar):** Execute lightweight DSP and spectrogram generation on Edge (Device) while offloading heavy neural classification and LLM orchestration to Cloud.
4.  **Crowdsourced Knowledge (The Citizen Pillar):** Build a gamified ingestion pipeline to accept user recordings and validations, training self-supervised models on unlabelled data.
5.  **Dynamic Caches (The Offline Pillar):** Implement "Music Packs" (compressed metadata) to ensure high-performance retrieval and offline functionality.

## Alignment Map
- **Pillar 1** -> `src/services/audio/demixer.py`
- **Pillar 2** -> `src/services/audio/dsp_engine.py` & `src/utils/audio/spectrogram.py`
- **Pillar 3** -> `src/modules/api/` & `src/modules/agent/`
- **Pillar 4** -> `src/modules/db/ingestion.py` & `src/modules/neu/training/`
- **Pillar 5** -> `src/services/cache/pack_manager.py`

## Ideal State
- **Zero-Touch Organization:** Instant sorting via demixed-audio fingerprints.
- **Polyphonic Understanding:** Perfect identification of concurrent instruments.
- **Universal Knowledge:** A global, crowdsourced graph of Ragas, Gharanas, and Artists.
