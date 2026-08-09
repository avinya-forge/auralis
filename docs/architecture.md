# Auralis Architecture



## Streamlined Vision: "Merlin for Music"
The core ideology is to draw inspiration from the Merlin Bird ID app, applying its advanced spectrogram-based identification to music libraries, while expanding upon our foundational mission. The ultimate goal is to enable limitless possibilities for musical analysis:

1. **Acoustic Identification & Deduplication**: Scan folders of music, generate a unique audio ID (Song ID) based on distinct acoustic factors (spectrogram features), and use these precise signatures to definitively compare and deduplicate files, ensuring every track is distinctly recognized.
2. **Comprehensive Metadata Aggregation**: Use the generated Song IDs to automatically query free, highly accurate online libraries (like MusicBrainz or acoustic fingerprint databases) to gather all relevant metadata and gracefully rename/organize files into a single source of truth.
3. **Deep Layered Analysis (The Merlin Inspiration)**: Capitalize on spectrogram technology to dissect the multiple layers of sound within a track. This includes identifying specific Indian Classical Ragas, detecting distinct patterns, and isolating individual instruments or vocalist signatures.
4. **Real-time Detection & Limitless Scaling**: Leverage these capabilities not just for static libraries, but eventually for real-time internal detection after playing a song, validating and utilizing these technologies in a focused, step-by-step manner.
5. **Intelligent Tracking & Contextual Filtering**: The application functions as an intelligent "brain" that structurally organizes physical libraries via AI. It requires 100% accurate metadata validation to power advanced UI-based filtering (e.g., dynamically filtering all "piano-based" songs, not just by text search, but by neural tagging).
6. **Sub-track Disambiguation**: The system must definitively understand *why* two seemingly identical songs differ (e.g., distinguishing between original, unplugged, live, or remastered versions) based on spectral differences and deeply embedded metadata tagging. We are essentially an advanced metadata processor powered by modern ML.


## Phase Roadmap

1. **Phase 1: Foundation (Acoustic Identification & Deduplication)**
   - Goal: Build the core spectrogram engine and implement song fingerprinting.
   - Key Features: Basic deduplication, accurate metadata matching.

2. **Phase 2: Data Aggregation (Comprehensive Metadata Aggregation)**
   - Goal: Connect to external metadata APIs and enrich the library data.
   - Key Features: Knowledge graph integration, lyric fetching, artist biographies.

3. **Phase 3: Advanced Intelligence (Deep Layered Analysis)**
   - Goal: Introduce sophisticated AI models for layered audio analysis.
   - Key Features: Raga detection, instrument classification, vocalist signature identification.

4. **Phase 4: Real-time & Scale (Real-time Detection)**
   - Goal: Enable streaming input analysis and optimize for large libraries.
   - Key Features: Microphone integration for instant identification, batch processing optimizations.


## User Journey / Flows

### Flow 1: Core Spectrogram Generation to UI Feedback
1. **User Action**: The user drags and drops a folder of unorganized music into the 'Scan' tab.
2. **Engine Processing**: The `Scanner` processes each file. The `DSPEngine` extracts audio frames.
3. **Neural Analysis**: The system computes a Mel-spectrogram for the audio. Neural classifiers identify distinct acoustic patterns (instruments, genre markers, vocalists).
4. **Fingerprinting**: A unique 'Song ID' is generated based on the spectrogram features.
5. **Metadata Matching**: The 'Song ID' is used to query external databases to verify/fetch accurate metadata.
6. **UI Feedback**: The 'Organize' tab updates in real-time, displaying the newly identified song with its correct title, artist, album art, and advanced neural tags (e.g., 'Piano', 'Acoustic', 'Live'). The user sees a visual representation of the audio's unique signature.


## Plugin API Documentation
Every plugin in Auralis must inherit from `PluginInterface` and implement `name`, `version`, and `init()`. Event hooking patterns include `on_scan_start`, `on_track_played`, and `on_metadata_updated`.
