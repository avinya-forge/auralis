# Release Notes

## [Unreleased]

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
