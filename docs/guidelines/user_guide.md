# Auralis User Guide

Welcome to Auralis, your advanced music library manager and player. This guide will help you get started with scanning your library, organizing your files, and enhancing your metadata.

## Table of Contents

1.  [Installation](#installation)
2.  [Getting Started](#getting-started)
3.  [Library Scanning](#library-scanning)
4.  [Metadata Enhancement](#metadata-enhancement)
5.  [Organization](#organization)
6.  [Audio Similarity](#audio-similarity)
7.  [Lyrics](#lyrics)
8.  [Configuration](#configuration)

## Installation

### Prerequisites

-   Python 3.8 or higher
-   Audio playback libraries (e.g., ffmpeg for some formats)

### Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/patternseekers/auralis.git
    cd auralis
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    For optional features (Metadata, Audio Analysis):
    ```bash
    pip install -e .[all]
    ```

3.  Run the application:
    ```bash
    python auralis.py
    ```

## Getting Started

When you first launch Auralis, you will see the main dashboard. The interface is divided into tabs for different functions: Scan, Organize, Metadata, and Similarity.

## Library Scanning

To add music to your library:

1.  Navigate to the **Scan** tab.
2.  Click **Select Folder** to choose your music directory.
3.  Click **Start Scan** to index your files.
4.  The application will list all found audio files and their basic metadata.

## Metadata Enhancement

Auralis can automatically fetch metadata from online sources like MusicBrainz, Discogs, Spotify, and Last.fm.

1.  Select files in the library view.
2.  Click **Update Metadata**.
3.  Configure options:
    -   **Force Update**: Overwrite existing tags.
    -   **Fetch Lyrics**: Automatically download lyrics (see [Lyrics](#lyrics)).
4.  Click **Start** to begin fetching.

### Supported Sources

-   **MusicBrainz**: Primary source for accurate release data.
-   **Discogs**: Excellent for electronic and vinyl releases.
-   **Spotify**: Good for popular music.
-   **Last.fm**: Useful for genre tags.

## Organization

Keep your library clean by automatically renaming and moving files.

1.  Go to the **Organize** tab.
2.  Select the source files.
3.  Choose a destination directory.
4.  Select a naming pattern (e.g., `{artist}/{album}/{track} - {title}`).
5.  Click **Organize Files**.

## Audio Similarity

Find duplicate tracks or group similar songs.

1.  Go to the **Similarity** tab.
2.  Select a folder to analyze.
3.  Choose **Find Duplicates** or **Group by Similarity**.
4.  Review the results and manage duplicates.

## Lyrics

Auralis can fetch and embed lyrics into your audio files.

### Providers

-   **Genius**: Large database of lyrics and annotations.
-   **AZLyrics**: Reliable source for pop/rock lyrics.
-   **Tekstowo**: Good for Polish and international hits.

### Saving Lyrics

By default, lyrics are embedded into the audio file metadata (ID3/Vorbis comments).

To save lyrics as a separate `.lrc` file:
-   Enable the **Save LRC File** option in settings or when prompted during metadata updates.

## Configuration

Settings are stored in `~/.auralis/config.json`. You can configure API keys for services like Discogs and Spotify to enable higher rate limits and better results.

### Environment Variables

You can also use a `.env` file for secrets:
-   `SPOTIPY_CLIENT_ID` / `SPOTIPY_CLIENT_SECRET`
-   `LASTFM_API_KEY` / `LASTFM_API_SECRET`
-   `DISCOGS_TOKEN`

## Troubleshooting

### Common Issues

#### 1. "FPcalc not found" Error
If you see errors related to `fpcalc`, it means the acoustid fingerprinting tool is not installed or not in your PATH.
-   **Windows**: Download `fpcalc.exe` from [AcoustID](https://acoustid.org/chromaprint) and place it in the application folder or add its location to your PATH environment variable.
-   **macOS**: Install via Homebrew: `brew install chromaprint`.
-   **Linux**: Install via your package manager: `sudo apt-get install libchromaprint-tools`.

#### 2. Metadata Updates Fail
-   Check your internet connection.
-   Verify API keys if you are using Discogs or Spotify.
-   Ensure files are not read-only.

#### 3. GUI Freezes During Scan
Scanning large libraries can be resource-intensive.
-   Wait for the process to complete; it usually runs in a background thread but might cause UI lag on slower systems.
-   Try scanning smaller sub-folders first.

#### 4. Lyrics Not Found
-   Verify artist and title tags are correct.
-   Try searching manually on Genius or AZLyrics to check spelling.
-   Enable "Fuzzy Matching" in settings (if available) to improve hit rate.

### Reporting Bugs

If you encounter a persistent issue, please open a bug report on GitHub with:
1.  A description of the problem.
2.  Steps to reproduce.
3.  Log output (run with `--debug` flag).
