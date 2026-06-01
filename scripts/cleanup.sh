#!/usr/bin/env bash
# Auralis Cleanup Script
# Prunes orphaned staging records and temporary files.

DB_PATH="${1:-cache.db}"
STAGING_DIR="${2:-./uploads}"

echo "[CLEANUP] Pruning database: $DB_PATH"

# Delete records older than 7 days that are still in 'pending' or 'failed'
python3 -c "
import sqlite3
from src.utils.db_utils import get_db_connection
try:
    with get_db_connection('$DB_PATH') as conn:
        conn.execute(\"\"\"
            DELETE FROM ingestion_staging
            WHERE (status = 'pending_validation' OR status = 'extraction_failed')
            AND extracted_at < datetime('now', '-7 days')
        \"\"\")
        print('[DB] Pruned old staging records.')
except Exception as e:
    print(f'[DB] Cleanup skipped or failed: {e}')
"

# Remove orphaned .part files in upload directory
if [ -d "$STAGING_DIR" ]; then
    echo "[FS] Pruning orphaned chunks in: $STAGING_DIR"
    find "$STAGING_DIR" -name "*.part*" -mtime +2 -delete
fi

echo "[CLEANUP] Done."
