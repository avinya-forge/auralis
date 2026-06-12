-- Auralis V2 Schema Migration
-- Expands existing schema with Gharana/Instrument tracking tables.

CREATE TABLE IF NOT EXISTS instruments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    family TEXT
);

CREATE TABLE IF NOT EXISTS gharanas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    region TEXT
);

CREATE TABLE IF NOT EXISTS track_instruments (
    track_id TEXT NOT NULL,
    instrument_id INTEGER NOT NULL,
    confidence REAL NOT NULL,
    PRIMARY KEY (track_id, instrument_id),
    FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS track_gharanas (
    track_id TEXT NOT NULL,
    gharana_id INTEGER NOT NULL,
    confidence REAL NOT NULL,
    PRIMARY KEY (track_id, gharana_id),
    FOREIGN KEY (gharana_id) REFERENCES gharanas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vocalists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    gharana_id INTEGER,
    FOREIGN KEY (gharana_id) REFERENCES gharanas(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS track_vocalists (
    track_id TEXT NOT NULL,
    vocalist_id INTEGER NOT NULL,
    confidence REAL NOT NULL,
    PRIMARY KEY (track_id, vocalist_id),
    FOREIGN KEY (vocalist_id) REFERENCES vocalists(id) ON DELETE CASCADE
);
