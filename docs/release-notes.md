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
-   Added CLI interface for headless operation (`scan`, `organize`, `metadata` commands).
-   Improved `setup_audio_similarity.py` script with system dependency checks.
