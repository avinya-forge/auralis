import os

from setuptools import find_packages, setup

setup(
    name="auralis",
    version="0.7.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6==6.10.2",
        "mutagen==1.47.0",
        "requests==2.32.5",
        "beautifulsoup4==4.14.3",
        "lxml==6.0.2",
        "pyacoustid==1.3.0",
        "discogs-client==2.3.0",
        "musicbrainzngs==0.7.1",
        "pillow==12.1.1",
        "numpy==2.4.2",
        "psutil==7.2.2",
        "python-dotenv==1.2.2",
        "pydub==0.25.1",
        "tqdm==4.67.3",
    ],
    extras_require={
        "metadata": [
            "spotipy==2.25.0",
            "pylast==5.3.0",
        ],
        "audio": [
            "librosa==0.11.0",
            "scikit-learn==1.8.0",
            "soundfile==0.13.1",
        ],
        "language": [
            "SpeechRecognition==3.14.5",
            "langdetect==1.0.9",
        ],
        "ai": [
            "transformers==4.49.0",
            "torch==2.6.0",
            "torchaudio==2.6.0",
            "scipy==1.15.2",
            "librosa==0.11.0",
        ],
        "all": [
            "spotipy==2.25.0",
            "pylast==5.3.0",
            "librosa==0.11.0",
            "scikit-learn==1.8.0",
            "soundfile==0.13.1",
            "SpeechRecognition==3.14.5",
            "langdetect==1.0.9",
            "transformers==4.49.0",
            "torch==2.6.0",
            "torchaudio==2.6.0",
            "scipy==1.15.2",
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
