# Auralis Backlog

> **North Star**: Orchestrating Roadmap via Milestone Schema.


## [RESOLVE] Blockers
- **RESOLVE-001**: Ambiguity in Target. Need specific starting task.
- **RESOLVE-002**: Git Sync Blocked. Cannot fetch from remote origin securely due to disabled terminal prompts.


- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PL-008: Add "playlist editor" ui tab (crud operations)** | [DONE] | [src/modules/pl]
- **SPEC:** Create `PlaylistEditorTab` in `src/modules/pl`. Use `QListWidget` for track reordering (drag/drop). Add buttons for Save, Rename, and Export. Connect to `PlaylistService` CRUD endpoints.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PERF-002A: Rewrite `MusicScanner` with `asyncio.gather`** | [DONE] | [src/modules/perf]
- **SPEC:** Rewrite `MusicScanner.scan_directories` using `asyncio.gather` for recursive directory traversal.

> **🎯 EPIC:** PERF-002A | **Target:** src/core/scanner.py | **DoD:** 0 err, >95% cov

> - **[x] TASK:** perf-002a-1-refactor-scan-method | **Loc:** src/core/scanner.py

>   - **Spec:** Convert scan_directories to async, use asyncio.gather for parallel dir traversal | **Deps:** asyncio, os | **Hygiene:** Update error handling

> - **[x] TASK:** perf-002a-2-update-tests | **Loc:** tests/test_scanner.py

>   - **Spec:** Update unit tests to mock and await the new async scan method | **Deps:** pytest.mark.asyncio, unittest.mock | **Hygiene:** Maintain >95% test coverage



  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PERF-002B: Refactor `os.stat` and `mutagen` reads to be asynchronous** | [DONE] | [src/core/scanner.py]
- **SPEC:** Use `asyncio.to_thread` for asynchronous OS stat calls and mutagen tag reads, and process files concurrently using `asyncio.gather` bounded by a semaphore to prevent file limit errors.


> **🎯 EPIC:** PERF-002B | **Target:** src/core/scanner.py | **DoD:** 0 err, >95% cov

> - **[x] TASK:** perf-002b-1-refactor-os-stat | **Loc:** src/core/scanner.py
>   - **Spec:** Refactor `_get_modification_time` and `_extract_file_info` to use `asyncio.to_thread` for non-blocking file stats | **Deps:** asyncio, os | **Hygiene:** Update error handling

> - **[x] TASK:** perf-002b-2-refactor-mutagen-reads | **Loc:** src/core/scanner.py
>   - **Spec:** Refactor `_extract_metadata` to use `asyncio.to_thread` for mutagen tag reads | **Deps:** asyncio, mutagen | **Hygiene:** Update error handling

> - **[x] TASK:** perf-002b-3-update-tests | **Loc:** tests/test_scanner.py
>   - **Spec:** Update unit tests to mock and await the new async methods and mock `os.stat` | **Deps:** pytest.mark.asyncio, unittest.mock.patch | **Hygiene:** Maintain >95% test coverage

  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 2: FEATURE ENHANCEMENT (RESIDUAL DEBT)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PERF-003: Implement `metadatacache` using `sqlite3` (persistent)** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/perf]
- **SPEC:** Replace memory-dict in `MetadataService` with `MetadataCache` using SQLite. Schema: `hash (PRIMARY KEY)`, `json_data`, `last_updated`. Implement a 7-day TTL expiration logic.

> **🎯 EPIC:** PERF-003 | **Target:** src/modules/perf/metadata_cache.py | **DoD:** 0 err, >95% cov

> - **[x] TASK:** perf-003-1-implement-metadata-cache | **Loc:** src/modules/perf/metadata_cache.py
>   - **Spec:** Implement `MetadataCache` using SQLite with a 7-day TTL expiration logic | **Deps:** sqlite3, time, json | **Hygiene:** 100% path coverage | **LOC Estimate:** 50

> - **[x] TASK:** perf-003-2-integrate-metadata-service | **Loc:** src/services/metadata_service.py
>   - **Spec:** Swap `CacheService` with `MetadataCache` in `MetadataService` | **Deps:** None | **Hygiene:** Exception handling for database failures | **LOC Estimate:** 10

> - **[x] TASK:** perf-003-3-write-tests | **Loc:** tests/test_metadata_cache.py
>   - **Spec:** Unit tests for initialization, get, set, and 7-day TTL `clean_expired()` logic | **Deps:** pytest, unittest.mock | **Hygiene:** 100% path coverage | **LOC Estimate:** 50


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-003: Implement `musictagger` (genre/mood/instrument) using clap** | [BLOCKED] | [src/modules/neu]
- **SPEC:** Integrate `laion/clap-htsat-unfused` via Hugging Face Transformers. Create a `MusicTagger` class in `src/modules/neu` that loads the model into CPU/GPU cache and exposes a `tag_audio(file_path)` method returning a dictionary of `genre`, `mood`, and `instrument` scores.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-004: Implement `coversongdetector` using mert embeddings (cosine sim)** | [BLOCKED] | [src/modules/neu]
- **SPEC:** Utilize `m-a-p/MERT-v1-95M` to extract track embeddings. Implement `CoverSongDetector` in `src/modules/neu` to calculate cosine similarity between track vectors. Add a `find_covers(target_embedding)` method.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC NEU-005: Create `embeddingdatabase` (sqlite/json) to store track vectors** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/neu]
- **SPEC:** Build a lightweight SQLite adapter `EmbeddingDatabase` in `src/modules/neu`. The schema must include `track_id (VARCHAR)`, `vector_blob (BLOB)`, and `model_version (VARCHAR)`. Implement `upsert_embedding` and `search_similar`.

> **🎯 EPIC:** NEU-005 | **Target:** src/modules/neu | **DoD:** 0 err, >95% cov

> - **[x] TASK:** neu-005-1-implement-db-schema | **Loc:** src/modules/neu/embedding_database.py
>   - **Spec:** Create `EmbeddingDatabase` with SQLite table `embeddings` (track_id, vector_blob, model_version) | **Deps:** sqlite3 | **Hygiene:** Exception handling | **LOC Estimate:** 40

> - **[x] TASK:** neu-005-2-implement-methods | **Loc:** src/modules/neu/embedding_database.py
>   - **Spec:** Implement `upsert_embedding` and `search_similar` calculating cosine sim using numpy | **Deps:** numpy, sqlite3 | **Hygiene:** Handle empty DB | **LOC Estimate:** 50

> - **[x] TASK:** neu-005-3-write-tests | **Loc:** tests/test_embedding_database.py
>   - **Spec:** Unit tests for insertion and cosine similarity search accuracy | **Deps:** pytest, numpy | **Hygiene:** 100% path coverage | **LOC Estimate:** 50


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-006: Implement `originalversionfinder` logic (release date + similarity)** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/neu]
- **SPEC:** Create `OriginalVersionFinder` in `src/modules/neu`. Logic: query `EmbeddingDatabase` for vectors with >0.9 similarity, then query `MusicBrainz` API for release dates. Return the oldest track as the original.

> **🎯 EPIC:** NEU-006 | **Target:** src/modules/neu/original_version_finder.py | **DoD:** 0 err, >95% cov

> - **[x] TASK:** neu-006-1-implement-logic | **Loc:** src/modules/neu/original_version_finder.py
>   - **Spec:** Implement `OriginalVersionFinder` and `find_original` method | **Deps:** numpy, musicbrainzngs | **Hygiene:** Exception handling | **LOC Estimate:** 50

> - **[x] TASK:** neu-006-2-write-tests | **Loc:** tests/test_original_version_finder.py
>   - **Spec:** Unit tests mocking database and musicbrainzngs API | **Deps:** pytest, unittest.mock | **Hygiene:** 100% path coverage | **LOC Estimate:** 80

  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC NEU-008: Implement batch processing for ai analysis (prevent ui freeze)** | [DONE] | [src/modules/neu]
- **SPEC:** Implement `AIBatchProcessor` using Python multiprocessing.Queue. Expose `enqueue_track(path)` and `get_results()`. Ensure model inference runs in a dedicated background worker to prevent UI freezing.
> **🎯 EPIC:** NEU-008 | **Target:** src/modules/neu | **DoD:** 0 err, >95% cov

> - **[x] TASK:** neu-008-1-implement-processor | **Loc:** src/modules/neu/ai_batch_processor.py
>   - **Spec:** Create `AIBatchProcessor` class with multiprocessing.Queue | **Deps:** multiprocessing | **Hygiene:** Handle errors gracefully | **LOC Estimate:** 50

> - **[x] TASK:** neu-008-2-implement-worker | **Loc:** src/modules/neu/ai_batch_processor.py
>   - **Spec:** Implement worker loop to process tracks | **Deps:** multiprocessing | **Hygiene:** Safe termination | **LOC Estimate:** 40

> - **[x] TASK:** neu-008-3-write-tests | **Loc:** tests/test_ai_batch_processor.py
>   - **Spec:** Write tests for batch processing, enqueuing, and results | **Deps:** pytest | **Hygiene:** 100% path coverage | **LOC Estimate:** 60


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC NEU-009: Create "confidence score" filter for ai tags (thresholding)** | [DONE] | [src/modules/neu]
- **SPEC:** Update `MusicTagger` return type to include `confidence`. Add `ThresholdFilter` component that drops tags with `confidence < 0.65`. Expose this threshold via an `AIConfig` dataclass.
> **🎯 EPIC:** NEU-009 | **Target:** src/modules/neu | **DoD:** 0 err, >95% cov

> - **[x] TASK:** neu-009-1-implement-aiconfig | **Loc:** src/modules/neu/ai_config.py
>   - **Spec:** Create `AIConfig` dataclass with `confidence_threshold` | **Deps:** dataclasses | **Hygiene:** Default to 0.65 | **LOC Estimate:** 20

> - **[x] TASK:** neu-009-2-implement-threshold-filter | **Loc:** src/modules/neu/threshold_filter.py
>   - **Spec:** Create `ThresholdFilter` to drop tags based on confidence | **Deps:** src.modules.neu.ai_config | **Hygiene:** Filter lists correctly | **LOC Estimate:** 30

> - **[x] TASK:** neu-009-3-write-tests | **Loc:** tests/test_threshold_filter.py
>   - **Spec:** Test confidence filtering logic | **Deps:** pytest | **Hygiene:** 100% path coverage | **LOC Estimate:** 40


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC AUX-002: Implement "analyze raga" button and result display** | [DONE] | [src/modules/aux]
- **SPEC:** Extend `MetadataTab` UI in `src/modules/aux`. Add a `QPushButton('Analyze Raga')`. Connect it to `AIService.analyze_raga`. Create a `QLabel` to display the top 3 results with progress bar overlays.

> **🎯 EPIC:** AUX-002 | **Target:** src/modules/aux | **DoD:** 0 err, >95% cov

> - **[x] TASK:** aux-002-1-implement-raga-analyzer-widget | **Loc:** src/modules/aux/raga_analyzer.py
>   - **Spec:** Create `RagaAnalyzerWidget` and `RagaAnalysisWorker` for background raga analysis | **Deps:** PyQt6, src.services.ai_service | **Hygiene:** Exception handling for AI service | **LOC Estimate:** 100

> - **[x] TASK:** aux-002-2-integrate-metadata-tab | **Loc:** src/gui/pyqt/tabs/metadata_tab.py
>   - **Spec:** Import and embed `RagaAnalyzerWidget` into `MetadataTab` | **Deps:** src.modules.aux.raga_analyzer | **Hygiene:** Proper layout insertion | **LOC Estimate:** 15

> - **[x] TASK:** aux-002-3-write-tests | **Loc:** tests/test_aux_raga_analyzer.py
>   - **Spec:** Unit tests mocking `AIService` and PyQt elements | **Deps:** pytest, unittest.mock | **Hygiene:** >95% path coverage | **LOC Estimate:** 80

  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-003: Implement "find covers" context menu action in file list** | [TODO] | [src/modules/aux]
- **SPEC:** Modify `ListWidget` context menu in `src/modules/aux`. Add `QAction('Find Covers')`. When triggered, compute embedding via `AIService` and populate a new `CoverResultsDialog` with matches.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-004: Create `modeldownloaddialog` with progress bar for 1gb+ downloads** | [TODO] | [src/modules/aux]
- **SPEC:** Implement `ModelDownloadDialog` extending `QDialog`. Use `QNetworkAccessManager` to stream weights from Hugging Face. Display a `QProgressBar` and chunk download size for 1GB+ models.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-005: Add "ai settings" tab (device selection, model selection)** | [TODO] | [src/modules/aux]
- **SPEC:** Create `AISettingsTab` UI. Add `QComboBox` for Device (CPU/CUDA/MPS) and Model (CLAP/MERT). Bind to `AIConfig` singleton and trigger `ModelLoader.reload()` on apply.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-006: Implement "smart tagging" wizard (auto-apply high confidence tags)** | [TODO] | [src/modules/aux]
- **SPEC:** Implement `SmartTagWizard` in `src/modules/aux`. Sequence: 1. Select tracks. 2. Run batched `MusicTagger`. 3. Present a `QTableWidget` showing proposed tags. 4. Apply via `Mutagen` on confirmation.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK AUX-008: Implement "similar tracks" visual graph/list based on embeddings** | [BLOCKED] | [src/modules/aux]
- **SPEC:** Build a graph visualizer using `pyqtgraph`. Plot tracks as nodes based on PCA-reduced MERT embeddings. Implement hover tooltips to show track names and draw edges for similarity > 0.8.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-004: Add "plugins" settings tab in ui** | [TODO] | [src/modules/plg]
- **SPEC:** Add a `QTabWidget` panel to Settings named Plugins. Render loaded plugins in a `QTableWidget` with columns: Name, Version, Status. Support enabling/disabling via checkbox items.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC PLG-008: Add "enable/disable" plugin toggle logic** | [DONE] | [HIGH-RISK] | [DEBT] | [src/plugins]
- **SPEC:** Inject a SQLite table `plugin_state` tracking `plugin_id`, `is_active`. Update `PluginLoader` to query this table on app startup before calling `init()` on discovered `.py` modules.
> **🎯 EPIC:** PLG-008 | **Target:** src/plugins | **DoD:** 0 err, >95% cov

> - **[x] TASK:** plg-008-1-implement-plugin-state | **Loc:** src/plugins/plugin_state.py
>   - **Spec:** Create `PluginState` class with SQLite table `plugin_state` | **Deps:** sqlite3 | **Hygiene:** Exception handling | **LOC Estimate:** 50

> - **[x] TASK:** plg-008-2-update-plugin-loader | **Loc:** src/plugins/plugin_loader.py
>   - **Spec:** Query `PluginState` to filter plugins in `PluginLoader` | **Deps:** src.plugins.plugin_state | **Hygiene:** Early return disabled plugins | **LOC Estimate:** 20

> - **[x] TASK:** plg-008-3-write-tests | **Loc:** tests/test_plugin_state.py
>   - **Spec:** Write unit tests for plugin state persistence | **Deps:** pytest | **Hygiene:** 100% test coverage | **LOC Estimate:** 50


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK PLG-009: Create `themeplugin` specialization** | [TODO] | [src/modules/plg]
- **SPEC:** Design `ThemePluginInterface` inheriting from base. Force implementation of `get_stylesheet() -> str` and `get_palette() -> dict`. Inject result into global `QApplication.setStyleSheet()`.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-002: Implement lightweight flask/fastapi server** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Bootstrap `FastAPI` instance in `src/modules/api`. Initialize it within a `uvicorn.run` daemon thread. Create dependency injection hooks connecting FastAPI endpoints to `MusicScanner` singleton.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-003: Implement `get /status` endpoint** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Implement `@app.get('/status')` endpoint returning JSON with `uptime`, `version`, `total_tracks`, and `active_workers`. Ensure 200 OK response under 10ms.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-004: Implement `post /scan` endpoint** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Implement `@app.post('/scan')` accepting `dir_path`. Trigger `MusicScanner` via signal queue and return a `job_id` 202 Accepted. Ensure the endpoint does not block during scan.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-005: Implement `post /organize` endpoint** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Implement `@app.post('/organize')` accepting target payload and metadata. Dispatch to `OrganizationService` asynchronously. Respond with dry-run delta JSON.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-006: Implement `get /library` endpoint (pagination)** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Implement `@app.get('/library')` using pagination params (`limit`, `offset`). Query SQLite database for tracks, sort by `added_date`, and return array of serialized track objects.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-007: Implement `get /track/{id}` endpoint** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Implement `@app.get('/track/{id}')` pulling full track details including lyrics, cover art blob (Base64), and audio embeddings from `EmbeddingDatabase`.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-008: Add api authentication (basic/token)** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Add middleware `AuthMiddleware` to FastAPI. Require an `X-API-Key` header matching a hashed token in SQLite `api_keys` table. Return 401 Unauthorized if invalid.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-009: Create `apiserverthread` for gui integration** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Create `QThread` subclass `APIServerThread`. Connect a stop signal to gracefully shutdown `uvicorn`. Connect server logs to emit to `MainWindow` console debug panel.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK API-010: Add "enable remote api" toggle in settings** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/api]
- **SPEC:** Add QCheckBox 'Enable Remote API' to UI Settings. Toggle triggers start/stop of `APIServerThread`. Allow user to configure custom TCP port (default 8000).


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC MOB-001: Create mobilesyncservice for local network discovery** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/mob]
- **SPEC:** Integrate `zeroconf` to broadcast Auralis service via mDNS `_auralis._tcp.local.`. Enable mobile app discovery of desktop IP address and API port without manual entry.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-002: Implement websocket api for real-time track updates** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/mob]
- **SPEC:** Use `websockets` library to spin up WS endpoint at `/ws`. Emit real-time JSON payloads for `play`, `pause`, `seek`, and `track_changed` events.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-003: Add "send to mobile" right-click action in ui** | [TODO] | [src/modules/mob]
- **SPEC:** Extend UI `QMenu`. Add 'Push to Mobile' action. Trigger an HTTP POST to discovered mobile client IP with track raw binary stream over `requests.post()`.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK MOB-005: Create syncsettingstab in preferences** | [TODO] | [src/modules/mob]
- **SPEC:** Implement `SyncSettings` UI to define max cache size (e.g., 5GB), target bitrate for transcode (e.g., 128kbps), and whitelist of synced playlists.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-001: Implement libp2p node initialization logic** | [BLOCKED] | [src/modules/p2p]
- **SPEC:** Initialize `libp2p` node using python-libp2p. Establish a gossipsub router and peer identity matrix. Broadcast local node availability on designated swarm topic.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-002: Create distributed hash table (dht) for track indexing** | [BLOCKED] | [src/modules/p2p]
- **SPEC:** Implement `Kademlia` DHT routing. Hash track titles and insert into DHT providing the multiaddress of the host node possessing the high-res file.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-003: Implement chunked file transfer protocol over mesh** | [BLOCKED] | [src/modules/p2p]
- **SPEC:** Write file transfer handler breaking FLAC files into 256KB chunks. Stream chunks over libp2p `net.stream` validating SHA256 checksums per chunk.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK P2P-004: Add "discover network libraries" ui widget** | [BLOCKED] | [src/modules/p2p]
- **SPEC:** Add a new QTreeWidget tab 'Mesh Network'. Query DHT for active peers, populate their shared track counts, and allow users to browse remote folders asynchronously.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-001: Integrate local whisper model for stt** | [BLOCKED] | [src/modules/llm]
- **SPEC:** Embed `openai/whisper-tiny` via `ctranslate2` for high-speed local inference. Capture PyAudio microphone stream, chunk into 30s segments, and return transcribed text.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-002A: Implement zero-shot classification on transcribed text** | [BLOCKED] | [src/modules/llm]
- **SPEC:** Use `transformers` to run zero-shot classification on transcribed text for natural language intent.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-002B: Map classified intent to predefined sql schema queries** | [TODO] | [HIGH-RISK] | [DEBT] | [src/modules/llm]
- **SPEC:** Map natural language intent to predefined SQL schema queries (e.g., 'play upbeat rock' -> `WHERE genre='Rock' AND bpm>120`).


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-003: Add voice capture button to main toolbar** | [BLOCKED] | [src/modules/llm]
- **SPEC:** Render a red pulsing 'Record' QPushButton in the main toolbar. Bind to `pyaudio` stream start/stop and pipe audio buffer to `whisper` model upon release.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-004: Implement conversational feedback using local tts** | [BLOCKED] | [src/modules/llm]
- **SPEC:** Integrate `pyttsx3` or `Coqui TTS` for local voice generation. Synthesize audio confirmations like 'Playing 90s Grunge' and output via `sounddevice`.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK LLM-005: Create memory context window for chained queries** | [TODO] | [HIGH-RISK] | [DEBT] | [src/modules/llm]
- **SPEC:** Create a `ChatContext` class holding the last 5 user queries in memory. Allow relative querying (e.g., 'now filter it to just Nirvana' appending to previous SQL tree).


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-001: Integrate openal or equivalent for 3d positioning** | [BLOCKED] | [src/modules/spa]
- **SPEC:** Bridge Python to `pyopenal` library. Initialize ALC device and context. Map stereo audio buffers to 3D Cartesian coordinates `(x, y, z)` around the listener.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-002: Map "mood" metadata to spatial reverb presets** | [BLOCKED] | [src/modules/spa]
- **SPEC:** Create `ReverbMatrix` mapping tags like 'Concert Hall' or 'Ambient' to OpenAL EAX effect presets (decay time, density, diffusion). Apply on track load.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-003: Add spatial audio toggle in playback ui** | [BLOCKED] | [src/modules/spa]
- **SPEC:** Add a QSlider for '3D Depth' and a QCheckBox for 'Enable Spatial' in playback UI. Bind value changes to update OpenAL listener position and source relative coordinates.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-004: Implement head-tracking placeholder logic** | [BLOCKED] | [src/modules/spa]
- **SPEC:** Mock head-tracking input loop reading dummy quaternion values. Interpolate rotation matrix to adjust OpenAL listener orientation vectors dynamically.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK SPA-005: Write unit tests for spatial dsp chain** | [BLOCKED] | [src/modules/spa]
- **SPEC:** Write `pytest` suite mocking OpenAL context. Assert that modifying positions triggers the correct AL library C-bindings without crashing the main audio thread.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-001: Create local user authentication schema (sqlite)** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/id]
- **SPEC:** Expand base SQLite schema with `users` table (`id`, `username`, `password_hash`, `salt`). Implement `bcrypt` password hashing logic for local auth.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-002: Implement profile switching ui** | [BLOCKED] | [src/modules/id]
- **SPEC:** Implement `LoginDialog` QDialog popping up on app start if multiple profiles exist. Require password validation against `users` table before loading main window.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-003: Segment playlist and history tables by user id** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/id]
- **SPEC:** Add `user_id` foreign key to `playlists` and `play_history` tables. Update `PlaylistService` CRUD ops to filter strictly by the currently authenticated user session.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-004: Add personal listening stats aggregation** | [BLOCKED] | [src/modules/id]
- **SPEC:** Build `StatsAggregator` module querying `play_history` by `user_id` to calculate top genres, total listen time, and most played artists per profile.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 4: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK ID-005: Implement profile export/import (json)** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/id]
- **SPEC:** Implement `export_profile` creating a zipped JSON payload of user settings and history. Implement `import_profile` parsing JSON back into SQLite tables avoiding PK collisions.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-002: Implement `awsprovider` for s3 backing** | [BLOCKED] | [src/modules/cld]
- **SPEC:** Integrate `boto3`. Implement `AWSProvider` subclassing `CloudProviderInterface`. Handle multipart uploads for large FLAC files using `S3Transfer` manager.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-003: Implement `googledriveprovider` for drive backing** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/cld]
- **SPEC:** Integrate `google-api-python-client`. Implement `GoogleDriveProvider` handling OAuth2 flow. Implement chunked resumable media uploads to Google Drive.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK CLD-004: Add cloud settings tab to configure provider** | [TODO] | [HIGH-RISK] | [DEBT] | [src/modules/cld]
- **SPEC:** Design `CloudSettingsTab` UI. Add radio buttons for AWS/Google. Display fields for API Keys / OAuth secrets and a 'Test Connection' button.


  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC CLD-005: Create sqlite-based `syncstatetracker`** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/cld]
- **SPEC:** Create `sync_state` SQLite table. Track `file_hash`, `remote_id`, `last_sync_timestamp`. Prevent duplicate uploads by querying this state before pushing blobs.

> **🎯 EPIC:** CLD-005 | **Target:** src/modules/cld | **DoD:** 0 err, >95% cov
>
> - **[x] TASK:** cld-005-1-implement-db-schema | **Loc:** src/modules/cld/sync_state_tracker.py
>   - **Spec:** Create `SyncStateTracker` with SQLite table `sync_state` (`file_hash`, `remote_id`, `last_sync_timestamp`) | **Deps:** sqlite3 | **Hygiene:** Exception handling | **LOC Estimate:** 40
>
> - **[x] TASK:** cld-005-2-implement-methods | **Loc:** src/modules/cld/sync_state_tracker.py
>   - **Spec:** Implement `is_uploaded(file_hash)` and `record_upload(file_hash, remote_id)` | **Deps:** sqlite3 | **Hygiene:** Handle empty DB | **LOC Estimate:** 50
>
> - **[x] TASK:** cld-005-3-write-tests | **Loc:** tests/test_sync_state_tracker.py
>   - **Spec:** Unit tests for initialization, tracking, and duplicate prevention | **Deps:** pytest | **Hygiene:** 100% path coverage | **LOC Estimate:** 50



- **RESOLVE-003**: Implement integration hooks for scripts/run.sh to properly execute --skills endpoint logic from skills.sh.
- **RESOLVE-004**: Audit DB/Auth/API task expansions to ensure SDLC/PDLC mapping strictly implements zero-loss structure.

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-010: Implement `SingerIdentificationService` using wavlm-base-plus-sv** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/neu]
- **SPEC:** Use a Speaker/Singer Identification model (e.g., `microsoft/wavlm-base-plus-sv`) to extract voice embedding of current song. Save it into `EmbeddingDatabase` for DB constraints.
  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]

- **MILESTONE M1** | **PHASE 3: COGNITIVE INTELLIGENCE (NEURAL AUDIO)** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **TASK NEU-011: Implement Live vs. Studio Classification logic** | [BLOCKED] | [src/modules/neu]
- **SPEC:** Train or use a classifier based on `MERT` features to distinguish "Studio Recording" vs "Live Performance" vs "Cover/Acoustic". Expose API and save the classification to tags.
  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]

- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC PLG-001: Implement DependencyResolver via Kahn's Algorithm** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/plg]
- **SPEC:** Implement `DependencyResolver` module. Use Kahn's algorithm topological sort on `metadata.json` dependency dictionaries to compute execution order. Add circular dependency detection preventing initialization.

> **🎯 EPIC:** PLG-001 | **Target:** src/modules/plg | **DoD:** 0 err, >95% cov

> - **[x] TASK:** plg-001-1-parse-metadata | **Loc:** src/modules/plg/dependency_resolver.py
>   - **Spec:** Read and parse metadata.json into a dependency graph dict | **Deps:** json, os | **Hygiene:** Handle missing files | **LOC Estimate:** 30

> - **[x] TASK:** plg-001-2-implement-kahns | **Loc:** src/modules/plg/dependency_resolver.py
>   - **Spec:** Implement Kahn's algorithm for topological sort on the graph | **Deps:** collections.deque | **Hygiene:** O(V+E) time complexity | **LOC Estimate:** 40

> - **[x] TASK:** plg-001-3-circular-detection | **Loc:** src/modules/plg/dependency_resolver.py
>   - **Spec:** Detect circular deps when graph has remaining edges | **Deps:** None | **Hygiene:** [HIGH-RISK] Prevents infinite loops | **LOC Estimate:** 15

> - **[x] TASK:** plg-001-4-write-tests | **Loc:** tests/test_dependency_resolver.py
>   - **Spec:** Unit tests for linear, independent, and circular dependency graphs | **Deps:** pytest | **Hygiene:** 100% path coverage | **LOC Estimate:** 50

- **MILESTONE M1** | **PHASE 6: MOBILE EXTENSIONS** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC MOB-001: Implement OfflineCache SQLite Strategy** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/mob]
- **SPEC:** Build `OfflineCache` class with embedded SQLite database `mobile_tracks`. Enforce LRU eviction policy automatically freeing storage based on user max cache size limits by deleting oldest `.opus` records.
> **🎯 EPIC:** MOB-001 | **Target:** src/modules/mob | **DoD:** 0 err, >95% cov

> - **[x] TASK:** mob-001-1-implement-offline-cache | **Loc:** src/modules/mob/offline_cache.py
>   - **Spec:** Create `OfflineCache` with SQLite table `mobile_tracks` | **Deps:** sqlite3, os | **Hygiene:** Exception handling | **LOC Estimate:** 50

> - **[x] TASK:** mob-001-2-implement-lru | **Loc:** src/modules/mob/offline_cache.py
>   - **Spec:** Implement LRU eviction when limit is reached | **Deps:** sqlite3, os | **Hygiene:** O(1) eviction logic via DB order by | **LOC Estimate:** 30

> - **[x] TASK:** mob-001-3-write-tests | **Loc:** tests/test_mob/test_mob_offline_cache.py
>   - **Spec:** Unit tests for insertion, LRU eviction, and total size tracking | **Deps:** pytest, tempfile | **Hygiene:** 100% path coverage | **LOC Estimate:** 50


- **MILESTONE M1** | **PHASE 5: ECOSYSTEM EXPANSION** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC PLG-002: Implement PluginSandbox using MetaPathFinder** | [DONE] | [HIGH-RISK] | [DEBT] | [src/modules/plg]
- **SPEC:** Build `PluginSandboxFinder` subclassing `importlib.abc.MetaPathFinder`. Prevent `os`, `subprocess`, and `sys` library imports from sandboxed modules inside `src/modules/plg/` by raising `ImportError`.
> **🎯 EPIC:** PLG-002 | **Target:** src/modules/plg | **DoD:** 0 err, >95% cov

> - **[x] TASK:** plg-002-1-implement-sandbox | **Loc:** src/modules/plg/plugin_sandbox.py
>   - **Spec:** Create `PluginSandboxFinder` subclassing `importlib.abc.MetaPathFinder` to intercept banned modules | **Deps:** importlib.abc, inspect, sys | **Hygiene:** Exception handling for ImportError | **LOC Estimate:** 50

> - **[x] TASK:** plg-002-2-implement-tests | **Loc:** tests/test_plugin_sandbox.py
>   - **Spec:** Write unit tests using pytest for import interceptions | **Deps:** pytest, unittest.mock | **Hygiene:** 100% path coverage | **LOC Estimate:** 50

  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]

- **MILESTONE M1** | **PHASE 6: MOBILE EXTENSIONS** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]
- **EPIC NET-001: Implement P2PNetworkSecurity with libp2p and Noise** | [BLOCKED] | [HIGH-RISK] | [DEBT] | [src/modules/net]
- **SPEC:** Implement `P2PNetworkSecurity` module using `libp2p`. Generate `ed25519` keypair on initial boot. Setup `NoiseTransport` for secure handshakes to encrypt `.flac` file chunks over mesh network.

  - **GRANULAR:** [PDLC: Define Requirements] -> [SDLC: Implement Logic] -> [SDLC: Write Tests] -> [PDLC: Review & Release]
