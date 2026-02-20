# Release Notes

## [Unreleased]

### Planned (Phase 1: Core Stabilization & Compliance)
- Development Infrastructure Setup (flake8, mypy, pytest-cov).
- Test Fortress: Increasing coverage to 95%.
- Type Safety & Code Quality: Strict type hints and docstrings.

## [0.1.0] - 2024-05-23

### Added
-   Initialized documentation: Vision, Backlog, Standards.
-   Refactored `src/gui/ui_factory.py` to support multiple UI backends (PyQt6, wxPython).
-   Implemented basic `wxPython` backend skeleton and full GUI tabs.
-   Refactored `src/utils/audio_utils.py` to use `AudioMetadataHandler` class.
-   Enhanced CLI interface for robust headless operation (`scan`, `organize`, `metadata`, `check`).
-   Improved `setup_audio_similarity.py` script with robust system dependency checks.
-   Added `SpotifySource` and `LastFmSource` for metadata retrieval.
-   Fixed optional dependency handling in `AudioSimilarityService`.
-   Refactored dependency checking logic into `src/utils/dependency_checker.py`.
-   Implemented `AZLyricsProvider` for improved lyrics coverage and LRC saving.
-   Added `MetadataService` concurrency improvements using `ThreadPoolExecutor`.
-   Added comprehensive User Guide (`docs/user_guide.md`).
-   Added unit tests for core components, services, and utils.
