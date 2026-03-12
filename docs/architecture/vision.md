# Auralis Vision

## North Star
- **The Autonomous, High-Fidelity Music Neural Network.**
- Intelligent, self-organizing system.
- Bridges the gap between local high-fidelity archives and the metadata-rich world of streaming.

## Pipeline Laws (The "Iron Triangle")
- **Test Fortress:** All code (Core, GUI, CLI, Utils) must be covered by tests. Target coverage: 95%. Mocking is mandatory for UI components. No regression is acceptable.
- **Lint Zero:** Zero tolerance for linting errors. `flake8` and `mypy` (strict mode, `disallow_untyped_defs = True`, no global ignores) must pass clean.
- **Complexity Cap:** No function shall exceed a Cyclomatic Complexity of 10. Refactor ruthlessly.
- **Latest Stable Env Only:** Always use the latest stable environment and dependencies unless strictly impossible.

## Definition of Done (DoD)
- [ ] **Tested:** Unit tests added/updated covering happy paths and edge cases.
- [ ] **Linted:** Passes all static analysis checks.
- [ ] **Optimized:** O(n) or better complexity verified.
- [ ] **Secured:** Input sanitized, dependencies checked.
- [ ] **Documented:** Docstrings and relevant markdown updated.

## Ideal State
- **Zero-Touch Organization:** Instant sorting, tagging, and artwork integration.
- **Neural Audio Understanding:** Identifies Ragas, Cover Songs, and Moods using Zero-Shot Transformers (CLAP/MERT).
- **Universal Playback:** FLAC, MP3, WAV, OGG, and streams.
- **Deep Metadata:** Lyrics, artist bios, and similar tracks.
- **Fluid UI:** Responsive, modern interface (PyQt6/wxPython).

## Phase 5 Expansion Laws
- **Modularity First:** All new ecosystem features must be built as optional modules.
- **Performance Budget:** Background services (Sync, DJ Tools, AI) must not degrade main UI thread responsiveness.
- **Offline Fallback:** Cloud and Social features must fail gracefully without internet.
