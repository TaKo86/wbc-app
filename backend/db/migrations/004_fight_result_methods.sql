ALTER TABLE submission_fights
    DROP CONSTRAINT IF EXISTS submission_fights_result_check;

ALTER TABLE submission_fights
    ADD CONSTRAINT submission_fights_result_check
    CHECK (result IN (
        'Win', 'Loss', 'Draw', 'No contest',
        'Decision win', 'Decision loss', 'TKO win', 'TKO loss'
    ));