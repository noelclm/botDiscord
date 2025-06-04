CREATE TABLE IF NOT EXISTS discord_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    member_name TEXT NOT NULL,
    member_display_name TEXT NOT NULL,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    mobile BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calendar_event (
    chanel TEXT NOT NULL,
    msg TEXT NOT NULL,
    time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);