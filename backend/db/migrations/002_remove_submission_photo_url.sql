-- Run only if 001_fighter_submissions.sql was already applied.
ALTER TABLE fighter_submissions DROP COLUMN IF EXISTS photo_url;
