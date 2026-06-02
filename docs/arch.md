# Auralis Plugin API Documentation

This document outlines the usage, minimum requirements, event hooking patterns, and provides examples for the `PluginInterface` to help developers write extensions for Auralis.

## Minimum Requirements

Every plugin in Auralis must inherit from `PluginInterface` (typically located in `src/plugins/plugin_interface.py`) and implement the following base properties and methods:

- `name`: A string property indicating the unique name of the plugin.
- `version`: A string property indicating the semantic version of the plugin (e.g., `1.0.0`).
- `init()`: The initialization method called by the `PluginLoader` when the plugin is activated.

## Event Hooking Patterns

Auralis uses a robust event hooking system allowing plugins to react to various lifecycle stages or data events. The primary hooks include:

- `on_scan_start(directory: str)`: Called before a directory scan begins.
- `on_track_played(track_id: str)`: Called when a track starts playing.
- `on_metadata_updated(track_id: str, new_metadata: dict)`: Called when track metadata is modified.

To hook into these events, simply define the methods in your plugin class. The internal Event Bus will dynamically register and trigger them.

## Hello World Example

Below is a minimal 'Hello World' plugin that demonstrates how to implement the `PluginInterface` and log an initialization message.

```python
from src.plugins.plugin_interface import PluginInterface
import logging

class HelloWorldPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "HelloWorld"

    @property
    def version(self) -> str:
        return "1.0.0"

    def init(self) -> None:
        logging.info("HelloWorld plugin has been initialized successfully!")
        print(f"[{self.name} v{self.version}] Loading complete.")

    def on_track_played(self, track_id: str) -> None:
        logging.info(f"HelloWorld plugin says: Now playing track {track_id}")
```
# AI Feasibility Report: Advanced Music Analysis with Hugging Face

This report analyzes the feasibility of integrating Hugging Face (HF) models into Auralis for advanced audio analysis, including Raga identification, Cover Song Identification (CSI), and detailed music tagging.

## Executive Summary

**Feasibility:** High for General Tagging; Moderate for Raga/Cover Identification.

Integrating Hugging Face `transformers` models is technically feasible and would significantly enhance Auralis's capabilities. However, it introduces substantial dependencies (`torch`, `transformers`) and resource requirements (memory/CPU).

## 1. General Music Tagging & Classification

**Goal:** Identify genre, mood, instruments, and other details.

**Recommended Model:** `m-a-p/MERT-v1-95M` or `laion/clap-htsat-unfused`

*   **MERT (Music Understanding):** A powerful model trained on large-scale music datasets. It can extract robust features for downstream tasks like genre classification, mood detection, and instrument identification.
*   **CLAP (Contrastive Language-Audio Pretraining):** Allows **Zero-Shot Classification**. You can provide a list of arbitrary text tags (e.g., "Happy Rock", "Sad Jazz", "Sitar Solo") and the model will predict the most likely match for the audio. This is extremely flexible.

**Implementation:**
-   Use `transformers.pipeline("audio-classification", model="m-a-p/MERT-v1-95M")` (if supported directly) or use the model to extract embeddings and classify with a lightweight head.
-   For CLAP: Pass audio + list of candidate tags -> Get probabilities.

## 2. Raga Identification (Indian Classical Music)

**Goal:** Identify the Raga of a song.

**Feasibility:**
-   **Direct Model:** There is currently no "plug-and-play" pre-trained Raga classifier on Hugging Face.
-   **Approach 1 (Zero-Shot):** Use **CLAP** (`laion/clap-htsat-unfused`). Provide raga names as text prompts (e.g., "Indian Classical Raga Bhairav", "Raga Yaman", "Raga Todi"). The model's training data likely includes some Indian Classical Music, so it may work for popular ragas.
-   **Approach 2 (Fine-Tuning):** Use **MERT** embeddings and train a small classifier (Random Forest or simple Neural Net) on the **CompMusic Carnatic/Hindustani dataset**. This requires a training pipeline but yields high accuracy (88-97% as per recent research).

**Recommendation:** Start with **CLAP Zero-Shot** as a proof-of-concept. If accuracy is low, proceed with fine-tuning MERT.

## 3. Cover Song Identification (CSI) & Original/Singer Verification

**Goal:** Determine if a song is an Original or a Cover.

**Challenges:**
-   "Original" is a semantic concept (who released it first?).
-   "Cover" implies same composition, different performance.

**Approaches:**
1.  **Audio Similarity (Embeddings):**
    -   Use **MERT** to generate an embedding vector for the track.
    -   Compare this vector against a known database of "Original" embeddings (if available).
    -   *Limitation:* Requires a reference database.
2.  **Singer Identification:**
    -   Use a **Speaker/Singer Identification** model (e.g., `speechbrain/spkrec-ecapa-voxceleb` or `microsoft/wavlm-base-plus-sv`).
    -   If metadata says "Artist: Queen", verify if the voice matches the known voice embedding of "Freddie Mercury".
    -   *Feasibility:* High complexity. Requires a database of artist voice signatures.
3.  **Live vs. Studio Classification:**
    -   Train a classifier (using MERT features) to distinguish "Studio Recording" vs "Live Performance" vs "Cover/Acoustic".

**Recommendation:**
-   Implement **Audio Similarity** checking using MERT embeddings. If you have the "Original" file (e.g., in your library), you can detect duplicates/covers by high semantic similarity but low acoustic fingerprint match (AcoustID would fail, MERT would succeed).

## Technical Architecture Proposal

### New Module: `src/services/ai_service.py`

```python
class AIService:
    def __init__(self):
        self.models = {}  # Lazy load models

    def load_model(self, model_name):
        # Load heavy transformers models only when needed
        pass

    def analyze_audio(self, file_path, tasks=["tagging", "raga"]):
        # Run specific analysis pipelines
        pass
```

### Dependencies
-   `torch` (PyTorch) - Heavy dependency (~700MB+).
-   `transformers` (Hugging Face) - Moderate.
-   `librosa` - Already used for DSP.
-   `numpy` - Already used.

### Performance Considerations
-   **Inference Speed:** Running these models on CPU is slower than standard DSP. Expect 1-5 seconds per song for analysis.
-   **Memory:** Models like MERT-95M take ~400MB RAM. CLAP takes similar. Total RAM usage may increase by ~1GB when active.
-   **Optional Feature:** This should be an *optional* plugin (e.g., `pip install auralis[ai]`) to avoid bloating the core application for users who don't need it.

## Next Steps for Prototype
1.  Create a script `prototypes/ai_demo.py`.
2.  Implement `analyze_raga_zero_shot(audio_path)` using CLAP.
3.  Implement `analyze_mood_genre(audio_path)` using MERT/CLAP.
4.  Test with sample audio.
