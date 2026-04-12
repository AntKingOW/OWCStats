import sqlite3
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
DB_PATH = BASE / "owcs_vod_events.db"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vod_sources (
    vod_id TEXT PRIMARY KEY,
    source_url TEXT,
    local_path TEXT NOT NULL,
    source_mode TEXT NOT NULL,
    duration_seconds REAL NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vod_clips (
    clip_id TEXT PRIMARY KEY,
    vod_id TEXT NOT NULL,
    label TEXT NOT NULL,
    clip_path TEXT NOT NULL,
    start_seconds REAL NOT NULL,
    end_seconds REAL NOT NULL,
    duration_seconds REAL NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (vod_id) REFERENCES vod_sources(vod_id)
);

CREATE TABLE IF NOT EXISTS detected_events (
    event_id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    event_time_seconds REAL NOT NULL,
    event_type TEXT NOT NULL,
    player_name TEXT,
    hero_name TEXT,
    target_player_name TEXT,
    target_hero_name TEXT,
    team_name TEXT,
    confidence REAL,
    source_frame_path TEXT,
    raw_payload_json TEXT,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (clip_id) REFERENCES vod_clips(clip_id)
);

CREATE TABLE IF NOT EXISTS review_rows (
    review_row_id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    row_type TEXT NOT NULL,
    row_order INTEGER NOT NULL,
    row_payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reviewer_note TEXT,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (clip_id) REFERENCES vod_clips(clip_id)
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    print(f"Initialized database: {DB_PATH}")


if __name__ == "__main__":
    main()
