# Offline Caching Strategy Design

This document describes the architectural implementation of the `OfflineCache` strategy for mobile payload synchronization within Auralis.

## Objective

The `OfflineCache` singleton on the mobile client orchestrates the intelligent caching and offline availability of audio content. It ensures down-sampled `.opus` files are stored securely and retrieved efficiently while respecting limited mobile storage configurations.

## Implementation Details

### SQLite Mapping

All mobile tracks are cataloged in an embedded SQLite database table (`mobile_tracks`). Each record links audio metadata with the down-sampled local file path.

```sql
CREATE TABLE IF NOT EXISTS mobile_tracks (
    id TEXT PRIMARY KEY,
    title TEXT,
    artist TEXT,
    local_path TEXT,
    file_size INTEGER,
    last_accessed TIMESTAMP
);
```

### LRU Eviction Policy

A Least Recently Used (LRU) algorithm automatically frees space based on the user-defined maximum cache size. When a sync job attempts to cache a new file and total storage exceeds the threshold, the policy deletes records (and their linked `.opus` files) ordered by the oldest `last_accessed` timestamp.

### Example Architecture

```python
import sqlite3
import os

class OfflineCache:
    def __init__(self, db_path: str, max_size_bytes: int):
        self.conn = sqlite3.connect(db_path)
        self.max_size_bytes = max_size_bytes

    def cache_track(self, track_id: str, file_path: str, file_size: int):
        self._enforce_lru(file_size)
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO mobile_tracks (id, local_path, file_size, last_accessed) VALUES (?, ?, ?, datetime('now'))", (track_id, file_path, file_size))
        self.conn.commit()

    def _enforce_lru(self, incoming_size: int):
        cursor = self.conn.cursor()
        while self.get_total_size() + incoming_size > self.max_size_bytes:
            cursor.execute("SELECT id, local_path FROM mobile_tracks ORDER BY last_accessed ASC LIMIT 1")
            oldest = cursor.fetchone()
            if oldest:
                os.remove(oldest[1])
                cursor.execute("DELETE FROM mobile_tracks WHERE id=?", (oldest[0],))
                self.conn.commit()
            else:
                break
```
