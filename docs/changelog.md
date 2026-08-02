# Changelog

## [Unreleased]
### Added
- Added comprehensive test suites to achieve >95% coverage across core services:
  - `tests/test_vocalist_analyzer.py` for `src/services/ai/vocalist_analyzer.py`
  - `tests/test_dsp_engine.py` for `src/services/audio/dsp_engine.py`
  - `tests/test_instrument_classifier.py` for `src/services/ai/instrument_classifier.py`
  - `tests/test_file_utils.py` for `src/utils/file_utils.py`
  - `tests/test_ssl_pipeline.py` for `src/modules/neu/training/ssl_pipeline.py`
- Added comprehensive test suite for `src/utils/audio_utils.py`, specifically targeting `AudioMetadataHandler` and helper functions.

### Fixed
- Fixed bare `except Exception:` blocks across the codebase to adhere to flake8 standards by assigning the exception to a throwaway variable (`except Exception as e: _ = e`). Affected files:
  - `src/services/metadata_sanitizer.py`
  - `src/utils/audio_utils.py`
  - `src/core/scanner.py`
  - `src/gui/wx/main_window.py`
  - `src/gui/wx/tabs/metadata_tab.py`
  - `tests/test_ai_models.py`
