# Auralis Backlog

## Phase 1: Core Stabilization & Compliance
**Focus:** Establishing the "Iron Triangle" of testing, linting, and complexity management. Bringing the existing codebase up to the new "Pipeline Laws".

### Epic 1: Development Infrastructure
- [INF-001] | Create `requirements-dev.txt` with dev tools (`pytest`, `flake8`, `mypy`, `black`, `isort`) | [BLOCKS-INF-002, INF-003, INF-004] | [TODO]
- [INF-002] | Configure `flake8` with `.flake8` to match standards | [BLOCKS-INF-005] | [TODO]
- [INF-003] | Configure `mypy` with `mypy.ini` (strict mode) | [BLOCKS-INF-005] | [TODO]
- [INF-004] | Add `pytest-cov` and configure `.coveragerc` for coverage reporting | [INDEPENDENT] | [TODO]
- [INF-005] | Update CI workflow to run linting and type checks | [INDEPENDENT] | [TODO]

### Epic 2: Test Fortress (Coverage & Resilience)
- [TST-001] | Add unit tests for `src/utils/config.py` (env loading, defaults) | [INDEPENDENT] | [TODO]
- [TST-002] | Add unit tests for `src/gui/wx/dialogs/api_keys_dialog.py` | [INDEPENDENT] | [TODO]
- [TST-003] | Add unit tests for `src/gui/wx/main_window.py` (layout structure verification) | [INDEPENDENT] | [TODO]
- [TST-004] | Add unit tests for `src/gui/wx/tabs/scan_tab.py` | [INDEPENDENT] | [TODO]
- [TST-005] | Add unit tests for `src/gui/wx/tabs/organize_tab.py` | [INDEPENDENT] | [TODO]
- [TST-006] | Add unit tests for `src/gui/wx/tabs/metadata_tab.py` | [INDEPENDENT] | [TODO]
- [TST-007] | Add mocked tests for `create_env.py` script | [INDEPENDENT] | [TODO]
- [TST-008] | Add mocked tests for `setup_audio_similarity.py` script | [INDEPENDENT] | [TODO]
- [TST-009] | Add mocked tests for `setup_language_detection.py` script | [INDEPENDENT] | [TODO]
- [TST-010] | Verify and enhance `src/core/scanner.py` tests for error handling edge cases | [INDEPENDENT] | [TODO]

### Epic 3: Type Safety & Code Quality
- [TYP-001] | Add strict type hints to `src/utils/config.py` | [INDEPENDENT] | [TODO]
- [TYP-002] | Add strict type hints to `src/utils/file_utils.py` | [INDEPENDENT] | [TODO]
- [TYP-003] | Add strict type hints to `src/utils/system_utils.py` | [INDEPENDENT] | [TODO]
- [TYP-004] | Add strict type hints to `src/services/lyrics_service.py` | [INDEPENDENT] | [TODO]
- [TYP-005] | Add strict type hints to `src/services/metadata_service.py` | [INDEPENDENT] | [TODO]
- [DOC-001] | Add Google-style docstrings to `src/utils/config.py` | [INDEPENDENT] | [TODO]
- [DOC-002] | Add Google-style docstrings to `src/utils/file_utils.py` | [INDEPENDENT] | [TODO]
- [DOC-003] | Add Google-style docstrings to `src/services/lyrics_service.py` | [INDEPENDENT] | [TODO]

## Phase 2: Feature Enhancement
**Focus:** Expanding capabilities based on the Vision (Deep Metadata, Fluid UI).

### Epic 4: Advanced Metadata
- [MET-001] | Create `BioProvider` interface in `src/services/bio_service.py` | [BLOCKS-MET-002, MET-003, MET-004] | [TODO]
- [MET-002] | Implement `LastFmBioProvider` using `pylast` | [INDEPENDENT] | [TODO]
- [MET-003] | Implement `WikipediaBioProvider` (skeleton) using `beautifulsoup4` | [INDEPENDENT] | [TODO]
- [MET-004] | Integrate Bio Service into `MetadataService` pipeline | [INDEPENDENT] | [TODO]

### Epic 5: UI/UX Refinement
- [UI-001] | Implement `ThemeManager` class for PyQt6 styles | [BLOCKS-UI-002, UI-003] | [TODO]
- [UI-002] | Create Dark Theme JSON configuration file | [INDEPENDENT] | [TODO]
- [UI-003] | Apply `ThemeManager` to `MainWindow` (PyQt6) | [INDEPENDENT] | [TODO]
- [UI-004] | Implement Status Bar detailed messages in wxPython backend | [INDEPENDENT] | [TODO]
- [UI-005] | Add "Check for Updates" menu item placeholder in both UIs | [INDEPENDENT] | [TODO]

### Epic 6: Performance Optimization
- [PERF-001] | Profile `Scanner.scan_folder` with `cProfile` to identify bottlenecks | [BLOCKS-PERF-002] | [TODO]
- [PERF-002] | Optimize `MetadataService.batch_update` for large libraries (>10k tracks) | [INDEPENDENT] | [TODO]
- [PERF-003] | Implement lazy loading for artwork in `MainWindow` (PyQt6) | [INDEPENDENT] | [TODO]

### Epic 7: Security Hardening
- [SEC-001] | Audit dependencies for known vulnerabilities using `safety` or `pip-audit` | [BLOCKS-SEC-002] | [TODO]
- [SEC-002] | Implement input sanitization for all metadata fields in `MetadataService` | [INDEPENDENT] | [TODO]
- [SEC-003] | Verify SSL certificate validation in all `requests` calls | [INDEPENDENT] | [TODO]
