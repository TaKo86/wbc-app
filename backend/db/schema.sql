-- WBC Muay Thai NZ — PostgreSQL schema
-- Run against an empty database: psql $DATABASE_URL -f db/schema.sql

CREATE TYPE gender_t AS ENUM ('M', 'F');
CREATE TYPE title_level_t AS ENUM ('World', 'Pro', 'Amateur');
CREATE TYPE title_scope_t AS ENUM ('New Zealand', 'Oceania', 'International', 'World');
CREATE TYPE bout_status_t AS ENUM ('scheduled', 'completed', 'cancelled');
CREATE TYPE submission_status_t AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE gyms (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    city        TEXT
);

CREATE TABLE fighters (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    gender      gender_t NOT NULL,
    gym_id      INTEGER REFERENCES gyms(id) ON DELETE SET NULL,
    photo_url   TEXT,
    am_wins     INTEGER NOT NULL DEFAULT 0,
    am_losses   INTEGER NOT NULL DEFAULT 0,
    am_draws    INTEGER NOT NULL DEFAULT 0,
    pro_wins    INTEGER NOT NULL DEFAULT 0,
    pro_losses  INTEGER NOT NULL DEFAULT 0,
    pro_draws   INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, gender)
);
CREATE INDEX idx_fighters_gym ON fighters(gym_id);

CREATE TABLE fighter_submissions (
    id              SERIAL PRIMARY KEY,
    submitted_name  TEXT NOT NULL,
    submitted_email TEXT NOT NULL,
    name            TEXT NOT NULL,
    gender          gender_t NOT NULL,
    gym_name        TEXT,
    am_wins         INTEGER NOT NULL DEFAULT 0,
    am_losses       INTEGER NOT NULL DEFAULT 0,
    am_draws       INTEGER NOT NULL DEFAULT 0,
    pro_wins       INTEGER NOT NULL DEFAULT 0,
    pro_losses     INTEGER NOT NULL DEFAULT 0,
    pro_draws      INTEGER NOT NULL DEFAULT 0,
    status          submission_status_t NOT NULL DEFAULT 'pending',
    admin_note      TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_fighter_submissions_status ON fighter_submissions(status, created_at DESC);

CREATE TABLE submission_fights (
    id              SERIAL PRIMARY KEY,
    submission_id   INTEGER NOT NULL REFERENCES fighter_submissions(id) ON DELETE CASCADE,
    fight_number    SMALLINT NOT NULL CHECK (fight_number BETWEEN 1 AND 5),
    opponent_name   TEXT NOT NULL,
    result          VARCHAR(20) NOT NULL CHECK (result IN ('Win', 'Loss', 'Draw', 'No contest', 'Decision win', 'Decision loss', 'TKO win', 'TKO loss')),
    UNIQUE (submission_id, fight_number)
);

-- One row per weight class per gender. kg_display keeps "+90.7" style labels as text.
CREATE TABLE weight_classes (
    id          SERIAL PRIMARY KEY,
    gender      gender_t NOT NULL,
    code        VARCHAR(6) NOT NULL,          -- e.g. 'LW', 'SMW'
    name        TEXT NOT NULL,                -- e.g. 'Lightweight'
    kg_display  VARCHAR(8) NOT NULL,          -- e.g. '61.25', '+90.7'
    sort_order  SMALLINT NOT NULL,
    UNIQUE (gender, code)
);

-- A title is one belt: one weight class x one level x one scope.
-- (Most divisions only have Pro/Amateur; World titles use scope 'World'.)
CREATE TABLE titles (
    id              SERIAL PRIMARY KEY,
    weight_class_id INTEGER NOT NULL REFERENCES weight_classes(id) ON DELETE CASCADE,
    level           title_level_t NOT NULL,
    scope           title_scope_t NOT NULL DEFAULT 'New Zealand',
    UNIQUE (weight_class_id, level, scope)
);

-- Full history of title fights for a belt. The current champion is derived
-- (the winner of the most recent row for a title_id) rather than stored as
-- a flag, so there's one source of truth and it can't drift out of sync.
CREATE TABLE title_fights (
    id              SERIAL PRIMARY KEY,
    title_id        INTEGER NOT NULL REFERENCES titles(id) ON DELETE CASCADE,
    fight_date      DATE NOT NULL,
    winner_id       INTEGER NOT NULL REFERENCES fighters(id),
    opponent_id     INTEGER REFERENCES fighters(id),   -- null for a vacant-title award
    event           TEXT,
    is_vacant_win   BOOLEAN NOT NULL DEFAULT false,
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_title_fights_title_date ON title_fights(title_id, fight_date);

-- Ranked contenders under a title. The champion is NOT a row here — they
-- come from title_fights. rank is nullable so "eligible but unranked"
-- fighters can still be attached to a division via requirement/flag.
CREATE TABLE rankings (
    id              SERIAL PRIMARY KEY,
    title_id        INTEGER NOT NULL REFERENCES titles(id) ON DELETE CASCADE,
    fighter_id      INTEGER NOT NULL REFERENCES fighters(id) ON DELETE CASCADE,
    rank            SMALLINT,
    requirement     TEXT,      -- e.g. 'Needs 1 Muay Thai win'
    flag            TEXT,      -- e.g. 'Vacated title'
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (title_id, fighter_id)
);
CREATE INDEX idx_rankings_title_rank ON rankings(title_id, rank);

CREATE TABLE bouts (
    id              SERIAL PRIMARY KEY,
    scheduled_at    TIMESTAMPTZ NOT NULL,
    weight_class_id INTEGER NOT NULL REFERENCES weight_classes(id),
    title_id        INTEGER REFERENCES titles(id),     -- null if not a title fight
    fighter_a_id    INTEGER NOT NULL REFERENCES fighters(id),
    fighter_b_id    INTEGER NOT NULL REFERENCES fighters(id),
    rounds          SMALLINT NOT NULL DEFAULT 5,
    city            TEXT,
    status          bout_status_t NOT NULL DEFAULT 'scheduled',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_bouts_scheduled ON bouts(scheduled_at);

CREATE TABLE news (
    id           SERIAL PRIMARY KEY,
    published_on DATE NOT NULL,
    title        TEXT NOT NULL,
    summary      TEXT,
    url          TEXT,
    source       TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_news_published ON news(published_on DESC);
