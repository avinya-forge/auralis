# Auralis - Advanced Music File Management

Auralis is a powerful cross-platform application for managing music file collections. It offers a 3-stage workflow for scanning, organizing, and enhancing metadata of your music files.

## Features

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

Auralis can be configured using a `.env` file or environment variables. A sample `.env.example` file is provided with all available options.

Key configuration options:

- **UI_FRAMEWORK**: Choose between `pyqt6` and `wxpython`
- **API Keys**: Provide API keys for AcoustID and Discogs
- **File Paths**: Configure default input and output directories
- **Processing Settings**: Adjust thread count and system optimization
- **File Organization**: Configure file organization preferences

## Usage

Run the application:

```
python auralis.py
```

### Optional Features

#### Audio Language Detection

Auralis can automatically detect the spoken language in audio files for more accurate language-based organization:

1. Install additional dependencies:
   ```
   python setup_language_detection.py
   ```

2. Enable the "Use Audio Content for Language Detection" option in Stage 2 (Organize).

#### Lyrics Embedding

Auralis can fetch lyrics for your music and embed them in the audio files:

1. The lyrics feature works out of the box with the standard installation
2. Enable the "Fetch and Embed Lyrics" option in Stage 3 (Metadata)
3. Lyrics will be fetched from online sources and embedded in your audio files
4. Compatible with music players that support lyrics display (Apple Music, iTunes, etc.)

#### Audio Similarity Detection

Auralis can identify duplicate tracks based on their actual audio content, regardless of filenames or metadata:

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

## Troubleshooting

- **Missing Dependencies**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **API Issues**: Verify your API keys are correctly set in the `.env` file
- **Platform-Specific Issues**: Check the logs for detailed error information
- **Audio Similarity Detection**: Run `python setup_audio_similarity.py` to install required libraries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Developed by PatternSeekers 