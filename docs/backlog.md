# Auralis Backlog

## Phase 1: Foundation (Core Compliance)
**Focus:** Establishing the "Iron Triangle" of testing, linting, and complexity management. Ensuring the codebase is robust, type-safe, and fully tested before adding complex features.

### Epic 1: Strict Typing (Codebase-wide)
- [TYP-001] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.core` | [INDEPENDENT] | [DONE]
- [TYP-002] | Resolve type errors in `src/core/scanner.py` | [BLOCKS-TYP-001] | [DONE]
- [TYP-003] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.services` | [INDEPENDENT] | [DONE]
- [TYP-004] | Resolve type errors in `src/services/metadata_service.py` | [BLOCKS-TYP-003] | [DONE]
- [TYP-005] | Resolve type errors in `src/services/lyrics_service.py` | [BLOCKS-TYP-003] | [DONE]
- [TYP-006] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.utils` | [INDEPENDENT] | [DONE]
- [TYP-007] | Resolve type errors in `src/utils/file_utils.py` | [BLOCKS-TYP-006] | [DONE]
- [TYP-008] | Resolve type errors in `src/utils/system_utils.py` | [BLOCKS-TYP-006] | [DONE]
- [TYP-009] | Enable strict typing for `src.gui` (remove ignore) | [INDEPENDENT] | [DONE]
- [TYP-010] | Resolve type errors in `src/gui/wx/main_window.py` | [BLOCKS-TYP-009] | [DONE]
- [TYP-011] | Resolve type errors in `src/gui/wx/tabs/*.py` | [BLOCKS-TYP-009] | [DONE]
- [TYP-012] | Enable strict typing for `src.cli` (remove ignore) | [INDEPENDENT] | [DONE]
- [TYP-013] | Resolve type errors in `src/cli/cli_main.py` | [BLOCKS-TYP-012] | [DONE]

### Epic 2: Test Fortress (95% Coverage)
- [TST-001] | Create `tests/test_cli_main.py` using `unittest.mock` | [INDEPENDENT] | [DONE]
- [TST-002] | Create `tests/test_gui_wx_main_window.py` with mock wx controls | [INDEPENDENT] | [DONE]
- [TST-003] | Create `tests/test_gui_wx_tabs_scan.py` | [INDEPENDENT] | [DONE]
- [TST-004] | Create `tests/test_gui_wx_tabs_organize.py` | [INDEPENDENT] | [DONE]
- [TST-005] | Create `tests/test_gui_wx_tabs_metadata.py` | [INDEPENDENT] | [DONE]
- [TST-006] | Create `tests/test_services_audio_similarity.py` (mock librosa) | [INDEPENDENT] | [DONE]
- [TST-007] | Create `tests/test_services_language_service.py` (mock langdetect) | [INDEPENDENT] | [DONE]
- [TST-008] | Create `tests/test_core_scanner_edge_cases.py` (permission errors, corrupt files) | [INDEPENDENT] | [DONE]
- [TST-009] | Implement `conftest.py` with global mocks for optional deps | [INDEPENDENT] | [DONE]
- [TST-010] | Configure CI to fail if coverage < 95% | [INDEPENDENT] | [TODO]

### Epic 3: Lint Zero & Documentation
- [LNT-001] | Fix all `flake8` warnings in `src/gui` | [INDEPENDENT] | [DONE]
- [LNT-002] | Fix all `flake8` warnings in `src/cli` | [INDEPENDENT] | [DONE]
- [DOC-001] | Add Google-style docstrings to `src/core/scanner.py` | [INDEPENDENT] | [DONE]
- [DOC-002] | Add Google-style docstrings to `src/services/metadata_service.py` | [INDEPENDENT] | [DONE]
- [DOC-003] | Add Google-style docstrings to `src/gui/wx/main_window.py` | [INDEPENDENT] | [DONE]
- [DOC-004] | Update `README.md` with new badge status | [INDEPENDENT] | [TODO]

## Phase 2: Feature Enhancement (Metadata & UI)
**Focus:** Expanding capabilities based on the Vision (Deep Metadata, Fluid UI).

### Epic 4: Advanced Metadata (Deep Dive)
- [MET-001] | Implement `BioProvider` interface in `src/services/bio_service.py` | [INDEPENDENT] | [DONE]
- [MET-002] | Implement `LastFmBioProvider` using `pylast` | [BLOCKS-MET-001] | [DONE]
- [MET-003] | Implement `WikipediaBioProvider` using `beautifulsoup4` | [BLOCKS-MET-001] | [DONE]
- [MET-004] | Integrate Bio Service into `MetadataService` pipeline | [BLOCKS-MET-002, MET-003] | [DONE]
- [MET-005] | Implement `LyricsProvider` interface | [INDEPENDENT] | [DONE]
- [MET-006] | Implement `GeniusLyricsProvider` | [BLOCKS-MET-005] | [DONE]
- [MET-007] | Implement `MusixmatchLyricsProvider` | [BLOCKS-MET-005] | [DONE]
- [MET-008] | Add `AlbumArtFetcher` with size filtering | [INDEPENDENT] | [DONE]
- [MET-009] | Add `GenreClassifier` using `mutagen` basic tags | [INDEPENDENT] | [TODO]
- [MET-010] | Implement `MetadataSanitizer` (remove comments, unknown tags) | [INDEPENDENT] | [TODO]

### Epic 5: UI/UX Refinement
- [UI-001] | Create `ThemeManager` class (Singleton) | [INDEPENDENT] | [TODO]
- [UI-002] | Define JSON Schema for Theme files | [BLOCKS-UI-001] | [TODO]
- [UI-003] | Create `dark_theme.json` | [BLOCKS-UI-002] | [TODO]
- [UI-004] | Create `light_theme.json` | [BLOCKS-UI-002] | [TODO]
- [UI-005] | Implement Theme Switcher in `MainWindow` Menu | [BLOCKS-UI-001] | [TODO]
- [UI-006] | Add "Status Bar" detailed progress indicator | [INDEPENDENT] | [TODO]
- [UI-007] | Implement "Drag and Drop" for folders onto `ScanTab` | [INDEPENDENT] | [TODO]
- [UI-008] | Add "Recent Folders" history to `ScanTab` | [INDEPENDENT] | [TODO]
- [UI-009] | Add "Cover Art Preview" in `MetadataTab` | [INDEPENDENT] | [TODO]
- [UI-010] | Implement "System Tray" icon and minimization | [INDEPENDENT] | [TODO]

### Epic 6: Performance Optimization
- [PERF-001] | Implement `LazyLoader` for album art images | [INDEPENDENT] | [TODO]
- [PERF-002] | Refactor `Scanner` to use `asyncio` for I/O operations | [INDEPENDENT] | [TODO]
- [PERF-003] | Implement `MetadataCache` using `sqlite3` | [INDEPENDENT] | [TODO]
- [PERF-004] | Optimize `LanguageService` initialization (lazy load models) | [INDEPENDENT] | [TODO]
- [PERF-005] | Profile `AudioSimilarityService` and optimize numpy usage | [INDEPENDENT] | [TODO]

## Phase 3: Cognitive Intelligence (The "Neural Network")
**Focus:** Introducing AI/ML capabilities for autonomous organization and smart playback.

### Epic 7: Audio Analysis
- [AUD-001] | Implement `BPMDetector` using `librosa.beat` | [INDEPENDENT] | [TODO]
- [AUD-002] | Implement `KeyDetector` using `librosa.feature.chroma` | [INDEPENDENT] | [TODO]
- [AUD-003] | Implement `MoodAnalyzer` (valence/arousal) skeleton | [INDEPENDENT] | [TODO]
- [AUD-004] | Create `AnalysisTagHandler` to save BPM/Key to ID3 tags | [BLOCKS-AUD-001, AUD-002] | [TODO]
- [AUD-005] | optimize `librosa` imports to prevent startup lag | [INDEPENDENT] | [TODO]
- [AUD-006] | Implement `AudioFingerprinter` using `pyacoustid` | [INDEPENDENT] | [TODO]
- [AUD-007] | Create `DuplicateFinder` based on audio fingerprints | [BLOCKS-AUD-006] | [TODO]
- [AUD-008] | Implement `SilenceTrimmer` utility | [INDEPENDENT] | [TODO]
- [AUD-009] | Add "Loudness Normalization" (ReplayGain) calculator | [INDEPENDENT] | [TODO]
- [AUD-010] | Integrate Analysis results into `MetadataTab` UI | [INDEPENDENT] | [TODO]

### Epic 8: Smart Playlists
- [PL-001] | Create `PlaylistGenerator` service class | [INDEPENDENT] | [TODO]
- [PL-002] | Implement "Generate Upbeat Playlist" (BPM > 120) | [BLOCKS-PL-001] | [TODO]
- [PL-003] | Implement "Generate Chill Playlist" (BPM < 100) | [BLOCKS-PL-001] | [TODO]
- [PL-004] | Implement "Flow Mode" (Match Key + BPM) logic | [BLOCKS-PL-001] | [TODO]
- [PL-005] | Export Playlists to `.m3u8` format | [INDEPENDENT] | [TODO]
- [PL-006] | Import Playlists from `.m3u8` | [INDEPENDENT] | [TODO]
- [PL-007] | Implement "Similar Tracks" finder (Cosine Similarity) | [INDEPENDENT] | [TODO]
- [PL-008] | Add "Playlist Editor" UI Tab | [INDEPENDENT] | [TODO]
- [PL-009] | Implement "History" tracker for generated playlists | [INDEPENDENT] | [TODO]
- [PL-010] | Add "Export to Spotify" (CSV/API) stub | [INDEPENDENT] | [TODO]

## Phase 4: Ecosystem Expansion
**Focus:** Extending Auralis beyond the desktop app.

### Epic 9: Plugin System
- [PLG-001] | Define `PluginInterface` abstract base class | [INDEPENDENT] | [TODO]
- [PLG-002] | Create `PluginLoader` using `importlib` | [BLOCKS-PLG-001] | [TODO]
- [PLG-003] | Implement "Hello World" sample plugin | [BLOCKS-PLG-002] | [TODO]
- [PLG-004] | Add "Plugins" settings tab in UI | [INDEPENDENT] | [TODO]
- [PLG-005] | Implement `PluginSandbox` restrictions | [INDEPENDENT] | [TODO]

### Epic 10: Remote API
- [API-001] | Design REST API spec (OpenAPI/Swagger) | [INDEPENDENT] | [TODO]
- [API-002] | Implement lightweight Flask/FastAPI server | [INDEPENDENT] | [TODO]
- [API-003] | Implement `GET /status` endpoint | [BLOCKS-API-002] | [TODO]
- [API-004] | Implement `POST /scan` endpoint | [BLOCKS-API-002] | [TODO]
- [API-005] | Implement `POST /organize` endpoint | [BLOCKS-API-002] | [TODO]
