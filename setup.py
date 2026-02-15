#!/usr/bin/env python3
"""
Auralis - Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="auralis",
    version="0.1.0",
    author="PatternSeekers",
    author_email="info@patternseekers.com",
    description="Advanced music file management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/patternseekers/auralis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "auralis=auralis:main",
        ],
    },
    include_package_data=True,
)