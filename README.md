# Auralis

**The Autonomous, High-Fidelity Music Neural Network.**

![CI](https://github.com/patternseekers/auralis/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Version](https://img.shields.io/badge/version-v0.8.1-blue)

## Project Pulse

| Milestone | Version | Phase | Status | Tech Debt | Backlog Density |
|---|---|---|---|---|---|
| M1 | 0.8.1 | Phase 6: Everything-Stream Engine | [READY] | 0% | 462/60 |

## Documentation Map

- [Backlog](./docs/backlog.md)
- [Release Notes](./docs/release-notes.md)
- [Vision](./docs/vision.md)
- [Habits](./docs/rules/habits.md)
- [Hygiene](./docs/rules/hygiene.md)
- [Ultra Lean Standards](./docs/standards/ultra-lean.md)

## Quick Start

**Active Milestone:** Phase 6: Everything-Stream Engine
Integrating Multi-Tier Audio Comparison, Security Scrutiny, and UI Control.

## System Architecture

```mermaid
graph TD
    A[Raw Music Files] --> B(Scan & Rename)
    B --> C(Organize & Deduplicate)
    C --> D(Metadata Enhancement)
    D --> E[Structured Library]

    subgraph Intelligence Layer
        F[Neural Audio]
        G[Lyrics Embedding]
        H[Language Detection]
    end

    D -.-> Intelligence Layer
```

## Core Specifications

- **Cross-Platform**: Windows, macOS, and Linux support.
- **Multiple UI Frameworks**: PyQt6 (default) and wxPython (experimental).
- **3-Stage Workflow**: Scan & Rename, Organize, Metadata Enhancement.
- **API Integration**: AcoustID, MusicBrainz, Discogs, Spotify, Last.fm.
- **Intelligence Layer**: Language Detection, Lyrics Embedding, Audio Similarity, Neural Audio Tagging.
