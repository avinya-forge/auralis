# Auralis Architecture



## Streamlined Vision: "Merlin for Music"
The core ideology is to draw inspiration from the Merlin Bird ID app, applying its advanced spectrogram-based identification to music libraries, while expanding upon our foundational mission. The ultimate goal is to enable limitless possibilities for musical analysis:

1. **Acoustic Identification & Deduplication**: Scan folders of music, generate a unique audio ID (Song ID) based on distinct acoustic factors (spectrogram features), and use these precise signatures to definitively compare and deduplicate files, ensuring every track is distinctly recognized.
2. **Comprehensive Metadata Aggregation**: Use the generated Song IDs to automatically query free, highly accurate online libraries (like MusicBrainz or acoustic fingerprint databases) to gather all relevant metadata and gracefully rename/organize files into a single source of truth.
3. **Deep Layered Analysis (The Merlin Inspiration)**: Capitalize on spectrogram technology to dissect the multiple layers of sound within a track. This includes identifying specific Indian Classical Ragas, detecting distinct patterns, and isolating individual instruments or vocalist signatures.
4. **Real-time Detection & Limitless Scaling**: Leverage these capabilities not just for static libraries, but eventually for real-time internal detection after playing a song, validating and utilizing these technologies in a focused, step-by-step manner.
5. **Intelligent Tracking & Contextual Filtering**: The application functions as an intelligent "brain" that structurally organizes physical libraries via AI. It requires 100% accurate metadata validation to power advanced UI-based filtering (e.g., dynamically filtering all "piano-based" songs, not just by text search, but by neural tagging).
6. **Sub-track Disambiguation**: The system must definitively understand *why* two seemingly identical songs differ (e.g., distinguishing between original, unplugged, live, or remastered versions) based on spectral differences and deeply embedded metadata tagging. We are essentially an advanced metadata processor powered by modern ML.

## Phase Roadmap ("Merlin for Music")
- **Phase 1 (Foundation):** Core library scanning, initial ID3 tag extraction, and SQLite persistence.
- **Phase 2 (Acoustic Fingerprinting):** Generate Song IDs from basic acoustic features to start local file deduplication.
- **Phase 3 (Knowledge Graph Sync):** Integrate with MusicBrainz/Spotify APIs using Song IDs to automatically correct and complete metadata.
- **Phase 4 (Deep Spectral Analysis):** Implement real-time mel-spectrogram streaming and sliding window extraction for neural classification (e.g., specific instrument identification, Indian Classical Ragas).
- **Phase 5 (Contextual Brain):** Enable advanced UI filtering and dynamic play queues based on deep structural insights and semantic tags.

## User Journey Flows
1. **Initial Scan & Fingerprinting:**
   - User adds a music directory.
   - System streams files, generates mel-spectrograms in the background, and maps them to Song IDs.
   - UI provides real-time progress feedback on acoustic analysis via the Scan Tab.
2. **Metadata Refinement & Conflict Resolution:**
   - System queries cloud knowledge graphs with Song IDs.
   - For ambiguous tracks (e.g., Live vs Studio), the neural classifier analyzes spectral layers (e.g., audience noise, specific instruments) and flags for user validation if confidence is below threshold.
   - UI prompts user in the Validation Tab with visual spectrogram anomalies for manual confirmation.
3. **Deep Search & Discovery:**
   - User queries "Acoustic Guitar, Slow Tempo" in the Organize Tab.
   - System queries the semantic SQLite database and instantly returns files matching those acoustic properties, regardless of filename or traditional text tags.
