#!/bin/bash
if ! command -v radon &> /dev/null; then pip install radon; fi
radon cc -n C src/ || true
