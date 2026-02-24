# Auralis Vision

## North Star
**The Autonomous, High-Fidelity Music Neural Network.**
Auralis is not just a music player; it is an intelligent, self-organizing system that understands your music library at a deep, structural level. It bridges the gap between local high-fidelity archives and the metadata-rich world of streaming, providing a "best of both worlds" experience.

## Pipeline Laws (The "Iron Triangle")
1.  **Test Fortress:** All code (Core, GUI, CLI, Utils) must be covered by tests. Target coverage: 95%. Mocking is mandatory for UI components. No regression is acceptable.
2.  **Lint Zero:** Zero tolerance for linting errors. `flake8` and `mypy` (strict mode, `disallow_untyped_defs = True`, no global ignores) must pass clean.
3.  **Complexity Cap:** No function shall exceed a Cyclomatic Complexity of 10. Refactor ruthlessly.

## Definition of Done (DoD)
A task is only "Done" when it meets the following atomic criteria:
-   [ ] **Tested:** Unit tests added/updated covering happy paths and edge cases.
-   [ ] **Linted:** Passes all static analysis checks.
-   [ ] **Optimized:** O(n) or better complexity verified.
-   [ ] **Secured:** Input sanitized, dependencies checked.
-   [ ] **Documented:** Docstrings and relevant markdown updated.

## Ideal State
-   **Zero-Touch Organization:** Drop a folder of chaotic MP3s, and Auralis sorts, tags, and artworks them instantly.
-   **Neural Audio Understanding:** Identifies Ragas, Cover Songs, and Moods using Zero-Shot Transformers (CLAP/MERT) without relying on external databases.
-   **Universal Playback:** Plays FLAC, MP3, WAV, OGG, and streams seamlessly.
-   **Deep Metadata:** Lyrics, artist bios, and similar tracks are fetched automatically.
-   **Fluid UI:** A responsive, modern interface (PyQt6/wxPython) that feels native on every OS.
