# Changelog

## [Unreleased]
### Added
- Added `tests/test_edge_cloud_handoff.py` for edge-cloud integration verification.
- Completed neural modules pattern audit in `docs/audit_report.md`.
- Groomed backlog and added tasks for missing docstrings and CoverSongDetector.
- Added comprehensive test suite for `src/utils/audio_utils.py`, specifically targeting `AudioMetadataHandler` and helper functions.

### Fixed
- Removed duplicate `prune_play_history` call in PyQt main window `closeEvent`.
- Fixed bare `except Exception:` blocks across the codebase to adhere to flake8 standards by assigning the exception to a throwaway variable (`except Exception as e: _ = e`). Affected files:
  - `src/services/metadata_sanitizer.py`
  - `src/utils/audio_utils.py`
  - `src/core/scanner.py`
  - `src/gui/wx/main_window.py`
  - `src/gui/wx/tabs/metadata_tab.py`
  - `tests/test_ai_models.py`
