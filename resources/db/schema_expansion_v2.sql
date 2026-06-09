-- V2 Schema expansion
CREATE TABLE IF NOT EXISTS v2_metadata (
    id INTEGER PRIMARY KEY,
    track_id TEXT NOT NULL,
    gharana TEXT,
    instrument TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
