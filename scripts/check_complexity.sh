#!/bin/bash
# scripts/check_complexity.sh
# Audits src/ for Cyclomatic Complexity > 10

set -e

echo "[AUDIT] Checking Cyclomatic Complexity (Threshold > 10)..."
# radon cc -nc src/ lists functions with complexity C or worse (C means >10).
radon cc -nc src/ > radon_output.txt

if [ -s radon_output.txt ]; then
    echo "[WARNING] Found functions with cyclomatic complexity > 10:"
    cat radon_output.txt
    rm radon_output.txt
    exit 1
else
    echo "[AUDIT] All functions have acceptable complexity."
    rm radon_output.txt
    exit 0
fi
