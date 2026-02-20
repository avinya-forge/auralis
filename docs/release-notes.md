# Release Notes

## [Unreleased]

### Planned (Phase 1: Core Stabilization & Compliance)
- Development Infrastructure Setup (flake8, mypy, pytest-cov).
- Test Fortress: Increasing coverage to 95%.
- Type Safety & Code Quality: Strict type hints and docstrings.

### Added
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
