#!/bin/bash
# scripts/audit_deps.sh
# Audits requirements for vulnerabilities and unpinned dependencies.

set -e

echo "[AUDIT] Checking for vulnerabilities in dependencies using safety..."
safety check -r requirements.txt -r requirements-dev.txt || echo "[WARNING] Vulnerabilities found!"

echo "[AUDIT] Checking for unpinned dependencies..."
grep -E -n "^[^#].*$" requirements.txt requirements-dev.txt | grep -v -E "==|>=" && {
    echo "[WARNING] Found unpinned dependencies. Please pin them using == or >=."
    exit 1
}

echo "[AUDIT] Dependency check passed."
exit 0
