# Changelog

## [Unreleased]
### Added
- Added comprehensive test suite for `src/utils/audio_utils.py`, specifically targeting `AudioMetadataHandler` and helper functions.

### Fixed
- Fixed bare `except Exception:` blocks across the codebase to adhere to flake8 standards by assigning the exception to a throwaway variable (`except Exception as e: _ = e`). Affected files:
  - `src/services/metadata_sanitizer.py`
  - `src/utils/audio_utils.py`
  - `src/core/scanner.py`
  - `src/gui/wx/main_window.py`
  - `src/gui/wx/tabs/metadata_tab.py`
  - `tests/test_ai_models.py`
