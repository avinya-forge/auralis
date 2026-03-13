# Auralis - Advanced Music File Management

> **"The Autonomous, High-Fidelity Music Neural Network."**
> Auralis organizes, enhances, and secures your music library with neural intelligence and spatial awareness.

---

## 🚀 The Hook: Quick Start

**Experience the future of audio management.**

### Local Launch
```bash
git clone https://github.com/patternseekers/auralis.git
cd auralis
pip install -r requirements.txt

# Start Auralis CLI / GUI environment
bash scripts/run.sh --start
```

### Automation & Sync
Execute tests, audits, and dynamic updates idempotently via `scripts/run.sh`:
- `bash scripts/run.sh --test` (Lint/Coverage/Unit)
- `bash scripts/run.sh --backlog` (Audit SDLC+PDLC tasks)
- `bash scripts/run.sh --sync` (Idempotent file-tree alignment)
- `bash scripts/run.sh --skills` (Self-update using skills.sh)

---

## ⚡ The Engine: Pulse Table

| Milestone | Version | Phase | Status | Debt% |
|---|---|---|---|---|
| M1 | 0.9.0 | Phase 4: Ecosystem Expansion | Active | 0% |

---

## 🗺️ The Map: Visual SSOT Index

**Plan**: [Backlog](./docs/planning/backlog.md) | [Roadmap](./docs/planning/roadmap.md) | [Map](./docs/planning/map.md) | [Doubts](./docs/planning/doubts.md) | [Conflict Map](./docs/planning/conflict-map.md)
**Architecture**: [Arch](./docs/architecture/arch.md) | [System Design](./docs/architecture/system-design.md) | [Vision](./docs/architecture/vision.md) | [Decisions](./docs/architecture/decisions.md) | [Network Security](./docs/architecture/network-security.md) | [Offline Caching](./docs/architecture/offline-caching-strategy.md) | [Plugin Sandbox](./docs/architecture/plugin-sandbox.md) | [Plugin Resolver](./docs/architecture/plugin-dependency-resolver.md) | [Swagger](./docs/architecture/swagger.yaml)
**Rules**: [Standards](./docs/rules/standards.md) | [Habits](./docs/rules/habits.md) | [Hygiene](./docs/rules/hygiene.md) | [Process Flow](./docs/rules/process-flow.md)
**Engineering**: [Index](./docs/engineering/index.md) | [Conventions](./docs/engineering/conventions.md)
**Release**: [Release Notes](./docs/release/release-notes.md) | [Metrics](./docs/release/metrics.md) | [Project Health](./docs/release/project-health.md) | [System Health](./docs/release/system-health.md)

---

## 🏛️ System Architecture

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

---

## Legacy Documentation (0-Loss Audit)

# Auralis - Advanced Music File Management

![CI](https://github.com/patternseekers/auralis/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

## North Star
**The Autonomous, High-Fidelity Music Neural Network.**

## Pulse Table
| Milestone | Version | Phase | Status | Debt% | Density |
|---|---|---|---|---|---|
| M1 | 0.9.0 | Phase 4: Ecosystem Expansion | Active | 0% | 60 Tasks |

## IO_SSOT Index
- **Plan**:
  - [Backlog](./docs/planning/backlog.md)
  - [Map](./docs/planning/map.md)
  - [Doubts](./docs/planning/doubts.md)
  - [Conflict Map](./docs/planning/conflict-map.md)
- **Architecture**:
  - [Architecture](./docs/architecture/arch.md)
  - [Vision](./docs/architecture/vision.md)
  - [Decisions](./docs/architecture/decisions.md)
  - [Network Security](./docs/architecture/network-security.md)
  - [Offline Caching Strategy](./docs/architecture/offline-caching-strategy.md)
  - [Plugin Sandbox](./docs/architecture/plugin-sandbox.md)
  - [Plugin Dependency Resolver](./docs/architecture/plugin-dependency-resolver.md)
  - [Swagger API Specs](./docs/architecture/swagger.yaml)
- **Rules**:
  - [Standards](./docs/rules/standards.md)
  - [Habits](./docs/rules/habits.md)
  - [Hygiene](./docs/rules/hygiene.md)
  - [Process Flow](./docs/rules/process-flow.md)
- **Release**:
  - [Release Notes](./docs/release/release-notes.md)
  - [Metrics](./docs/release/metrics.md)
  - [Project Health](./docs/release/project-health.md)
  - [System Health](./docs/release/system-health.md)

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

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Multiple UI Frameworks**: Supports both PyQt6 and wxPython
- **3-Stage Workflow**:
  1. **Scan & Rename**: Scans directories for music files and renames them based on metadata
  2. **Organize**: Moves files to a new directory structure based on metadata
  3. **Metadata Enhancement**: Retrieves additional metadata from online sources
- **Advanced UI**: Detailed file table with customizable columns, file information panel, and progress tracking
- **API Integration**: Integrates with AcoustID/MusicBrainz and Discogs for enhanced metadata
- **Robust Configuration**: Loads settings from environment variables or config file
- **Audio Language Detection**: Automatically detects the spoken language in audio files for better organization
- **Lyrics Embedding**: Fetches lyrics from online sources and embeds them in audio files for display in music players
- **Audio Similarity Detection**: Identifies duplicate tracks based on actual audio content, regardless of filenames or metadata
- **Audio Analysis**: Automatically detects BPM (Beats Per Minute) and Musical Key using advanced audio signal processing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/patternseekers/auralis.git
   cd auralis
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   ```
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file with your API keys and preferences
   ```

## Configuration

- Configure using `.env` file or environment variables.
- Sample `.env.example` provided.

**Key Options:**

- **UI_FRAMEWORK**: Choose between `pyqt6` (default) and `wxpython` (experimental).
  - Note: For `wxpython`, you must install it manually: `pip install wxPython`.
- **API Keys**: Provide API keys for AcoustID, Discogs, Spotify, and Last.fm
- **File Paths**: Configure default input and output directories
- **Processing Settings**: Adjust thread count and system optimization
- **File Organization**: Configure file organization preferences

## Usage

### GUI Mode

Run the application with the default GUI:

```
python auralis.py
```

### CLI Mode

- Provides command-line interface for headless operation.

```bash
# Scan directories
python auralis.py scan /path/to/music --output-json results.json

# Organize files
python auralis.py organize results.json /path/to/destination

# Update metadata
python auralis.py metadata results.json --lyrics
```

Use `python auralis.py --help` for detailed command information.

### Optional Features

#### Audio Language Detection

- Automatically detects spoken language in audio files for precise organization.

1. Install additional dependencies:
   ```
   python setup_language_detection.py
   ```

2. Enable the "Use Audio Content for Language Detection" option in Stage 2 (Organize).

#### Lyrics Embedding

- Fetches and embeds lyrics directly into audio files.

1. The lyrics feature works out of the box with the standard installation
2. Enable the "Fetch and Embed Lyrics" option in Stage 3 (Metadata)
3. Lyrics will be fetched from online sources and embedded in your audio files
4. Compatible with music players that support lyrics display (Apple Music, iTunes, etc.)

#### Audio Similarity Detection

- Identifies duplicates via audio fingerprinting, bypassing metadata or filename inconsistencies.

1. Install additional dependencies:
   ```
   python setup_audio_similarity.py
   ```

2. Enable the "Detect Similar Audio Content" option in Stage 2 (Organize)
3. The system will analyze audio fingerprints to find duplicate tracks
4. By default, only the highest quality version of each duplicate will be kept
5. Quality is determined by audio format, bitrate, file size, and metadata completeness

### Workflow

1. **Stage 1: Scan & Rename**
   - Add source directories containing music files
   - Configure file extensions and scan depth
   - Optionally rename files based on metadata

2. **Stage 2: Organize**
   - Set a destination directory for organized files
   - Configure organization options (by language, handle duplicates, etc.)
   - Enable audio language detection for more accurate organization
   - Enable audio similarity detection to find duplicates based on content
   - Run a dry run to preview changes before applying them

3. **Stage 3: Metadata Enhancement**
   - Configure online sources (MusicBrainz, Discogs)
   - Enable lyrics fetching to embed lyrics in your audio files
   - Update metadata from online sources
   - Save enhanced metadata to files

## API Registration

### AcoustID

1. Register at [AcoustID](https://acoustid.org/login)
2. Request an API key
3. Add the key to your `.env` file

### Discogs

1. Create an account at [Discogs](https://www.discogs.com/)
2. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
3. Create a new application to get API credentials
4. Add the credentials to your `.env` file

### Spotify (Optional)

1. Create an app at [Spotify for Developers](https://developer.spotify.com/dashboard)
2. Get your `Client ID` and `Client Secret`
3. Add `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` to your `.env` file
4. Install dependency: `pip install spotipy`

### Last.fm (Optional)

1. Get an API account at [Last.fm API](https://www.last.fm/api/account/create)
2. Get your `API Key` and `Shared Secret`
3. Add `LASTFM_API_KEY` and `LASTFM_API_SECRET` to your `.env` file
4. Install dependency: `pip install pylast`

## Troubleshooting

- **Missing Dependencies**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **API Issues**: Verify your API keys are correctly set in the `.env` file
- **Platform-Specific Issues**: Check the logs for detailed error information
- **Audio Similarity Detection**: Run `python setup_audio_similarity.py` to install required libraries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Developed by PatternSeekers
