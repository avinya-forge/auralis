# Auralis Backlog

## High Priority

- [x] Refactor `MetadataService` to use `ThreadPoolExecutor` for better concurrency management.
- [x] Add `AZLyricsProvider` to `LyricsService`.
- [x] Implement LRC (synced lyrics) file saving in `LyricsService`.
- [x] Add comprehensive unit tests for `MetadataService.update_metadata` covering concurrency.
- [x] Add comprehensive unit tests for `LyricsService` including new provider and LRC saving.
- [x] Create `docs/user_guide.md` to document application usage and features.

## Completed

- [x] Refactor `src/gui/ui_factory.py` to support multiple UI backends (PyQt6, wxPython).
- [x] Add unit tests for `src/gui/ui_factory.py`.
- [x] Add unit tests for `src/core/scanner.py` covering core logic.
- [x] Add unit tests for `src/core/organizer.py` covering core logic.
- [x] Add unit tests for `src/services/audio_similarity_service.py`.
- [x] Refactor `src/gui/pyqt/main_window.py` to reduce complexity (C901).
- [x] Refactor `src/services/audio_similarity_service.py` to reduce complexity (C901).
- [x] Refactor `src/services/metadata_service.py` to reduce complexity (C901).
- [x] Refactor `src/utils/audio_utils.py` to reduce complexity.
- [x] Refactor `src/utils/system_utils.py` to reduce complexity.
- [x] Fix all remaining linting issues (flake8) across the codebase.
- [x] Refactor dependency checking logic into `src/utils/dependency_checker.py`.
- [x] Add CLI `check` command to verify system dependencies.
- [x] Implement basic wxPython `MainWindow` skeleton.
- [x] Update README to reflect current status of wxPython support (or implement it).
- [x] Add type hinting to `src/core/` modules.
- [x] Set up CI/CD pipeline (GitHub Actions).
- [x] Implement "Audio Similarity Detection" installation script improvements.
- [x] Add more metadata sources (e.g., Spotify, Last.fm).
- [x] Create a CLI interface for headless operation.
