import os

from setuptools import find_packages, setup

setup(
    name="auralis",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.0.0",
        "mutagen>=1.45.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "pyacoustid>=1.2.0",
        "discogs-client>=2.3.0",
        "musicbrainzngs>=0.7.0",
        "pillow>=9.0.0",
        "numpy>=1.20.0",
        "psutil>=5.9.0",
        "python-dotenv>=0.19.0",
        "pydub>=0.25.1",
        "tqdm>=4.66.0",
    ],
    extras_require={
        "metadata": [
            "spotipy>=2.19.0",
            "pylast>=4.3.0",
        ],
        "audio": [
            "librosa>=0.9.0",
            "scikit-learn>=1.0.0",
            "soundfile>=0.10.0",
        ],
        "language": [
            "SpeechRecognition>=3.8.0",
            "langdetect>=1.0.9",
        ],
        "ai": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
            "scipy>=1.9.0",
            "librosa>=0.9.0",
        ],
        "all": [
            "spotipy>=2.19.0",
            "pylast>=4.3.0",
            "librosa>=0.9.0",
            "scikit-learn>=1.0.0",
            "soundfile>=0.10.0",
            "SpeechRecognition>=3.8.0",
            "langdetect>=1.0.9",
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
            "scipy>=1.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auralis=auralis:main",
        ],
    },
    author="PatternSeekers",
    description="A modern, intelligent music library organizer",
    long_description=(
        open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else ""
    ),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
)
