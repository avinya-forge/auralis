#!/bin/bash
if ! command -v safety &> /dev/null; then pip install safety; fi
safety check -r requirements.txt || true
