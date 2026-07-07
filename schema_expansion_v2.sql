-- Auralis Schema Expansion v2
-- Extends the multi-modal knowledge graph schema

-- Gharanas (Musical lineages or schools in Indian Classical Music)
CREATE TABLE IF NOT EXISTS gharanas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    founded_year INTEGER,
    founder TEXT
);

-- Instruments (Specific physical instruments and their classifications)
CREATE TABLE IF NOT EXISTS instruments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    family TEXT, -- e.g., String, Percussion, Wind
    origin_region TEXT,
    description TEXT
);

-- Vocalist Signatures (Unique acoustic characteristics for specific singers)
CREATE TABLE IF NOT EXISTS vocalist_signatures (
    id TEXT PRIMARY KEY,
    vocalist_id TEXT NOT NULL,
    signature_vector BLOB NOT NULL, -- Stored as raw bytes (e.g., numpy array)
    base_frequency REAL,
    timbre_profile TEXT,
    FOREIGN KEY(vocalist_id) REFERENCES artists(id)
);

-- Junction table linking artists to their Gharanas
CREATE TABLE IF NOT EXISTS artist_gharanas (
    artist_id TEXT NOT NULL,
    gharana_id TEXT NOT NULL,
    PRIMARY KEY (artist_id, gharana_id),
    FOREIGN KEY(artist_id) REFERENCES artists(id),
    FOREIGN KEY(gharana_id) REFERENCES gharanas(id)
);

-- Junction table linking recordings to specific instruments
CREATE TABLE IF NOT EXISTS recording_instruments (
    recording_id TEXT NOT NULL,
    instrument_id TEXT NOT NULL,
    PRIMARY KEY (recording_id, instrument_id),
    FOREIGN KEY(recording_id) REFERENCES recordings(id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(id)
);
