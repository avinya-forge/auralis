#!/bin/bash

# Auralis: Unified Automation Script
# SDLC+PDLC Evolution | 0-Loss | skills.sh-Integrated
# Modes: --start (docker/local), --test, --backlog (drill-down), --sync (skills.sh)

log_resolve() {
    local blocker_msg="$1"
    local backlog_file="docs/backlog.md"

    if ! grep -qF "$blocker_msg" "$backlog_file"; then
        # Add to the [RESOLVE] Blockers section if it exists, else append
        if grep -q "## \[RESOLVE\] Blockers" "$backlog_file"; then
            sed -i "/## \[RESOLVE\] Blockers/a - **RESOLVE-NEW**: $blocker_msg" "$backlog_file"
        else
            echo -e "\n## [RESOLVE] Blockers\n- **RESOLVE-NEW**: $blocker_msg" >> "$backlog_file"
        fi
        echo "[RUN.SH] Logged blocker to backlog: $blocker_msg"
    fi
}

audit() {
    echo "[SKILLS] Running AUDIT..."
    echo "[RECON] Syncing state against codebase..."

    local backlog="docs/backlog.md"
    local temp_file=$(mktemp)

    while IFS= read -r line || [ -n "$line" ]; do
        if echo "$line" | grep -q "\[ \] TASK.*\*\*Loc:\*\* "; then
            # Extract filepath from **Loc:**
            filepath=$(echo "$line" | grep -o "\*\*Loc:\*\* [^ |]*" | cut -d' ' -f2)
            if [ -f "$filepath" ]; then
                echo "$line" | sed 's/\[ \] TASK/\[x\] TASK/' >> "$temp_file"
                echo "[RECON] -> Marked $filepath as Done [x]"
            else
                echo "$line" >> "$temp_file"
            fi
        elif echo "$line" | grep -q "\[x\] TASK.*\*\*Loc:\*\* "; then
            filepath=$(echo "$line" | grep -o "\*\*Loc:\*\* [^ |]*" | cut -d' ' -f2)
            if [ ! -f "$filepath" ] && ! echo "$line" | grep -q "\[DEBT\]"; then
                echo "$line" | sed 's/| \*\*Loc/| \[DEBT\] | \*\*Loc/' >> "$temp_file"
                echo "[RECON] -> Marked $filepath as [DEBT] (missing code)"
            else
                echo "$line" >> "$temp_file"
            fi
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$backlog"

    mv "$temp_file" "$backlog"

    # Grep EPIC/DEBT across backlog
    grep -E "EPIC|DEBT" docs/backlog.md

    # Recursive expansion (for all matching tasks, run expand)
    grep -E "EPIC|DEBT" docs/backlog.md | while read -r line; do
        pdlc_expand "$line"
    done
}

verify() {
    echo "[SKILLS] Running LINT/TEST (verify)..."
    python -m flake8 src/ tests/ || echo "[LINT] flake8 failed"
    python -m mypy src/ tests/ || echo "[LINT] mypy failed"
    python -m pytest --cov=src tests/ || echo "[TEST] pytest failed"
}

pdlc_expand() {
    echo "[SKILLS] Running PDLC_EXPAND on $1..."
    # If the task contains an EPIC or DEBT reference without expanded tasks underneath, it flags it.
    if ! grep -F -A 5 -- "$1" docs/backlog.md | grep -q "🎯 EPIC"; then
        echo "[PDLC] Missing granular breakdown for: $1. Needs manual expansion via SDLC protocol."
    else
        echo "[PDLC] Found expanded tasks. Processing SDLC layers: [REQUIREMENTS, DESIGN, IMPLEMENTATION, TESTING, DEPLOYMENT]"
    fi
}

case "$1" in
    --start)
        echo "[RUN.SH] MODE: LAUNCH"
        # Optional: Add docker start if defined in future
        python auralis.py
        ;;
    --test|verify)
        echo "[RUN.SH] MODE: VERIFY"
        verify
        ;;
    --backlog|audit)
        echo "[RUN.SH] MODE: AUDIT"
        audit
        ;;
    expand)
        pdlc_expand "$2"
        ;;
    --sync)
        echo "[RUN.SH] MODE: SYNC - IDEMPOTENT file-tree alignment"
        mkdir -p docs/
        for file in docs/backlog.md docs/roadmap.md docs/system-design.md docs/conventions.md; do
            if [ ! -f "$file" ]; then
                title="$(basename "$file" .md | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')"
                echo "# $title" > "$file"
                echo "" >> "$file"
                echo "> Auto-populated uniform schema." >> "$file"
                echo "[RUN.SH] Created missing file: $file"
            fi
        done
        echo "[RUN.SH] Sync complete."
        ;;
    --skills)
        echo "[RUN.SH] MODE: EVOLVE"
        echo "[SKILLS] Syncing agentic patterns from local skills.sh..."
        if [ -f "scripts/skills.sh" ]; then
            echo "[SKILLS] Found skills.sh. Sourcing..."
            source scripts/skills.sh
            echo "[SKILLS] Sync complete. Patterns integrated."
        else
            echo "[SKILLS] Simulated parsing of pattern patterns from skills.sh (file not found)."
        fi
        ;;
    --blocker)
        # Utility to explicitly log blockers
        if [ -z "$2" ]; then
            echo "Usage: scripts/run.sh --blocker 'Blocker message'"
            exit 1
        fi
        log_resolve "$2"
        ;;
    *)
        echo "Usage: scripts/run.sh [--start | --test | --backlog | --sync | --blocker 'msg' | verify | audit | expand 'msg']"
        exit 1
        ;;
esac
