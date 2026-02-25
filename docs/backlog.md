# Auralis Backlog

## Phase 3: Cognitive Intelligence (Neural Audio)
**Focus:** Integrating Deep Learning models (Hugging Face Transformers) for zero-shot classification and advanced audio understanding.

### Epic 11: Neural Core Infrastructure (AIService)
- [AI-010] | Add `auralis ai check` CLI command to verify environment | [BLOCKS-AI-004] | [TODO]

### Epic 12: Neural Features (The Brain)
- [NEU-001] | Implement `RagaClassifier` using Zero-Shot CLAP | [BLOCKS-AI-002] | [TODO]
- [NEU-002] | Define standard list of 20+ common Ragas for classification prompt | [BLOCKS-NEU-001] | [TODO]
- [NEU-003] | Implement `MusicTagger` (Genre/Mood/Instrument) using CLAP | [BLOCKS-AI-002] | [TODO]
- [NEU-004] | Implement `CoverSongDetector` using MERT Embeddings (Cosine Sim) | [BLOCKS-AI-002] | [TODO]
- [NEU-005] | Create `EmbeddingDatabase` (SQLite/JSON) to store track vectors | [BLOCKS-NEU-004] | [TODO]
- [NEU-006] | Implement `OriginalVersionFinder` logic (Release Date + Similarity) | [BLOCKS-NEU-004] | [TODO]
- [NEU-007] | Add `TXXX:RAGA` and `TXXX:AI_MOOD` tag handlers in `MusicScanner` | [INDEPENDENT] | [TODO]
- [NEU-008] | Implement batch processing for AI analysis (prevent UI freeze) | [BLOCKS-AI-001] | [TODO]
- [NEU-009] | Create "Confidence Score" filter for AI tags (thresholding) | [BLOCKS-NEU-003] | [TODO]
- [NEU-010] | Write integration tests for `RagaClassifier` (using sample audio) | [BLOCKS-NEU-001] | [TODO]

### Epic 13: Cognitive UI/UX
- [AUX-001] | Create `AIPanel` widget for `MetadataTab` | [INDEPENDENT] | [TODO]
- [AUX-002] | Implement "Analyze Raga" button and result display | [BLOCKS-AUX-001] | [TODO]
- [AUX-003] | Implement "Find Covers" context menu action in File List | [BLOCKS-AUX-001] | [TODO]
- [AUX-004] | Create `ModelDownloadDialog` with progress bar for 1GB+ downloads | [INDEPENDENT] | [TODO]
- [AUX-005] | Add "AI Settings" tab (Device selection, Model selection) | [INDEPENDENT] | [TODO]
- [AUX-006] | Implement "Smart Tagging" wizard (Auto-apply high confidence tags) | [BLOCKS-AUX-001] | [TODO]
- [AUX-007] | Add visual "Brain" icon/indicator when AI processing is active | [INDEPENDENT] | [TODO]
- [AUX-008] | Implement "Similar Tracks" visual graph/list based on embeddings | [BLOCKS-NEU-005] | [TODO]
- [AUX-009] | Add CLI command `auralis ai analyze <file>` | [INDEPENDENT] | [TODO]
- [AUX-010] | Add CLI command `auralis ai covers <dir>` | [INDEPENDENT] | [TODO]

## Phase 2: Feature Enhancement (Residual Debt)
**Focus:** Closing gaps in existing Audio/Playlist functionality.

### Epic 7: Audio Analysis (Legacy Completion)
- [AUD-006] | Implement `AudioFingerprinter` using `pyacoustid` (Chromaprint) | [INDEPENDENT] | [TODO]
- [AUD-007] | Create `DuplicateFinder` based on audio fingerprints (Exact Match) | [BLOCKS-AUD-006] | [TODO]
- [AUD-008] | Implement `SilenceTrimmer` utility using `pydub` | [INDEPENDENT] | [TODO]
- [AUD-009] | Add "Loudness Normalization" (ReplayGain) calculator | [INDEPENDENT] | [TODO]
- [AUD-010] | Integrate ReplayGain tags into `MetadataService` | [BLOCKS-AUD-009] | [TODO]
- [AUD-011] | Add unit tests for `SilenceTrimmer` | [BLOCKS-AUD-008] | [TODO]
- [AUD-012] | Add unit tests for `ReplayGain` calculator | [BLOCKS-AUD-009] | [TODO]

### Epic 8: Smart Playlists (Legacy Completion)
- [PL-004] | Implement "Flow Mode" (Match Key + BPM) logic details | [INDEPENDENT] | [TODO]
- [PL-007] | Implement "Similar Tracks" finder (Cosine Similarity - Legacy Features) | [INDEPENDENT] | [TODO]
- [PL-008] | Add "Playlist Editor" UI Tab (CRUD operations) | [INDEPENDENT] | [TODO]
- [PL-009] | Implement "History" tracker persistence | [INDEPENDENT] | [TODO]
- [PL-010] | Add "Export to Spotify" (CSV) stub | [INDEPENDENT] | [TODO]

### Epic 6: Performance Optimization (Legacy Completion)
- [PERF-001] | Implement `LazyLoader` for album art images in ListWidget | [INDEPENDENT] | [TODO]
- [PERF-002] | Refactor `Scanner` to use `asyncio` for I/O operations (Experiment) | [INDEPENDENT] | [TODO]
- [PERF-003] | Implement `MetadataCache` using `sqlite3` (Persistent) | [INDEPENDENT] | [TODO]

## Phase 4: Ecosystem Expansion
**Focus:** Extending Auralis beyond the desktop app.

### Epic 9: Plugin System
- [PLG-001] | Define `PluginInterface` abstract base class | [INDEPENDENT] | [TODO]
- [PLG-002] | Create `PluginLoader` using `importlib` | [BLOCKS-PLG-001] | [TODO]
- [PLG-003] | Implement "Hello World" sample plugin | [BLOCKS-PLG-002] | [TODO]
- [PLG-004] | Add "Plugins" settings tab in UI | [INDEPENDENT] | [TODO]
- [PLG-005] | Implement `PluginSandbox` restrictions | [INDEPENDENT] | [TODO]
- [PLG-006] | Create documentation for Plugin API | [BLOCKS-PLG-001] | [TODO]
- [PLG-007] | Implement plugin dependency resolver | [BLOCKS-PLG-002] | [TODO]
- [PLG-008] | Add "Enable/Disable" plugin toggle logic | [BLOCKS-PLG-002] | [TODO]
- [PLG-009] | Create `ThemePlugin` specialization | [BLOCKS-PLG-001] | [TODO]
- [PLG-010] | Write unit tests for `PluginLoader` | [BLOCKS-PLG-002] | [TODO]

### Epic 10: Remote API
- [API-001] | Design REST API spec (OpenAPI/Swagger) | [INDEPENDENT] | [TODO]
- [API-002] | Implement lightweight Flask/FastAPI server | [INDEPENDENT] | [TODO]
- [API-003] | Implement `GET /status` endpoint | [BLOCKS-API-002] | [TODO]
- [API-004] | Implement `POST /scan` endpoint | [BLOCKS-API-002] | [TODO]
- [API-005] | Implement `POST /organize` endpoint | [BLOCKS-API-002] | [TODO]
- [API-006] | Implement `GET /library` endpoint (Pagination) | [BLOCKS-API-002] | [TODO]
- [API-007] | Implement `GET /track/{id}` endpoint | [BLOCKS-API-002] | [TODO]
- [API-008] | Add API Authentication (Basic/Token) | [BLOCKS-API-002] | [TODO]
- [API-009] | Create `APIServerThread` for GUI integration | [BLOCKS-API-002] | [TODO]
- [API-010] | Add "Enable Remote API" toggle in Settings | [INDEPENDENT] | [TODO]
