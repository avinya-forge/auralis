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

## Phase 5: Seamless Ecosystem Sync
### EPIC-19: Auralis Sync Engine (Device & Cloud)
- [TSK-19-001] | Implement generic SyncProtocol interface for device connectors | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-002] | Create LocalDirectorySyncProvider for USB/MTP devices | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-003] | Develop CloudSyncProvider base class for standard REST backends | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-004] | Implement WebDAVSyncProvider using python-webdav-client | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-003] | [TODO]
- [TSK-19-005] | Create NextcloudSyncProvider with chunked upload support | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-006] | Develop SyncConflictResolver using last-modified timestamp heuristics | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-007] | Implement NeuralTagMergeStrategy for retaining Auralis metadata during sync | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-006] | [TODO]
- [TSK-19-008] | Create SmartPlaylistSyncAdapter to convert Auralis dynamic lists to M3U8 for devices | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-009] | Implement SyncManager background thread with progress callback events | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-010] | Create SyncStatusStore (SQLite) to track file hashes and sync history | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-009] | [TODO]
- [TSK-19-011] | Develop DeltaSyncAlgorithm to only transfer modified or new files | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-012] | Implement SyncPauseResume mechanism using partial file transfers | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-013] | Create SyncUI Tab in MainWindow for managing active connections | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-012] | [TODO]
- [TSK-19-014] | Develop DeviceDiscoveryService to auto-detect attached USB volumes | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-015] | Implement CloudConfigDialog for OAuth/Basic Auth credential input | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-016] | Create SyncConflictUI to allow user override on complex metadata collisions | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-015] | [TODO]
- [TSK-19-017] | Develop SyncLoggingService to write detailed sync traces to disk | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-018] | Implement SyncScheduler for automated daily/weekly background syncs | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-19-019] | Create CLI command `auralis sync run <profile>` for headless operation | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-19-018] | [TODO]
- [TSK-19-020] | Add end-to-end integration tests for LocalDirectorySyncProvider | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 6: Sonic Perfection
### EPIC-20: Audiophile DSP Chain
- [TSK-20-001] | Implement DSPNode abstract base class with process(buffer) method | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-002] | Create DSPChain manager to route audio buffers through active nodes | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-003] | Develop ParametricEQNode (10-band) using SciPy biquad filters | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-004] | Implement DynamicRangeCompressorNode with adjustable threshold, ratio, attack, release | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-003] | [TODO]
- [TSK-20-005] | Create StereoEnhancerNode using mid-side processing matrix | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-006] | Develop CrossfeedNode to reduce listening fatigue on headphones (Bauer model) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-007] | Implement BitcrusherNode (Lo-Fi effect) with variable bit depth and sample rate reduction | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-006] | [TODO]
- [TSK-20-008] | Create ConvolutionReverbNode using fast FFT-based convolution | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-009] | Develop ReverbImpulseResponseLoader for parsing standard WAV IR files | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-010] | Implement DSPPresetManager to save/load filter configurations as JSON | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-009] | [TODO]
- [TSK-20-011] | Create DSPUI Panel in MainWindow with interactive EQ curve visualization | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-012] | Develop CompressorUI Widget with real-time gain reduction meter | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-013] | Implement ReverbUI Panel with impulse response visualizer | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-012] | [TODO]
- [TSK-20-014] | Create DSPBypassToggle to quickly A/B test the active processing chain | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-015] | Develop DSPLatencyCompensator to maintain sync with UI visualizations | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-016] | Implement AudioBufferPool to reduce GC pressure during DSP execution | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-015] | [TODO]
- [TSK-20-017] | Create CLI command `auralis dsp render <input> <output> <preset>` for offline processing | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-018] | Add SIMD/NumPy optimizations to ParametricEQNode process loop | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-20-019] | Develop integration tests verifying bit-perfect passthrough when DSP is bypassed | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-20-018] | [TODO]
- [TSK-20-020] | Implement automated performance benchmarks for DSPChain (target <5ms per block) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 7: Cognitive Analytics
### EPIC-21: Neural Library Insights
- [TSK-21-001] | Implement LibraryStatsAggregator for counting genre, mood, and era distributions | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-002] | Create VectorSpaceAnalyzer using PCA/t-SNE to map audio embeddings to 2D coordinates | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-003] | Develop LibraryInsightsUI Dashboard to display aggregated statistics | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-004] | Implement EmbeddingScatterPlot widget using PyQtGraph/matplotlib | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-003] | [TODO]
- [TSK-21-005] | Create HarmonicDensityMapper to visualize key distribution across the entire library | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-006] | Develop BPMHeatmapGenerator to show tempo trends over release decades | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-007] | Implement RagaDistributionChart to display cultural tonality spread | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-006] | [TODO]
- [TSK-21-008] | Create NeuralClusteringAlgorithm (K-Means) to group similar tracks without tags | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-009] | Develop ClusterNamingHeuristic based on dominant tags within a cluster | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-010] | Implement PlaylistRecommendationEngine using user listening history and track embeddings | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-009] | [TODO]
- [TSK-21-011] | Create 'Rediscover' Smart Playlist generator targeting forgotten, highly-rated tracks | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-012] | Develop 'Sonic Journey' Playlist generator that slowly transitions BPM and Mood | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-013] | Implement LibraryAnomalyDetector to find mis-tagged or corrupted audio files based on neural mismatch | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-012] | [TODO]
- [TSK-21-014] | Create InsightsExportService to generate PDF/HTML reports of library stats | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-015] | Develop HabitTrackerService to log playtime, skip rates, and completion rates (local only) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-016] | Implement ListeningTrendsGraph showing genre/mood preference changes over time | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-015] | [TODO]
- [TSK-21-017] | Create 'Year in Review' local summary generator (Auralis Wrapped) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-018] | Develop CLI command `auralis insights generate` to dump stats to JSON | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-21-019] | Add extensive unit tests for VectorSpaceAnalyzer coordinate generation | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-21-018] | [TODO]
- [TSK-21-020] | Implement query caching for LibraryStatsAggregator to improve Dashboard load times | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 8: Format Fluidity
### EPIC-22: Advanced Transcoding Matrix
- [TSK-22-001] | Implement FFmpegWrapper leveraging subprocess with dynamic binary resolution | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-002] | Create TranscodeJob data class encapsulating source, target, and bitrates | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-003] | Develop TranscodeQueueManager with configurable worker thread pool | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-004] | Implement FLACtoMP3Encoder profile with LAME V0 variable bitrate defaults | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-003] | [TODO]
- [TSK-22-005] | Create WAVtoFLACEncoder profile with maximum compression level | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-006] | Develop OPUSConversionProfile optimized for low-bandwidth mobile streaming | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-007] | Implement MetadataTransferUtility to map Vorbis comments to ID3v2 during transcode | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-006] | [TODO]
- [TSK-22-008] | Create CoverArtEmbedder for ensuring transcoded files retain album artwork | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-009] | Develop TranscodeProgressMonitor emitting granular percentage updates via callbacks | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-010] | Implement TranscodeUI Dialog for configuring batch conversion options | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-009] | [TODO]
- [TSK-22-011] | Create JobQueueWidget to display active, pending, and failed transcode tasks | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-012] | Develop FFmpegInstallationDetector providing automated download prompts if missing | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-013] | Implement TranscodeErrorAnalyzer to parse FFmpeg stderr and map to user-friendly messages | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-012] | [TODO]
- [TSK-22-014] | Create AutoTranscodeRuleEngine (e.g., 'Always convert >24bit/96kHz to 16bit/44.1kHz for device X') | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-015] | Develop TranscodeCacheManager for storing frequently converted tracks | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-016] | Implement CLI command `auralis transcode <dir> --format mp3 --vbr 0` | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-015] | [TODO]
- [TSK-22-017] | Create DirectoryMirrorService to replicate a FLAC library structure into an MP3 library | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-018] | Develop GaplessPlaybackVerification utility for transcoded albums | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-22-019] | Add integration tests verifying bit-rate and channel mapping across formats | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-22-018] | [TODO]
- [TSK-22-020] | Implement hardware acceleration probes (NVENC/VAAPI/VideoToolbox) for faster encode | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 9: Deep Text Understanding
### EPIC-23: Semantic Lyric Comprehension
- [TSK-23-001] | Integrate lightweight local NLP pipeline (e.g., spacy) for lyric tokenization | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-002] | Create LyricSentimentAnalyzer to score tracks on a positive/negative/neutral axis | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-003] | Develop ThemeExtractionEngine using TF-IDF and zero-shot classification on lyrics | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-004] | Implement SyncedLyricAligner utilizing dynamic time warping (DTW) against audio envelopes | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-003] | [TODO]
- [TSK-23-005] | Create LRCParserService to validate and normalize inconsistent LRC file formats | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-006] | Develop LyricTopicMapper defining 50+ common lyrical themes (Love, Rebellion, Nature, etc.) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-007] | Implement ExplicitContentDetector using heuristic lists and context-aware NLP | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-006] | [TODO]
- [TSK-23-008] | Create SemanticSearchIndex (SQLite FTS5) enabling complex lyric queries ('songs about winter') | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-009] | Develop LyricUI Panel featuring dynamic scrolling synced to playback time | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-010] | Implement TranslationService prototype using local MarianMT models for cross-lingual lyrics | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-009] | [TODO]
- [TSK-23-011] | Create SentimentTrendGraph showing narrative arc (sentiment over time) within a single track | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-012] | Develop VocabularyDensityAnalyzer calculating unique word ratios per artist | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-013] | Implement MissingLyricHeuristic to auto-fetch when confidence is low or files are absent | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-012] | [TODO]
- [TSK-23-014] | Create LyricalSimilarityEngine computing cosine distance between track lyric vectors | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-015] | Develop 'Lyrically Similar' Smart Playlist generator | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-016] | Implement UI Highlighting for named entities (Places, People) detected in lyrics | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-015] | [TODO]
- [TSK-23-017] | Create CLI command `auralis lyrics analyze <file>` to output semantic JSON | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-018] | Add unit tests for DTW alignment logic in SyncedLyricAligner | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-23-019] | Develop caching layer for LyricSentimentAnalyzer to prevent re-computing static text | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-23-018] | [TODO]
- [TSK-23-020] | Implement integration with MetadataSanitizer to ensure extracted themes are saved as TXXX tags | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 10: Relational Topology
### EPIC-24: Graph-Based Library Navigation
- [TSK-24-001] | Implement GraphDataModel defining Nodes (Artist, Album, Track, Genre) and Edges (Similarity, Features) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-002] | Create SQLiteGraphAdapter to construct relational queries mapping traditional metadata to graph structures | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-003] | Develop ForceDirectedLayoutEngine for calculating 2D node positions dynamically | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-004] | Implement WebGLGraphRenderer (via QWebEngine/WebView) for high-performance visual rendering | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-003] | [TODO]
- [TSK-24-005] | Create NodeInteractionHandler (Click, Hover, Drag) routing events to Auralis core functions | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-006] | Develop ArtistConstellationBuilder linking artists via shared session musicians (BioProvider integration) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-007] | Implement GenreEvolutionTree tracing ancestral links between musical styles | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-006] | [TODO]
- [TSK-24-008] | Create NeuralSimilarityEdges connecting nodes based on MERT/CLAP embedding distance | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-009] | Develop 'Six Degrees' pathfinding algorithm (Dijkstra) between any two artists | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-010] | Implement GraphFilterUI allowing users to toggle edge types (e.g., hide genre links, show only neural links) | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-009] | [TODO]
- [TSK-24-011] | Create NodeDetailOverlay displaying metadata when hovering over graph elements | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-012] | Develop GraphPlaybackQueue integrating node selection directly into the active playlist | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-013] | Implement 'Wander Mode' where playback traverses the graph via nearest-neighbor algorithms | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-012] | [TODO]
- [TSK-24-014] | Create SubGraphExtractor to isolate and visualize specific library niches (e.g., '1990s Trip-Hop') | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-015] | Develop GraphExportUtility generating DOT/Graphviz files for external analysis | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-016] | Implement GraphStatePersistence saving node positions and zoom levels across sessions | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-015] | [TODO]
- [TSK-24-017] | Create CLI command `auralis graph build` to pre-compute heavy relational edges | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-018] | Add unit tests for ForceDirectedLayoutEngine physics calculations | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-24-019] | Develop performance benchmark for rendering >10,000 nodes simultaneously | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-24-018] | [TODO]
- [TSK-24-020] | Implement caching mechanism for 'Six Degrees' pathfinding queries | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 11: Synesthetic Experience
### EPIC-25: Audiovisual Synthesis Engine
- [TSK-25-001] | Implement AudioFeatureExtractor thread providing low-latency FFT, RMS, and spectral flux streams | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-002] | Create VisualizerPluginInterface defining init(), render(features), and teardown() | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-003] | Develop OpenGLCanvas widget for high-performance rendering integration | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-004] | Implement OscilloscopeVisualizer (Time-domain waveform rendering) | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-003] | [TODO]
- [TSK-25-005] | Create SpectrogramVisualizer (Frequency-domain waterfall rendering) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-006] | Develop ReactiveParticleSystem mapping spectral flux to particle velocity and color | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-007] | Implement ChromagramVisualizer mapping harmonic content to color wheels (Circle of Fifths) | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-006] | [TODO]
- [TSK-25-008] | Create BeatSyncHeuristic utilizing onset detection to trigger visual flashes/camera shakes | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-009] | Develop GenerativeShaderLoader executing GLSL fragment shaders driven by audio uniforms | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-010] | Implement 'Neural Dream' visualizer modulating Stable Diffusion latent space via audio embeddings | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-009] | [TODO]
- [TSK-25-011] | Create VisualizerSettingsUI panel to adjust sensitivity, decay, and color palettes | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-012] | Develop FullscreenManager handling multi-monitor boundary transitions and exclusive mode | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-013] | Implement VisualizerPresetManager saving shader configurations and audio mappings | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-012] | [TODO]
- [TSK-25-014] | Create BackgroundRenderMode allowing visualizers to run as an OS wallpaper (Windows/Linux specific API) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-015] | Develop FrameRateGovernor ensuring audio playback thread is never starved by rendering thread | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-016] | Implement VideoExportUtility capturing visualizer output to MP4 via FFmpeg | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-015] | [TODO]
- [TSK-25-017] | Create CLI command `auralis render-video <track> <visualizer> <output>` | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-018] | Add integration tests verifying AudioFeatureExtractor latency (<16ms) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-25-019] | Develop robust error handling for bad GLSL compilation in GenerativeShaderLoader | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-25-018] | [TODO]
- [TSK-25-020] | Implement smooth interpolation (lerp) for audio uniforms to prevent visual jitter | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 12: Collective Truth
### EPIC-26: Decentralized Metadata Consensus
- [TSK-26-001] | Implement GossipProtocolEngine handling node discovery and message propagation | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-002] | Create MetadataProposalSchema defining JSON structure for suggested tag edits | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-003] | Develop LocalTrustScore mechanism evaluating peer reliability based on accepted proposals | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-004] | Implement ConsensusAlgorithm (e.g., majority vote with trust weighting) for resolving conflicting tags | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-003] | [TODO]
- [TSK-26-005] | Create AcoustIDBridge using audio fingerprints as the immutable primary key for network queries | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-006] | Develop NetworkBlacklist rejecting proposals from nodes distributing malformed or malicious data | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-007] | Implement FederatedSearchService allowing cross-node queries for missing lyrics or bios | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-006] | [TODO]
- [TSK-26-008] | Create MetadataBountySystem tracking which local files require community resolution | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-009] | Develop ConsensusUI Dashboard displaying active proposals and network health | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-010] | Implement AutoAcceptRules (e.g., 'Accept typos fixes automatically, require manual review for genre changes') | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-009] | [TODO]
- [TSK-26-011] | Create ContributionStatsTracker logging user's accepted proposals to the network | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-012] | Develop DecentralizedCoverArtCache utilizing IPFS or similar chunked DHT storage | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-013] | Implement NetworkRateLimiter preventing local node exhaustion from inbound queries | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-012] | [TODO]
- [TSK-26-014] | Create CLI command `auralis net start` to run node in headless background mode | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-015] | Develop P2PConnectionEncrypter ensuring all gossip traffic is TLS/Noise secured | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-016] | Implement NetworkBootstrapper utilizing hardcoded seed nodes or local mDNS | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-015] | [TODO]
- [TSK-26-017] | Create DatabaseMigration script preparing SQLite schema for multi-signature metadata | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-018] | Add simulation tests running 50+ local nodes verifying consensus convergence | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-26-019] | Develop conflict resolution UI allowing manual override of network consensus | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-26-018] | [TODO]
- [TSK-26-020] | Implement periodic state snapshotting to accelerate node startup times | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 13: Archival Healing
### EPIC-27: Adaptive Audio Restorer
- [TSK-27-001] | Integrate Demucs (or similar source separation model) via ModelLoader | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-002] | Create StemSeparationService to isolate vocals, drums, bass, and other from a stereo mix | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-003] | Develop DeClippingAlgorithm detecting consecutive max-amplitude samples and interpolating smooth curves | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-004] | Implement VinylDeClicker using median filtering and wavelet transforms | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-003] | [TODO]
- [TSK-27-005] | Create TapeHissRemover utilizing spectral gating based on ambient noise profiling | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-006] | Develop RestorationJobManager queuing heavy AI restoration tasks to prevent UI blocking | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-007] | Implement StemMixerUI allowing real-time volume adjustment of separated stems | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-006] | [TODO]
- [TSK-27-008] | Create KaraokeMode generator that automatically phase-cancels or mutes the vocal stem | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-009] | Develop DrumExtractUtility exporting isolated drum breaks to WAV for production use | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-010] | Implement AudioDiffAnalyzer computing phase difference between original and restored files | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-009] | [TODO]
- [TSK-27-011] | Create RestorationPreview widget enabling quick A/B looping of a processed 5-second segment | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-012] | Develop AutoMasteringHeuristic applying subtle EQ/Compression to match target LUFS post-restoration | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-013] | Implement ArchivalMetadataWriter appending restoration logs to `TXXX:AURALIS_RESTORE` tags | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-012] | [TODO]
- [TSK-27-014] | Create CLI command `auralis restore <file> --declip --declick` | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-015] | Develop CLI command `auralis unmix <file> --stems 4` | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-016] | Implement hardware acceleration (CUDA/MPS) explicitly for the Demucs separation pipeline | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-015] | [TODO]
- [TSK-27-017] | Create FileBackupManager ensuring the original file is duplicated before destructive restoration | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-018] | Add comprehensive unit tests for DeClippingAlgorithm math logic | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-27-019] | Develop memory management protocol for StemSeparationService handling large audio tensors | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-27-018] | [TODO]
- [TSK-27-020] | Implement progress tracking UI that accurately reflects AI model inference stages | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]

## Phase 14: System Orchestration
### EPIC-28: Macro-Workflow Automation
- [TSK-28-001] | Implement EventBus architecture publishing core signals (FileAdded, ScanComplete, PlaybackStarted) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-002] | Create WorkflowEngine evaluating triggers and executing defined action sequences | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-003] | Develop VisualScriptingUI utilizing standard node-graph libraries (e.g., NodeGraphQt) | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-004] | Implement TriggerNodes (e.g., 'On New Folder Detected', 'On Tag Update') | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-003] | [TODO]
- [TSK-28-005] | Create ActionNodes (e.g., 'Transcode to MP3', 'Fetch Lyrics', 'Analyze Raga', 'Move to Dir') | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-006] | Develop ConditionNodes (e.g., 'If Genre == Jazz', 'If Bitrate < 320') | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-007] | Implement PythonScriptNode allowing custom Python execution within the workflow context | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-006] | [TODO]
- [TSK-28-008] | Create WorkflowSerializer saving graph state to JSON execution plans | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-009] | Develop MacroRecorder tracking user UI actions and converting them to a repeatable workflow | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-010] | Implement ScheduledWorkflowRunner executing macros via cron-style syntax | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-009] | [TODO]
- [TSK-28-011] | Create WorkflowLogViewer displaying success/failure states of automated executions | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-012] | Develop SafeExecutionSandbox restricting PythonScriptNode access to OS-level functions | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-013] | Implement DryRunMode simulating a workflow and reporting planned changes without execution | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-012] | [TODO]
- [TSK-28-014] | Create CommunityMacroRepository integrated into the UI for sharing workflow JSONs | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-015] | Develop 'Auto-DJ' Macro template transitioning tracks based on time of day and user mood | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-016] | Implement 'Library Janitor' Macro template automatically identifying and purging duplicates weekly | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-015] | [TODO]
- [TSK-28-017] | Create CLI command `auralis macro run <workflow_name>` | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-018] | Add unit tests validating complex logic flow (Nested IFs, Loops) in WorkflowEngine | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
- [TSK-28-019] | Develop robust error handling preventing a failed action node from crashing the entire application | [Test] [Lint] [Opt] [Sec] [Doc] | [BLOCKS-TSK-28-018] | [TODO]
- [TSK-28-020] | Implement ExecutionRateLimiter preventing infinite loops in cyclic workflow graphs | [Test] [Lint] [Opt] [Sec] [Doc] | [INDEPENDENT] | [TODO]
