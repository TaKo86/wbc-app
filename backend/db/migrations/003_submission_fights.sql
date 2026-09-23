CREATE TABLE submission_fights (
    id              SERIAL PRIMARY KEY,
    submission_id   INTEGER NOT NULL REFERENCES fighter_submissions(id) ON DELETE CASCADE,
    fight_number    SMALLINT NOT NULL CHECK (fight_number BETWEEN 1 AND 5),
    opponent_name   TEXT NOT NULL,
    result          VARCHAR(20) NOT NULL CHECK (result IN ('Win', 'Loss', 'Draw', 'No contest')),
    UNIQUE (submission_id, fight_number)
);