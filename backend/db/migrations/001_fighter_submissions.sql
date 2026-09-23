-- Run once against an existing deployment.
CREATE TYPE submission_status_t AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE fighter_submissions (
    id              SERIAL PRIMARY KEY,
    submitted_name  TEXT NOT NULL,
    submitted_email TEXT NOT NULL,
    name            TEXT NOT NULL,
    gender          gender_t NOT NULL,
    gym_name        TEXT,
    am_wins         INTEGER NOT NULL DEFAULT 0,
    am_losses       INTEGER NOT NULL DEFAULT 0,
    am_draws        INTEGER NOT NULL DEFAULT 0,
    pro_wins       INTEGER NOT NULL DEFAULT 0,
    pro_losses     INTEGER NOT NULL DEFAULT 0,
    pro_draws      INTEGER NOT NULL DEFAULT 0,
    status          submission_status_t NOT NULL DEFAULT 'pending',
    admin_note      TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_fighter_submissions_status
    ON fighter_submissions(status, created_at DESC);