# WBC Muay Thai NZ — backend

FastAPI + PostgreSQL API for the site. Read-only for now (GET endpoints only) — write/admin
endpoints can come later once you've decided who updates data and how.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit DATABASE_URL if needed
```

Create the database, then load the schema:

```bash
createdb wbc_muaythai
psql $DATABASE_URL -f db/schema.sql
```

Load the data that's already been extracted from your spreadsheet:

```bash
python seed.py data.json
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Docs at http://localhost:8000/docs.

## Endpoints

- `GET /champions` — every title's current holder (derived from `title_fights`, not stored directly)
- `GET /rankings?gender=M|F&level=Pro|Amateur` — every division's champion + ranked contenders
- `GET /rankings/{title_id}` — one division
- `GET /results?limit=&offset=` — title fight history, newest first
- `GET /bouts?include_past=false` — scheduled bouts (empty until some are added)
- `GET /news?limit=`

## How the schema is organised

- **fighters / gyms / weight_classes** — the base entities.
- **titles** — one row per belt: a weight class × level (World/Pro/Amateur) × scope.
- **title_fights** — full history of who beat whom for a title. There's no `is_current`
  flag; the current champion is just whoever won the most recent row for that title, and
  defences are counted from there. One source of truth, nothing to keep in sync.
- **rankings** — contenders under a title, separate from the champion row.
- **bouts** — scheduled fights, optionally linked to a title.

## Known data issues from the seed

Run `python seed.py data.json` and read the output — it prints every result whose winner
name didn't match an existing fighter (spelling differences between your spreadsheet's
tabs) instead of guessing and silently creating a duplicate. Fix the name in the source
JSON (or add an alias) and re-run.
