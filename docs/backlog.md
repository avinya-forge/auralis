# Auralis Backlog

## Phase 3: Cognitive Intelligence (Neural Audio)
**Focus:** Integrating Deep Learning models (Hugging Face Transformers) for zero-shot classification and advanced audio understanding.

### Epic 11: Neural Core Infrastructure (AIService)

### Epic 12: Neural Features (The Brain)
- [NEU-003] | Implement `MusicTagger` (Genre/Mood/Instrument) using CLAP | [BLOCKS-AI-002] | [TODO]
- [NEU-004] | Implement `CoverSongDetector` using MERT Embeddings (Cosine Sim) | [BLOCKS-AI-002] | [TODO]
- [NEU-005] | Create `EmbeddingDatabase` (SQLite/JSON) to store track vectors | [BLOCKS-NEU-004] | [TODO]
- [NEU-006] | Implement `OriginalVersionFinder` logic (Release Date + Similarity) | [BLOCKS-NEU-004] | [TODO]
- [NEU-008] | Implement batch processing for AI analysis (prevent UI freeze) | [BLOCKS-AI-001] | [TODO]
- [NEU-009] | Create "Confidence Score" filter for AI tags (thresholding) | [BLOCKS-NEU-003] | [TODO]

### Epic 13: Cognitive UI/UX
- [AUX-002] | Implement "Analyze Raga" button and result display | [BLOCKS-AUX-001] | [TODO]
- [AUX-003] | Implement "Find Covers" context menu action in File List | [BLOCKS-AUX-001] | [TODO]
- [AUX-004] | Create `ModelDownloadDialog` with progress bar for 1GB+ downloads | [INDEPENDENT] | [TODO]
- [AUX-005] | Add "AI Settings" tab (Device selection, Model selection) | [INDEPENDENT] | [TODO]
- [AUX-006] | Implement "Smart Tagging" wizard (Auto-apply high confidence tags) | [BLOCKS-AUX-001] | [TODO]
- [AUX-008] | Implement "Similar Tracks" visual graph/list based on embeddings | [BLOCKS-NEU-005] | [TODO]

## Phase 2: Feature Enhancement (Residual Debt)
**Focus:** Closing gaps in existing Audio/Playlist functionality.

### Epic 7: Audio Analysis (Legacy Completion)

### Epic 8: Smart Playlists (Legacy Completion)
- [PL-008] | Add "Playlist Editor" UI Tab (CRUD operations) | [INDEPENDENT] | [TODO]

### Epic 6: Performance Optimization (Legacy Completion)
- [PERF-001] | Implement `LazyLoader` for album art images in ListWidget | [INDEPENDENT] | [TODO]
- [PERF-002] | Refactor `Scanner` to use `asyncio` for I/O operations (Experiment) | [INDEPENDENT] | [TODO]
- [PERF-003] | Implement `MetadataCache` using `sqlite3` (Persistent) | [INDEPENDENT] | [TODO]

## Phase 4: Ecosystem Expansion
**Focus:** Extending Auralis beyond the desktop app.

### Epic 9: Plugin System
- [PLG-004] | Add "Plugins" settings tab in UI | [INDEPENDENT] | [TODO]
- [PLG-005] | Implement `PluginSandbox` restrictions | [INDEPENDENT] | [TODO]
- [PLG-006] | Create documentation for Plugin API | [BLOCKS-PLG-001] | [TODO]
- [PLG-007] | Implement plugin dependency resolver | [BLOCKS-PLG-002] | [TODO]
- [PLG-008] | Add "Enable/Disable" plugin toggle logic | [BLOCKS-PLG-002] | [TODO]
- [PLG-009] | Create `ThemePlugin` specialization | [BLOCKS-PLG-001] | [TODO]

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

## Phase 5: Ecosystem Expansion
**Focus:** Expanding the capabilities of Auralis to form a complete music management ecosystem.

### Epic 19: Cloud Sync Engine
- [CLD-001] | Define `CloudProviderInterface` abstract class for sync [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [DONE]
- [CLD-002] | Implement `AWSProvider` for S3 backing [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-001] | [TODO]
- [CLD-003] | Implement `GoogleDriveProvider` for Drive backing [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-001] | [TODO]
- [CLD-004] | Add Cloud Settings Tab to configure provider [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [CLD-005] | Create SQLite-based `SyncStateTracker` [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [CLD-006] | Implement bi-directional diff generator [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-005] | [TODO]
- [CLD-007] | Build incremental push logic [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-006] | [TODO]
- [CLD-008] | Build incremental pull logic [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-006] | [TODO]
- [CLD-009] | Create progress indicator for sync operations [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [CLD-010] | Implement auto-sync scheduler on startup [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-CLD-007] | [TODO]

### Epic 20: Advanced DJ Tools
- [DJ-001] | Integrate beat grid analysis into `AudioAnalysisService` [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DJ-002] | Implement Camelot Wheel UI visualization [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DJ-003] | Build track transition recommender (Energy + Key) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DJ-001] | [TODO]
- [DJ-004] | Create `CrossfadeGenerator` using pydub [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DJ-005] | Generate single continuous mix file from playlist [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DJ-004] | [TODO]
- [DJ-006] | Save CUE sheet alongside continuous mix [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DJ-005] | [TODO]
- [DJ-007] | Add DJ Tools Tab to main interface [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DJ-008] | Implement loop region detection [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DJ-001] | [TODO]
- [DJ-009] | Export loops as separate stems [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DJ-008] | [TODO]
- [DJ-010] | Implement manual BPM tap counter [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 21: Lyrics Ecosystem
- [LYR-001] | Integrate LRC format parser [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [LYR-002] | Implement real-time karaoke display UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-001] | [TODO]
- [LYR-003] | Integrate whisper for auto-transcription of un-lyricized tracks [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [LYR-004] | Build sentiment analyzer for lyrics using transformers [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-003] | [TODO]
- [LYR-005] | Map lyric sentiment to UI color themes [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-004] | [TODO]
- [LYR-006] | Extract keyword tags from lyrics [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-004] | [TODO]
- [LYR-007] | Build full-text search index for lyrics in SQLite [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [LYR-008] | Add lyric snippet matching to main search bar [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-007] | [TODO]
- [LYR-009] | Implement bad word filter/explicit tagger [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-001] | [TODO]
- [LYR-010] | Add support for synchronized lyric editing [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-LYR-001] | [TODO]

### Epic 22: Hardware Integration
- [HW-001] | Build WASAPI/ASIO driver bridge for bit-perfect output [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [HW-002] | Implement MIDI mapping engine [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [HW-003] | Create MIDI learning UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-HW-002] | [TODO]
- [HW-004] | Support playback control via MIDI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-HW-002] | [TODO]
- [HW-005] | Support volume/EQ control via MIDI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-HW-002] | [TODO]
- [HW-006] | Implement global hotkeys daemon [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [HW-007] | Detect external DAC sample rate capabilities [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [HW-008] | Implement on-the-fly sample rate conversion [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-HW-007] | [TODO]
- [HW-009] | Build hardware status widget for status bar [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [HW-010] | Integrate with Stream Deck [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 23: Visualizer Suite
- [VIS-001] | Build FFT analyzer pipeline [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIS-002] | Implement basic spectrum analyzer widget [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIS-001] | [TODO]
- [VIS-003] | Create oscilloscope visualizer [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIS-001] | [TODO]
- [VIS-004] | Implement GPU acceleration for visualizers via OpenGL [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIS-005] | Build 'Album Art Colors' visualizer [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIS-004] | [TODO]
- [VIS-006] | Add full-screen visualization mode [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIS-007] | Implement visualizer plugin API [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIS-008] | Create fluid dynamics visualizer (WebGL wrapper) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIS-007] | [TODO]
- [VIS-009] | Tie beat detection to visualizer events [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIS-010] | Allow custom shader loading for visualizers [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIS-004] | [TODO]

### Epic 24: Database Refactoring
- [DB-001] | Define comprehensive SQLAlchemy ORM models [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DB-002] | Implement alembic for database migrations [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-001] | [TODO]
- [DB-003] | Migrate existing track metadata to new schema [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-001] | [TODO]
- [DB-004] | Implement Many-to-Many relationship for Artists/Tracks [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-001] | [TODO]
- [DB-005] | Implement Many-to-Many relationship for Genres/Tracks [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-001] | [TODO]
- [DB-006] | Create DB connection pool manager [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DB-007] | Refactor `MusicScanner` to stream straight to DB [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-006] | [TODO]
- [DB-008] | Implement fast full-text search indexing on DB level [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-001] | [TODO]
- [DB-009] | Add database backup and restore functionality [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DB-010] | Write migration tests [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DB-002] | [TODO]

### Epic 25: Social Discovery
- [SOC-001] | Implement Last.fm scrobbling client [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [SOC-002] | Build ListenBrainz scrobbling client [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [SOC-003] | Create 'Listening Now' presence module [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [SOC-004] | Integrate Discord Rich Presence [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-003] | [TODO]
- [SOC-005] | Build shared 'Listening Room' server socket [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [SOC-006] | Implement client-side 'Listening Room' UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-005] | [TODO]
- [SOC-007] | Sync playback state between room clients [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-005] | [TODO]
- [SOC-008] | Add chat functionality to Listening Room [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-006] | [TODO]
- [SOC-009] | Implement shared queue management [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-007] | [TODO]
- [SOC-010] | Allow exporting Listening Room history [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-SOC-009] | [TODO]

### Epic 26: Audio Enhancement Pipeline
- [DSP-001] | Integrate 10-band parametric EQ [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-002] | Build EQ preset manager [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DSP-001] | [TODO]
- [DSP-003] | Implement automatic EQ based on genre [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DSP-002] | [TODO]
- [DSP-004] | Integrate dynamic range compressor [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-005] | Build multi-band compressor UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DSP-004] | [TODO]
- [DSP-006] | Add stereo widener effect [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-007] | Implement true peak limiter [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-008] | Create DSP routing matrix [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-009] | Allow VST3 plugin hosting [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DSP-010] | Implement crossfeed for headphone listening [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 27: Podcast Ecosystem
- [POD-001] | Build RSS feed parser [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-002] | Implement Podcast Subscription manager [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-POD-001] | [TODO]
- [POD-003] | Create auto-downloader for new episodes [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-POD-002] | [TODO]
- [POD-004] | Add Podcast View Tab to UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-005] | Implement playback position tracking [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-006] | Build silence skipper specifically for spoken word [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-007] | Support chapter markers extraction [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-008] | Add chapter navigation UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-POD-007] | [TODO]
- [POD-009] | Implement variable speed playback without pitch shift [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [POD-010] | Create OPML import/export [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-POD-002] | [TODO]

### Epic 28: Vinyl Archiving
- [VIN-001] | Implement direct audio recording interface [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIN-002] | Add level metering and clipping detection [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIN-001] | [TODO]
- [VIN-003] | Build click/crackle removal algorithm [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIN-001] | [TODO]
- [VIN-004] | Implement auto track-splitting via silence detection [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIN-001] | [TODO]
- [VIN-005] | Add RIAA equalization curve filter [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIN-006] | Build Discogs release matcher via barcode/matrix [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIN-007] | Support high-res FLAC encoding parameters [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [VIN-008] | Create 'Vinyl Rip' workflow wizard [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIN-004] | [TODO]
- [VIN-009] | Allow manual track boundary editing [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-VIN-004] | [TODO]
- [VIN-010] | Implement metadata templating for vinyl series [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 29: Smart Rules Engine
- [RUL-001] | Define Rule AST (Abstract Syntax Tree) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [RUL-002] | Implement rule evaluation engine [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-001] | [TODO]
- [RUL-003] | Create visual rule builder UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-002] | [TODO]
- [RUL-004] | Add support for conditional file moving [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-002] | [TODO]
- [RUL-005] | Add support for conditional tagging [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-002] | [TODO]
- [RUL-006] | Implement periodic rule execution daemon [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-002] | [TODO]
- [RUL-007] | Add 'Watch Folder' trigger [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [RUL-008] | Support dry-run rule preview [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-002] | [TODO]
- [RUL-009] | Create community rule sharing format (JSON) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-RUL-001] | [TODO]
- [RUL-010] | Integrate with OS notification system for rule events [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 30: Multi-Room Audio Protocol
- [MRA-001] | Implement UPnP/DLNA controller [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [MRA-002] | Implement Chromecast sender protocol [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [MRA-003] | Build generic 'Casting' UI menu [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-MRA-001] | [TODO]
- [MRA-004] | Add AirPlay sender support [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [MRA-005] | Create synchronized clock mechanism [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [MRA-006] | Implement multi-zone volume control [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-MRA-003] | [TODO]
- [MRA-007] | Add grouped device management [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-MRA-006] | [TODO]
- [MRA-008] | Support streaming FLAC to capable receivers [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [MRA-009] | Implement fallback transcoding for legacy receivers [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-MRA-008] | [TODO]
- [MRA-010] | Write integration tests for casting protocols [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-MRA-001] | [TODO]

### Epic 31: Historical Analytics Engine
- [STA-001] | Track complete playback lifecycle events [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [STA-002] | Build heat map visualization of listening times [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-003] | Implement 'Year in Review' generator [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-004] | Calculate and display user genre affinity scores [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-005] | Detect 'Forgotten Favorites' [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-006] | Track artist discovery trajectory [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-007] | Build interactive data dashboard UI [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-002] | [TODO]
- [STA-008] | Allow exporting analytics raw data [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-009] | Implement local machine learning to predict next skip [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-STA-001] | [TODO]
- [STA-010] | Add support for importing Last.fm history for baseline [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 32: Library Deduplication Pro
- [DED-001] | Implement bit-perfect audio comparison [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-002] | Build fuzzy metadata matcher (Levenshtein) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-003] | Create 'Duplicate Resolver' UI wizard [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DED-002] | [TODO]
- [DED-004] | Add logic to select 'Best Quality' version automatically [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-005] | Implement cross-referencing against playlists to update paths [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DED-003] | [TODO]
- [DED-006] | Add hardlink creation option instead of deleting [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-007] | Support finding duplicates across disconnected drives [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-008] | Create detailed deletion report [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-DED-003] | [TODO]
- [DED-009] | Implement safe trash/recycling bin fallback [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [DED-010] | Add 'Find Similar Sounding' using embeddings [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]

### Epic 33: Game Audio Integration
- [GAM-001] | Detect running game processes [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-002] | Implement auto-pause/mute on game launch [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-GAM-001] | [TODO]
- [GAM-003] | Build profile mapping (Game -> Playlist) [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-GAM-001] | [TODO]
- [GAM-004] | Integrate Overwolf/Discord overlay for controls [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-005] | Create game-specific volume ducking [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [BLOCKS-GAM-001] | [TODO]
- [GAM-006] | Sync lighting effects to Razer Chroma [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-007] | Sync lighting effects to Corsair iCUE [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-008] | Create low-latency audio path [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-009] | Build 'Epic Moment' highlight clipping tool [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
- [GAM-010] | Add global hotkey for quick playlist switch [Test (95%), Lint (0-err), Opt (Big O), Sec (Sanitize)] | [INDEPENDENT] | [TODO]
