CREATE TABLE IF NOT EXISTS parent_context_events (
    id          TEXT PRIMARY KEY,
    parent_id   TEXT NOT NULL,
    student_id  TEXT,
    tags_json   TEXT NOT NULL DEFAULT '[]',
    free_text   TEXT,
    engine_hint TEXT,
    ai_insight  TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
