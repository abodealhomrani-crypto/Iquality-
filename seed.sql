PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS activity_codes (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    trade TEXT NOT NULL,
    expected_sequence INTEGER NOT NULL,
    location TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_code TEXT NOT NULL,
    frame_path TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('supported', 'contradicted', 'not_observed')),
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reason TEXT NOT NULL,
    marker_ids TEXT,
    approval_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (approval_status IN ('pending', 'approved', 'rejected', 'escalated')),
    FOREIGN KEY (activity_code) REFERENCES activity_codes(code)
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_id INTEGER NOT NULL UNIQUE,
    approver_role TEXT NOT NULL DEFAULT 'QS Approver',
    decision TEXT NOT NULL DEFAULT 'pending'
        CHECK (decision IN ('pending', 'approved', 'rejected', 'escalated')),
    decided_at TEXT,
    notes TEXT,
    FOREIGN KEY (observation_id) REFERENCES observations(id)
);

INSERT OR IGNORE INTO activity_codes
    (code, name, trade, expected_sequence, location)
VALUES
    ('FORM-L3', 'Level 3 formwork', 'Structural', 10, 'Level 3'),
    ('REBAR-L3', 'Level 3 rebar fixing', 'Structural', 20, 'Level 3'),
    ('CONC-L3', 'Level 3 concrete pour', 'Structural', 30, 'Level 3'),
    ('MEP-L3', 'Level 3 MEP installation', 'MEP', 40, 'Level 3');
