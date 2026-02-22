# Release Notes

## [0.2.0] - Roadmap Reconstruction

### Architectural Pivot
-   **New North Star**: Defined "Autonomous, High-Fidelity Music Neural Network".
-   **Pipeline Laws**: Hardened to "Lint Zero" (Strict Mypy) and "Test Fortress" (95% Global Coverage).
-   **Backlog Expansion**: Constructed 100+ WU roadmap across 4 phases (Foundation, Features, Intelligence, Ecosystem).

### Archived Tasks (Vaulted from Backlog)

#### Phase 1: Core Stabilization & Compliance

##### Epic 1: Development Infrastructure
- [INF-001] | Create `requirements-dev.txt` with dev tools (`pytest`, `flake8`, `mypy`, `black`, `isort`) | [DONE]
- [INF-002] | Configure `flake8` with `.flake8` to match standards | [DONE]
- [INF-003] | Configure `mypy` with `mypy.ini` (strict mode) | [DONE]
- [INF-004] | Add `pytest-cov` and configure `.coveragerc` for coverage reporting | [DONE]
- [INF-005] | Update CI workflow to run linting and type checks | [DONE]

##### Epic 2: Test Fortress (Coverage & Resilience)
- [TST-001] | Create `tests/test_cli_main.py` using `unittest.mock` | [DONE]
- [TST-001] | Add unit tests for `src/utils/config.py` (env loading, defaults) | [DONE]
- [TST-002] | Add unit tests for `src/gui/wx/dialogs/api_keys_dialog.py` | [DONE]
- [TST-003] | Add unit tests for `src/gui/wx/main_window.py` (layout structure verification) | [DONE]
- [TST-004] | Add unit tests for `src/gui/wx/tabs/scan_tab.py` | [DONE]
- [TST-005] | Add unit tests for `src/gui/wx/tabs/organize_tab.py` | [DONE]
- [TST-006] | Add unit tests for `src/gui/wx/tabs/metadata_tab.py` | [DONE]
- [TST-007] | Add mocked tests for `create_env.py` script | [DONE]
- [TST-008] | Add mocked tests for `setup_audio_similarity.py` script | [DONE]
- [TST-009] | Add mocked tests for `setup_language_detection.py` script | [DONE]

##### Epic 3: Type Safety & Code Quality
- [TYP-001] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.core` | [DONE]
- [TYP-002] | Resolve type errors in `src/core/scanner.py` | [DONE]
- [TYP-003] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.services` | [DONE]
- [TYP-004] | Resolve type errors in `src/services/metadata_service.py` | [DONE]
- [TYP-005] | Resolve type errors in `src/services/lyrics_service.py` | [DONE]
- [TYP-006] | Enable `disallow_untyped_defs = True` in `mypy.ini` for `src.utils` | [DONE]
- [TYP-007] | Resolve type errors in `src/utils/file_utils.py` | [DONE]
- [TYP-008] | Resolve type errors in `src/utils/system_utils.py` | [DONE]
- [TYP-009] | Enable strict typing for `src.gui` (remove ignore) | [DONE]
- [TYP-010] | Resolve type errors in `src/gui/wx/main_window.py` | [DONE]
- [TYP-011] | Resolve type errors in `src/gui/wx/tabs/*.py` | [DONE]
- [TYP-012] | Enable strict typing for `src.cli` (remove ignore) | [DONE]
- [TYP-013] | Resolve type errors in `src/cli/cli_main.py` | [DONE]
- [TYP-001-Legacy] | Add strict type hints to `src/utils/config.py` | [DONE]
- [DOC-001] | Add Google-style docstrings to `src/utils/config.py` | [DONE]

### Added (Previous Unreleased Work)
-   Initialized documentation: Vision, Backlog, Standards.
-   Started refactoring for multi-backend UI support.
-   Added unit tests for core components.
-   Refactored `AudioSimilarityService` to reduce complexity and improve maintainability.
-   Verified `MainWindow` code quality.
-   Implemented basic `wxPython` backend skeleton.
-   Refactored `src/utils/audio_utils.py` to use `AudioMetadataHandler` class.
-   Added unit tests for `src/utils/audio_utils.py`.
-   Implemented full `wxPython` GUI tabs (Scan, Organize, Metadata) mirroring PyQt functionality.
-   Enhanced CLI interface for robust headless operation (`scan`, `organize`, `metadata` commands) with progress bars, advanced filtering, and logging control.
-   Improved `setup_audio_similarity.py` script with robust system dependency checks and `--check-only` mode.
-   Added `SpotifySource` and `LastFmSource` for metadata retrieval (requires API keys).
-   Updated documentation for new features and experimental wxPython status.
-   Fixed optional dependency handling in `AudioSimilarityService` to prevent crashes in minimal environments.
-   Refactored dependency checking logic into `src/utils/dependency_checker.py`, creating a unified system for verifying environment health.
-   Added `check` command to the CLI (`auralis.py check`) to diagnose missing dependencies and provide installation instructions.
-   Implemented `AZLyricsProvider` for improved lyrics coverage.
-   Added support for saving synced lyrics (`.lrc`) files.
-   Added `MetadataService` concurrency improvements using `ThreadPoolExecutor` for faster updates.
-   Added comprehensive User Guide (`docs/user_guide.md`).
-   Added unit tests for `LyricsService` (AZLyrics, LRC saving) and `MetadataService` concurrency.
-   **Consolidated Batch Updates:**
    -   Added `requirements-dev.txt`, `.flake8` (strict), `mypy.ini`.
    -   Updated CI pipeline.
    -   Refactored all services and core modules to meet complexity cap < 10.
    -   **Consolidated Batch Updates (Iteration 2):**
        -   Implemented robust unit tests for `src/utils/config.py` including singleton verification and environment loading.
        -   Added strict type hints and Google-style docstrings to `src/utils/config.py`.
        -   Added unit tests for `src/gui/wx/dialogs/api_keys_dialog.py` with full wxPython mocking.
        -   Added unit tests for `src/gui/wx/tabs/scan_tab.py` covering UI interactions and options retrieval.
        -   Added comprehensive unit tests for `src/gui/wx/main_window.py` validating layout and worker thread integration.
    -   **Consolidated Batch Updates (Iteration 3 - Alter-Agent-03):**
        -   Implemented unit tests for `OrganizeTab` (wxPython) with robust mocking of wx controls.
        -   Implemented unit tests for `MetadataTab` (wxPython) covering API key configuration and options.
        -   Added test suite for `create_env.py` script verifying environment setup logic.
        -   Added test suite for setup scripts (`setup_audio_similarity.py`, `setup_language_detection.py`) mocking dependency checks and system interactions.
        -   Consolidated and verified `tests/test_ui_factory.py`, `tests/test_utils.py`, `tests/test_wx_worker.py` ensuring comprehensive coverage.
    -   **Consolidated Batch Updates (Iteration 4 - Unified Typing & CLI Tests):**
        -   **Strict Typing Enforcement (100% Coverage):**
            -   Enabled `disallow_untyped_defs = True` for `src.gui` (PyQt6 & wxPython) and `src.cli`.
            -   Resolved 150+ MyPy errors across `src/gui/pyqt`, `src/gui/wx`, and `src/cli/cli_main.py`.
            -   Added comprehensive type hints to `WorkerThread`, `MainWindow`, and all Tab components.
        -   **Test Fortress Expansion:**
            -   Implemented `tests/test_cli_main.py` covering `scan` and `organize` commands with mocked dependencies (`MusicScanner`, `MusicOrganizer`).
            -   Verified CLI functionality in headless environment via unit tests.

## Iteration: Alter-Agent-03/unified-batch
*   **Consolidated PRs**: Swallowed and verified open work.
*   **Test Fortress**:
    *   Implemented `tests/test_services_language_service.py` (100% coverage).
    *   Implemented `tests/test_core_scanner_edge_cases.py` (Edge cases for scanner).
    *   Verified existing tests for GUI (TST-002, TST-003, TST-004, TST-005) and services (TST-006).
    *   Updated `tests/conftest.py` with global mocks for optional dependencies.
*   **Lint Zero**:
    *   Verified `src/gui` and `src/cli` are flake8 compliant (LNT-001, LNT-002).
*   **Documentation**:
    *   Added Google-style docstrings to `src/core/scanner.py`.
    *   Added Google-style docstrings to `src/services/metadata_service.py`.
    *   Added Google-style docstrings to `src/gui/wx/main_window.py`.

## Iteration: Swift-Executor-01/BioService
*   **Epic 4: Advanced Metadata**:
    *   Implemented `BioService` module (`src/services/bio_service.py`) for artist biography retrieval.
    *   Implemented `BioProvider` interface with `get_bio` method.
    *   Implemented `LastFmBioProvider` using optional `pylast` dependency (MET-002).
    *   Implemented `WikipediaBioProvider` using `beautifulsoup4` and `requests` with fallback logic (MET-003).
    *   Created comprehensive unit tests for `BioService` and its providers (`tests/test_services_bio_service.py`).
    *   Updated `tests/conftest.py` to promote `requests` and `bs4` to core dependencies for testing.

## Iteration: Swift-Executor-03/Metadata-Enhancements
*   **Epic 4: Advanced Metadata (Completed)**
    *   Implemented `MusixmatchLyricsProvider` using web scraping (MET-007).
    *   Integrated `BioService` into `MetadataService` pipeline to fetch and embed artist bios (MET-004).
    *   Implemented `AlbumArtFetcher` with image size filtering and validation (MET-008).
    *   Updated `LyricsService` to include Musixmatch provider.
    *   Verified implementation of `LyricsProvider` interface and `GeniusLyricsProvider` (MET-005, MET-006).
*   **Epic 2: Test Fortress**
    *   Configured CI to enforce test coverage threshold (currently 60%, targeting 95%) (TST-010).
    *   Added comprehensive unit tests for `AlbumArtFetcher` and `MusixmatchLyricsProvider`.
    *   Added integration tests for `MetadataService` bio fetching.

## Iteration: Swift-Executor-01/Theme-And-Sanitization
*   **Epic 4: Advanced Metadata (Completed)**
    *   Implemented `GenreClassifier` (`src/services/genre_service.py`) for managing genre tags (MET-009).
    *   Implemented `MetadataSanitizer` (`src/services/metadata_sanitizer.py`) to clean comments, ID3v1 tags, and whitespace (MET-010).
    *   Added comprehensive unit tests for both services with 100% coverage.
*   **Epic 5: UI/UX Refinement**
    *   Implemented `ThemeManager` (`src/gui/theme_manager.py`) supporting JSON-based themes (UI-001, UI-002).
    *   Created "Dark" and "Light" themes in `resources/themes/` (UI-003, UI-004).
    *   Integrated Theme Switcher into `MainWindow` Menu Bar (UI-005).
    *   Implemented Status Bar with progress tracking, moving it from the side panel (UI-006).
    *   Added `tests/test_gui_pyqt_main_window.py` to verify UI integration.
