# Auralis Backlog

> **North Star**: Orchestrating Roadmap via Milestone Schema.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-003: Implement `musictagger` (genre/mood/instrument) using clap** | [TODO] | [src/modules/neu]
- **SPEC:** Integrate `laion/clap-htsat-unfused` via Hugging Face Transformers. Create a `MusicTagger` class in `src/modules/neu` that loads the model into CPU/GPU cache and exposes a `tag_audio(file_path)` method returning a dictionary of `genre`, `mood`, and `instrument` scores.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-004: Implement `coversongdetector` using mert embeddings (cosine sim)** | [TODO] | [src/modules/neu]
- **SPEC:** Utilize `m-a-p/MERT-v1-95M` to extract track embeddings. Implement `CoverSongDetector` in `src/modules/neu` to calculate cosine similarity between track vectors. Add a `find_covers(target_embedding)` method.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-005: Create `embeddingdatabase` (sqlite/json) to store track vectors** | [TODO] | [src/modules/neu]
- **SPEC:** Build a lightweight SQLite adapter `EmbeddingDatabase` in `src/modules/neu`. The schema must include `track_id (VARCHAR)`, `vector_blob (BLOB)`, and `model_version (VARCHAR)`. Implement `upsert_embedding` and `search_similar`.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-006: Implement `originalversionfinder` logic (release date + similarity)** | [TODO] | [src/modules/neu]
- **SPEC:** Create `OriginalVersionFinder` in `src/modules/neu`. Logic: query `EmbeddingDatabase` for vectors with >0.9 similarity, then query `MusicBrainz` API for release dates. Return the oldest track as the original.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-008: Implement batch processing for ai analysis (prevent ui freeze)** | [TODO] | [src/modules/neu]
- **SPEC:** Implement `AIBatchProcessor` using Python multiprocessing.Queue. Expose `enqueue_track(path)` and `get_results()`. Ensure model inference runs in a dedicated background worker to prevent UI freezing.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-009: Create "confidence score" filter for ai tags (thresholding)** | [TODO] | [src/modules/neu]
- **SPEC:** Update `MusicTagger` return type to include `confidence`. Add `ThresholdFilter` component that drops tags with `confidence < 0.65`. Expose this threshold via an `AIConfig` dataclass.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-002: Implement "analyze raga" button and result display** | [TODO] | [src/modules/aux]
- **SPEC:** Extend `MetadataTab` UI in `src/modules/aux`. Add a `QPushButton('Analyze Raga')`. Connect it to `AIService.analyze_raga`. Create a `QLabel` to display the top 3 results with progress bar overlays.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-003: Implement "find covers" context menu action in file list** | [TODO] | [src/modules/aux]
- **SPEC:** Modify `ListWidget` context menu in `src/modules/aux`. Add `QAction('Find Covers')`. When triggered, compute embedding via `AIService` and populate a new `CoverResultsDialog` with matches.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-004: Create `modeldownloaddialog` with progress bar for 1gb+ downloads** | [TODO] | [src/modules/aux]
- **SPEC:** Implement `ModelDownloadDialog` extending `QDialog`. Use `QNetworkAccessManager` to stream weights from Hugging Face. Display a `QProgressBar` and chunk download size for 1GB+ models.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-005: Add "ai settings" tab (device selection, model selection)** | [TODO] | [src/modules/aux]
- **SPEC:** Create `AISettingsTab` UI. Add `QComboBox` for Device (CPU/CUDA/MPS) and Model (CLAP/MERT). Bind to `AIConfig` singleton and trigger `ModelLoader.reload()` on apply.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-006: Implement "smart tagging" wizard (auto-apply high confidence tags)** | [TODO] | [src/modules/aux]
- **SPEC:** Implement `SmartTagWizard` in `src/modules/aux`. Sequence: 1. Select tracks. 2. Run batched `MusicTagger`. 3. Present a `QTableWidget` showing proposed tags. 4. Apply via `Mutagen` on confirmation.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-008: Implement "similar tracks" visual graph/list based on embeddings** | [TODO] | [src/modules/aux]
- **SPEC:** Build a graph visualizer using `pyqtgraph`. Plot tracks as nodes based on PCA-reduced MERT embeddings. Implement hover tooltips to show track names and draw edges for similarity > 0.8.

- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PL-008: Add "playlist editor" ui tab (crud operations)** | [TODO] | [src/modules/pl]
- **SPEC:** Create `PlaylistEditorTab` in `src/modules/pl`. Use `QListWidget` for track reordering (drag/drop). Add buttons for Save, Rename, and Export. Connect to `PlaylistService` CRUD endpoints.

- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PERF-002: Refactor `scanner` to use `asyncio` for i/o operations (experiment)** | [TODO] | [src/modules/perf]
- **SPEC:** Rewrite `MusicScanner.scan_directories` using `asyncio.gather`. Implement `aiofiles` for asynchronous OS stat calls and mutagen tag reads to speed up recursive directory traversal.

- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PERF-003: Implement `metadatacache` using `sqlite3` (persistent)** | [TODO] | [src/modules/perf]
- **SPEC:** Replace memory-dict in `MetadataService` with `MetadataCache` using SQLite. Schema: `hash (PRIMARY KEY)`, `json_data`, `last_updated`. Implement a 7-day TTL expiration logic.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-004: Add "plugins" settings tab in ui** | [TODO] | [src/modules/plg]
- **SPEC:** Add a `QTabWidget` panel to Settings named Plugins. Render loaded plugins in a `QTableWidget` with columns: Name, Version, Status. Support enabling/disabling via checkbox items.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-005: Implement `pluginsandbox` restrictions** | [TODO] | [src/modules/plg]
- **SPEC:** Subclass `importlib.abc.MetaPathFinder` to restrict sys.modules loading. Block native OS modules (`os`, `subprocess`, `sys`) from being imported within dynamically loaded plugin namespaces.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-006: Create documentation for plugin api** | [TODO] | [src/modules/plg]
- **SPEC:** Draft `docs/api/plugins.md` detailing `PluginInterface` usage. Include minimum required properties (`name`, `version`, `init()`), event hooking patterns, and provide a full 'Hello World' markdown code block example.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-007: Implement plugin dependency resolver** | [TODO] | [src/modules/plg]
- **SPEC:** Create `DependencyResolver` using topological sort (Kahn's algorithm) to validate plugin dependencies based on `metadata.json` lists. Refuse to initialize if a circular dependency loop is detected.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-008: Add "enable/disable" plugin toggle logic** | [TODO] | [src/modules/plg]
- **SPEC:** Inject a SQLite table `plugin_state` tracking `plugin_id`, `is_active`. Update `PluginLoader` to query this table on app startup before calling `init()` on discovered `.py` modules.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-009: Create `themeplugin` specialization** | [TODO] | [src/modules/plg]
- **SPEC:** Design `ThemePluginInterface` inheriting from base. Force implementation of `get_stylesheet() -> str` and `get_palette() -> dict`. Inject result into global `QApplication.setStyleSheet()`.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-001: Design rest api spec (openapi/swagger)** | [DONE] | [src/modules/api]
- **SPEC:** Write `docs/api/swagger.yaml` containing minimum OpenAPI 3.0 definitions for `/status`, `/library`, and `/scan`. Include JSON schemas for `Track` and `ScanJob` return types.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-002: Implement lightweight flask/fastapi server** | [TODO] | [src/modules/api]
- **SPEC:** Bootstrap `FastAPI` instance in `src/modules/api`. Initialize it within a `uvicorn.run` daemon thread. Create dependency injection hooks connecting FastAPI endpoints to `MusicScanner` singleton.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-003: Implement `get /status` endpoint** | [TODO] | [src/modules/api]
- **SPEC:** Implement `@app.get('/status')` endpoint returning JSON with `uptime`, `version`, `total_tracks`, and `active_workers`. Ensure 200 OK response under 10ms.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-004: Implement `post /scan` endpoint** | [TODO] | [src/modules/api]
- **SPEC:** Implement `@app.post('/scan')` accepting `dir_path`. Trigger `MusicScanner` via signal queue and return a `job_id` 202 Accepted. Ensure the endpoint does not block during scan.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-005: Implement `post /organize` endpoint** | [TODO] | [src/modules/api]
- **SPEC:** Implement `@app.post('/organize')` accepting target payload and metadata. Dispatch to `OrganizationService` asynchronously. Respond with dry-run delta JSON.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-006: Implement `get /library` endpoint (pagination)** | [TODO] | [src/modules/api]
- **SPEC:** Implement `@app.get('/library')` using pagination params (`limit`, `offset`). Query SQLite database for tracks, sort by `added_date`, and return array of serialized track objects.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-007: Implement `get /track/{id}` endpoint** | [TODO] | [src/modules/api]
- **SPEC:** Implement `@app.get('/track/{id}')` pulling full track details including lyrics, cover art blob (Base64), and audio embeddings from `EmbeddingDatabase`.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-008: Add api authentication (basic/token)** | [TODO] | [src/modules/api]
- **SPEC:** Add middleware `AuthMiddleware` to FastAPI. Require an `X-API-Key` header matching a hashed token in SQLite `api_keys` table. Return 401 Unauthorized if invalid.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-009: Create `apiserverthread` for gui integration** | [TODO] | [src/modules/api]
- **SPEC:** Create `QThread` subclass `APIServerThread`. Connect a stop signal to gracefully shutdown `uvicorn`. Connect server logs to emit to `MainWindow` console debug panel.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-010: Add "enable remote api" toggle in settings** | [TODO] | [src/modules/api]
- **SPEC:** Add QCheckBox 'Enable Remote API' to UI Settings. Toggle triggers start/stop of `APIServerThread`. Allow user to configure custom TCP port (default 8000).

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-001: Create mobilesyncservice for local network discovery** | [TODO] | [src/modules/mob]
- **SPEC:** Integrate `zeroconf` to broadcast Auralis service via mDNS `_auralis._tcp.local.`. Enable mobile app discovery of desktop IP address and API port without manual entry.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-002: Implement websocket api for real-time track updates** | [TODO] | [src/modules/mob]
- **SPEC:** Use `websockets` library to spin up WS endpoint at `/ws`. Emit real-time JSON payloads for `play`, `pause`, `seek`, and `track_changed` events.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-003: Add "send to mobile" right-click action in ui** | [TODO] | [src/modules/mob]
- **SPEC:** Extend UI `QMenu`. Add 'Push to Mobile' action. Trigger an HTTP POST to discovered mobile client IP with track raw binary stream over `requests.post()`.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-004: Design offline caching strategy using sqlite** | [TODO] | [src/modules/mob]
- **SPEC:** Build `OfflineCache` singleton on mobile payload. Store down-sampled `.opus` files in local storage mapped via SQLite `mobile_tracks` with eviction LRU strategy.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-005: Create syncsettingstab in preferences** | [TODO] | [src/modules/mob]
- **SPEC:** Implement `SyncSettings` UI to define max cache size (e.g., 5GB), target bitrate for transcode (e.g., 128kbps), and whitelist of synced playlists.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-001: Implement libp2p node initialization logic** | [TODO] | [src/modules/p2p]
- **SPEC:** Initialize `libp2p` node using python-libp2p. Establish a gossipsub router and peer identity matrix. Broadcast local node availability on designated swarm topic.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-002: Create distributed hash table (dht) for track indexing** | [TODO] | [src/modules/p2p]
- **SPEC:** Implement `Kademlia` DHT routing. Hash track titles and insert into DHT providing the multiaddress of the host node possessing the high-res file.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-003: Implement chunked file transfer protocol over mesh** | [TODO] | [src/modules/p2p]
- **SPEC:** Write file transfer handler breaking FLAC files into 256KB chunks. Stream chunks over libp2p `net.stream` validating SHA256 checksums per chunk.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-004: Add "discover network libraries" ui widget** | [TODO] | [src/modules/p2p]
- **SPEC:** Add a new QTreeWidget tab 'Mesh Network'. Query DHT for active peers, populate their shared track counts, and allow users to browse remote folders asynchronously.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-005: Establish network security/encryption layer** | [TODO] | [src/modules/p2p]
- **SPEC:** Enforce Noise protocol handshake for libp2p connections. Generate ed25519 keypairs per node on first boot to guarantee encrypted transport layer.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-001: Integrate local whisper model for stt** | [TODO] | [src/modules/llm]
- **SPEC:** Embed `openai/whisper-tiny` via `ctranslate2` for high-speed local inference. Capture PyAudio microphone stream, chunk into 30s segments, and return transcribed text.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-002: Map natural language intent to playlist filters (sql builder)** | [TODO] | [src/modules/llm]
- **SPEC:** Use `transformers` to run zero-shot classification on transcribed text mapping natural language to predefined SQL schema queries (e.g., 'play upbeat rock' -> `WHERE genre='Rock' AND bpm>120`).

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-003: Add voice capture button to main toolbar** | [TODO] | [src/modules/llm]
- **SPEC:** Render a red pulsing 'Record' QPushButton in the main toolbar. Bind to `pyaudio` stream start/stop and pipe audio buffer to `whisper` model upon release.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-004: Implement conversational feedback using local tts** | [TODO] | [src/modules/llm]
- **SPEC:** Integrate `pyttsx3` or `Coqui TTS` for local voice generation. Synthesize audio confirmations like 'Playing 90s Grunge' and output via `sounddevice`.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-005: Create memory context window for chained queries** | [TODO] | [src/modules/llm]
- **SPEC:** Create a `ChatContext` class holding the last 5 user queries in memory. Allow relative querying (e.g., 'now filter it to just Nirvana' appending to previous SQL tree).

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-001: Integrate openal or equivalent for 3d positioning** | [TODO] | [src/modules/spa]
- **SPEC:** Bridge Python to `pyopenal` library. Initialize ALC device and context. Map stereo audio buffers to 3D Cartesian coordinates `(x, y, z)` around the listener.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-002: Map "mood" metadata to spatial reverb presets** | [TODO] | [src/modules/spa]
- **SPEC:** Create `ReverbMatrix` mapping tags like 'Concert Hall' or 'Ambient' to OpenAL EAX effect presets (decay time, density, diffusion). Apply on track load.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-003: Add spatial audio toggle in playback ui** | [TODO] | [src/modules/spa]
- **SPEC:** Add a QSlider for '3D Depth' and a QCheckBox for 'Enable Spatial' in playback UI. Bind value changes to update OpenAL listener position and source relative coordinates.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-004: Implement head-tracking placeholder logic** | [TODO] | [src/modules/spa]
- **SPEC:** Mock head-tracking input loop reading dummy quaternion values. Interpolate rotation matrix to adjust OpenAL listener orientation vectors dynamically.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-005: Write unit tests for spatial dsp chain** | [TODO] | [src/modules/spa]
- **SPEC:** Write `pytest` suite mocking OpenAL context. Assert that modifying positions triggers the correct AL library C-bindings without crashing the main audio thread.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-001: Create local user authentication schema (sqlite)** | [TODO] | [src/modules/id]
- **SPEC:** Expand base SQLite schema with `users` table (`id`, `username`, `password_hash`, `salt`). Implement `bcrypt` password hashing logic for local auth.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-002: Implement profile switching ui** | [TODO] | [src/modules/id]
- **SPEC:** Implement `LoginDialog` QDialog popping up on app start if multiple profiles exist. Require password validation against `users` table before loading main window.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-003: Segment playlist and history tables by user id** | [TODO] | [src/modules/id]
- **SPEC:** Add `user_id` foreign key to `playlists` and `play_history` tables. Update `PlaylistService` CRUD ops to filter strictly by the currently authenticated user session.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-004: Add personal listening stats aggregation** | [TODO] | [src/modules/id]
- **SPEC:** Build `StatsAggregator` module querying `play_history` by `user_id` to calculate top genres, total listen time, and most played artists per profile.

- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-005: Implement profile export/import (json)** | [TODO] | [src/modules/id]
- **SPEC:** Implement `export_profile` creating a zipped JSON payload of user settings and history. Implement `import_profile` parsing JSON back into SQLite tables avoiding PK collisions.

- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-002: Implement `awsprovider` for s3 backing** | [TODO] | [src/modules/cld]
- **SPEC:** Integrate `boto3`. Implement `AWSProvider` subclassing `CloudProviderInterface`. Handle multipart uploads for large FLAC files using `S3Transfer` manager.

- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-003: Implement `googledriveprovider` for drive backing** | [TODO] | [src/modules/cld]
- **SPEC:** Integrate `google-api-python-client`. Implement `GoogleDriveProvider` handling OAuth2 flow. Implement chunked resumable media uploads to Google Drive.

- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-004: Add cloud settings tab to configure provider** | [TODO] | [src/modules/cld]
- **SPEC:** Design `CloudSettingsTab` UI. Add radio buttons for AWS/Google. Display fields for API Keys / OAuth secrets and a 'Test Connection' button.

- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-005: Create sqlite-based `syncstatetracker`** | [TODO] | [src/modules/cld]
- **SPEC:** Create `sync_state` SQLite table. Track `file_hash`, `remote_id`, `last_sync_timestamp`. Prevent duplicate uploads by querying this state before pushing blobs.

