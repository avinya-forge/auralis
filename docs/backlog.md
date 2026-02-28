# Auralis Backlog

## Phase 3: Cognitive Intelligence (Neural Audio)
**Focus:** Integrating Deep Learning models (Hugging Face Transformers) for zero-shot classification and advanced audio understanding.

### Epic 11: Neural Core Infrastructure (AIService)

### Epic 12: Neural Features (The Brain)
- [NEU-002] | Define standard list of 20+ common Ragas for classification prompt | [BLOCKS-NEU-001] | [TODO]
- [NEU-003] | Implement `MusicTagger` (Genre/Mood/Instrument) using CLAP | [BLOCKS-AI-002] | [TODO]
- [NEU-004] | Implement `CoverSongDetector` using MERT Embeddings (Cosine Sim) | [BLOCKS-AI-002] | [TODO]
- [NEU-005] | Create `EmbeddingDatabase` (SQLite/JSON) to store track vectors | [BLOCKS-NEU-004] | [TODO]
- [NEU-006] | Implement `OriginalVersionFinder` logic (Release Date + Similarity) | [BLOCKS-NEU-004] | [TODO]
- [NEU-008] | Implement batch processing for AI analysis (prevent UI freeze) | [BLOCKS-AI-001] | [TODO]
- [NEU-009] | Create "Confidence Score" filter for AI tags (thresholding) | [BLOCKS-NEU-003] | [TODO]

### Epic 13: Cognitive UI/UX
- [AUX-001] | Create `AIPanel` widget for `MetadataTab` | [INDEPENDENT] | [DONE]
- [AUX-002] | Implement "Analyze Raga" button and result display | [BLOCKS-AUX-001] | [TODO]
- [AUX-003] | Implement "Find Covers" context menu action in File List | [BLOCKS-AUX-001] | [TODO]
- [AUX-004] | Create `ModelDownloadDialog` with progress bar for 1GB+ downloads | [INDEPENDENT] | [TODO]
- [AUX-005] | Add "AI Settings" tab (Device selection, Model selection) | [INDEPENDENT] | [TODO]
- [AUX-006] | Implement "Smart Tagging" wizard (Auto-apply high confidence tags) | [BLOCKS-AUX-001] | [TODO]
- [AUX-007] | Add visual "Brain" icon/indicator when AI processing is active | [INDEPENDENT] | [TODO]
- [AUX-008] | Implement "Similar Tracks" visual graph/list based on embeddings | [BLOCKS-NEU-005] | [TODO]
- [AUX-009] | Add CLI command `auralis ai analyze <file>` | [INDEPENDENT] | [DONE]
- [AUX-010] | Add CLI command `auralis ai covers <dir>` | [INDEPENDENT] | [DONE]

## Phase 2: Feature Enhancement (Residual Debt)
**Focus:** Closing gaps in existing Audio/Playlist functionality.

### Epic 7: Audio Analysis (Legacy Completion)
- [AUD-006] | Implement `AudioFingerprinter` using `pyacoustid` (Chromaprint) | [INDEPENDENT] | [TODO]
- [AUD-008] | Implement `SilenceTrimmer` utility using `pydub` | [INDEPENDENT] | [TODO]
- [AUD-011] | Add unit tests for `SilenceTrimmer` | [BLOCKS-AUD-008] | [TODO]

### Epic 8: Smart Playlists (Legacy Completion)
- [PL-008] | Add "Playlist Editor" UI Tab (CRUD operations) | [INDEPENDENT] | [TODO]
- [PL-009] | Implement "History" tracker persistence | [INDEPENDENT] | [DONE]
- [PL-010] | Add "Export to Spotify" (CSV) stub | [INDEPENDENT] | [DONE]

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

### Epic 14: Mobile Companion Node (Sync, offline playback)
- [MOB-001] | Create MobileSyncService for local network discovery | [INDEPENDENT] | [TODO]
- [MOB-002] | Implement WebSocket API for real-time track updates | [BLOCKS-MOB-001] | [TODO]
- [MOB-003] | Add "Send to Mobile" right-click action in UI | [INDEPENDENT] | [TODO]
- [MOB-004] | Design offline caching strategy using SQLite | [INDEPENDENT] | [TODO]
- [MOB-005] | Create SyncSettingsTab in Preferences | [INDEPENDENT] | [TODO]

### Epic 15: P2P Mesh Network (Library sharing)
- [P2P-001] | Implement libp2p node initialization logic | [INDEPENDENT] | [TODO]
- [P2P-002] | Create distributed hash table (DHT) for track indexing | [BLOCKS-P2P-001] | [TODO]
- [P2P-003] | Implement chunked file transfer protocol over mesh | [BLOCKS-P2P-001] | [TODO]
- [P2P-004] | Add "Discover Network Libraries" UI widget | [INDEPENDENT] | [TODO]
- [P2P-005] | Establish network security/encryption layer | [BLOCKS-P2P-001] | [TODO]

### Epic 16: LLM Voice Oracle (Natural language querying)
- [LLM-001] | Integrate local Whisper model for STT | [INDEPENDENT] | [TODO]
- [LLM-002] | Map natural language intent to playlist filters (SQL builder) | [BLOCKS-LLM-001] | [TODO]
- [LLM-003] | Add voice capture button to Main Toolbar | [INDEPENDENT] | [TODO]
- [LLM-004] | Implement conversational feedback using local TTS | [INDEPENDENT] | [TODO]
- [LLM-005] | Create memory context window for chained queries | [BLOCKS-LLM-002] | [TODO]

### Epic 17: Spatial Audio Engine (3D audio playback)
- [SPA-001] | Integrate OpenAL or equivalent for 3D positioning | [INDEPENDENT] | [TODO]
- [SPA-002] | Map "Mood" metadata to spatial reverb presets | [BLOCKS-SPA-001] | [TODO]
- [SPA-003] | Add Spatial Audio toggle in Playback UI | [INDEPENDENT] | [TODO]
- [SPA-004] | Implement head-tracking placeholder logic | [INDEPENDENT] | [TODO]
- [SPA-005] | Write unit tests for spatial DSP chain | [BLOCKS-SPA-001] | [TODO]

### Epic 18: Cloudless Identity (Local user profiles)
- [ID-001] | Create local User authentication schema (SQLite) | [INDEPENDENT] | [TODO]
- [ID-002] | Implement Profile switching UI | [BLOCKS-ID-001] | [TODO]
- [ID-003] | Segment Playlist and History tables by User ID | [BLOCKS-ID-001] | [TODO]
- [ID-004] | Add personal listening stats aggregation | [BLOCKS-ID-003] | [TODO]
- [ID-005] | Implement profile export/import (JSON) | [INDEPENDENT] | [TODO]
