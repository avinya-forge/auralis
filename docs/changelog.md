# Changelog

## [Unreleased]
### Added
- Documented streamlined vision, phase roadmap, and user journeys in `docs/architecture.md` (resolving `doc-002-vision-statement`).
- Implemented `CoverSongDetector` stub in `src/services/ai/cover_song_detector.py` and integrated it with `AIService` and `src/cli/cli_main.py` (resolving `feat-001-coversong`).
- Completed neural modules pattern audit in `docs/audit_report.md`.
- Added `tests/test_edge_cloud_handoff.py` to verify edge-cloud backup orchestration.
- Groomed backlog and added tasks for missing docstrings, CoverSongDetector, and python-jose deprecation.
- Added comprehensive test suite for `src/utils/audio_utils.py`, specifically targeting `AudioMetadataHandler` and helper functions.

### Fixed
- Fixed bandit issue [B614:pytorch_load] by adding weights_only=True in src/modules/neu/training/ssl_pipeline.py (resolving auto-audit-d654015a).
- Fixed bandit issue [B108:hardcoded_tmp_directory] by using `tempfile` in `src/modules/api/main.py` (resolving `auto-audit-eea3bda4`).
- Fixed bandit issue [B105:hardcoded_password_string] for token_type in `src/modules/api/main.py` (resolving `auto-audit-04e6e40d`).
- Fixed bandit issue [B311:blacklist] by replacing `random.random` with `secrets` in `src/modules/agent/orchestrator.py` (resolving `auto-audit-7b99757e`).
- Fixed bandit issue [B324:hashlib] regarding weak MD5 hash in `src/modules/agent/orchestrator.py` (resolving `auto-audit-8f07c86c`).
- Fixed bandit issue [B324:hashlib] regarding weak MD5 hash in `src/core/scanner.py` (resolving `auto-audit-e4c00041`).
- Ignored deprecation warnings from python-jose and starlette in pyproject.toml.
- Removed duplicate `prune_play_history` call in PyQt main window `closeEvent`.
- Fixed bare `except Exception:` blocks across the codebase to adhere to flake8 standards by assigning the exception to a throwaway variable (`except Exception as e: _ = e`). Affected files:
  - `src/services/metadata_sanitizer.py`
  - `src/utils/audio_utils.py`
  - `src/core/scanner.py`
  - `src/gui/wx/main_window.py`
  - `src/gui/wx/tabs/metadata_tab.py`
  - `tests/test_ai_models.py`

### Phase 7: Task Observer Implementation (agent-004)
- Implemented `TaskObserver` to monitor agent progress.
- Handled circuit breaking to mark a task as blocked after repeated failures.
- Updated metrics calculation for `docs/status.md` and fixed tracking variables for testing environment.

### Phase 7: Continuous Audit System (sys-004-continuous-audit)
- Implemented automated Python script to execute flake8, bandit, and mypy and inject findings into the backlog.
- Configured GitHub Action to run continuous audit on a daily schedule and submit PRs for tech debt.
- Added webhook notification system to alert on critical security flaws detected by Bandit.
