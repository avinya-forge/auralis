# Auralis Backlog

## High Priority

- [x] Refactor `src/gui/ui_factory.py` to support multiple UI backends (PyQt6, wxPython).
- [x] Add unit tests for `src/gui/ui_factory.py`.
- [x] Add unit tests for `src/core/scanner.py` covering core logic.
- [x] Add unit tests for `src/core/organizer.py` covering core logic.
- [x] Add unit tests for `src/services/audio_similarity_service.py`.
- [x] Refactor `src/gui/pyqt/main_window.py` to reduce complexity (C901).
- [x] Refactor `src/services/audio_similarity_service.py` to reduce complexity (C901).
- [x] Refactor `src/services/metadata_service.py` to reduce complexity (C901).
- [ ] Refactor `src/utils/audio_utils.py` and `src/utils/system_utils.py` to reduce complexity.
- [ ] Fix all remaining linting issues (flake8) across the codebase.

## Medium Priority

- [ ] Implement basic wxPython `MainWindow` skeleton.
- [ ] Update README to reflect current status of wxPython support (or implement it).
- [ ] Add type hinting to `src/core/` modules.
- [ ] Set up CI/CD pipeline (GitHub Actions).

## Low Priority

- [ ] Implement "Audio Similarity Detection" installation script improvements.
- [ ] Add more metadata sources (e.g., Spotify, Last.fm).
- [ ] Create a CLI interface for headless operation.
