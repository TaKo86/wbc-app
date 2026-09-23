# WBC App

This repo contains a full-stack Muay Thai / boxing site:
- FastAPI backend in [backend](backend)
- Vite + React + TypeScript frontend in [frontend](frontend)
- PostgreSQL-backed data layer for the real app
- pytest-based backend test suite
- GitHub Actions workflow for backend CI

This README is written as an operational handoff for a human or an agentic coding assistant. It is meant to reduce the time to first successful change.

## Current verified state

As of the latest verification, the project is working in the following state:
- The backend is configured to use PostgreSQL at localhost:5432.
- The database has been created and initialized locally.
- The schema from [backend/db/schema.sql](backend/db/schema.sql) has been applied.
- The backend can connect successfully to PostgreSQL using SQLAlchemy.
- The backend pytest suite has been run successfully in the current environment and exited successfully.
- The frontend dependencies are installed and the frontend test runner is configured via Vitest.

The live app configuration is effectively:
- PostgreSQL URL: `postgresql+psycopg2://wbc:wbc@localhost:5432/wbc_muaythai`
- Backend server default CORS origin: `http://localhost:5173`

## Monorepo layout

```text
wbc-app/
├── .github/
│   └── workflows/
│       └── backend-tests.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── routers/
│   │       ├── bouts.py
│   │       ├── champions.py
│   │       ├── news.py
│   │       ├── rankings.py
│   │       └── results.py
│   ├── db/
│   │   └── schema.sql
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_main.py
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── requirements.txt
│   ├── seed.py
│   └── venv/
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .gitignore
│   ├── README.md
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── readme.md
└── .gitignore (root if present)
```

## Backend architecture

### Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2 + pydantic-settings
- psycopg2 for PostgreSQL
- pytest for backend tests

### App entrypoint
- [backend/app/main.py](backend/app/main.py)
- It creates the FastAPI app and registers routers for:
  - champions
  - rankings
  - results
  - bouts
  - news
- The health endpoint is exposed at `/health`.

### Database layer
- [backend/app/database.py](backend/app/database.py) creates the SQLAlchemy `engine` and `SessionLocal`.
- [backend/app/config.py](backend/app/config.py) loads settings from the local `.env` file.
- The real DB connection is not SQLite; it is PostgreSQL in local development.

### Important DB facts
- The database name is `wbc_muaythai`.
- The configured local app user is `wbc` with password `wbc`.
- The connection is expected to be available on `localhost:5432`.
- The schema in [backend/db/schema.sql](backend/db/schema.sql) defines the app tables.

### API routes
The backend is read-only at the moment. The confirmed routes are:

```text
GET /health
GET /champions
GET /rankings?gender=M|F&level=World|Pro|Amateur
GET /rankings/{title_id}
GET /results
GET /bouts
GET /news
```

There are no write endpoints yet.

### Important business logic and schema details
Key understanding for agentic work:
- Models live in [backend/app/models.py](backend/app/models.py).
- Schemas live in [backend/app/schemas.py](backend/app/schemas.py).
- The response objects are not always flat DB rows; nested DTOs are common, especially for rankings and champions.
- Ranking responses are derived and nested.
- The title/champion logic is derived from `title_fights`; there is no simple direct champion field in the database.
- Seed logic in [backend/seed.py](backend/seed.py) contains nontrivial normalization and duplicate detection logic for raw imported data.

## Frontend architecture

### Stack
- React 19
- TypeScript
- Vite
- Vitest + Testing Library for frontend tests

### Scripts
From [frontend/package.json](frontend/package.json):

```powershell
cd frontend
npm install
npm run dev
npm run build
npm run test
npm run test:watch
```

### Frontend notes
- Vite runs at `http://localhost:5173` by default.
- The frontend is expected to talk to the backend at `http://127.0.0.1:8000` or equivalent.
- The app is not yet fully wired to all pages; it is in a partial integration state with examples rather than a fully complete site.

## Testing

### Backend tests
The backend test suite is in [backend/tests](backend/tests):
- [backend/tests/conftest.py](backend/tests/conftest.py)
- [backend/tests/test_main.py](backend/tests/test_main.py)

The test approach is:
- Use FastAPI `TestClient`
- Override `get_db` dependency to use in-memory SQLite for each test
- Keep the real PostgreSQL database separate from test execution

The current suite has been run successfully in the repo environment and exit status was successful.

### Frontend tests
The frontend uses Vitest and Testing Library. This is configured in [frontend/package.json](frontend/package.json) and should be used for UI-level verification.

## CI

The GitHub workflow in [.github/workflows/backend-tests.yml](.github/workflows/backend-tests.yml) runs backend pytest automatically on changes in `backend/**` and workflow changes.

Current CI behavior:
- Runs on push and PR to `main`
- Uses Python 3.11
- Installs backend requirements
- Creates a temporary `.env` for tests
- Executes pytest

## Local dev setup

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Then open:
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

Then open:
- App: `http://localhost:5173`

## Environment and secrets

### Backend `.env`
The active backend environment file currently contains the actual local PostgreSQL config and should be treated as local-only credentials.

Example shape:
```env
DATABASE_URL=postgresql+psycopg2://wbc:wbc@localhost:5432/wbc_muaythai
CORS_ORIGINS=http://localhost:5173
```

Important:
- `.env` should not be committed to the repo.
- The repo includes `.gitignore` entries for generated and local environment files.
- Do not share production credentials or commit secret values.

## Git hygiene / repo gotchas

Several repo-state issues have already been encountered and resolved.

### Important patterns
- Virtualenv folders should not be committed.
- Python cache folders such as `__pycache__` should be ignored.
- `.env` files should remain local-only.
- Local PostgreSQL installs are legitimate for development, but they must use the matching app credentials in the backend `.env` file.

### Generated files to ignore
These are expected to stay out of Git:
- `venv/`
- `__pycache__/`
- `**/__pycache__/`
- `*.pyc`
- `.env`

## Current project risks / known follow-ups

These are the main things to keep in mind for future work:
1. The backend is configured for a real database, so it will fail if PostgreSQL is not running locally.
2. The backend is currently read-only; no write/admin endpoints exist yet.
3. Some schema semantics are derived rather than stored directly; do not assume a one-to-one mapping between DB columns and API DTOs.
4. Seed logic has a lot of data-normalization behavior and should be treated as a sensitive part of the source data pipeline.
5. The frontend is partially scaffolded and not yet fully wired to all backend resources.

## Recommended next tasks

If continuing work on this repo, the sensible next sequence is:
1. Ensure PostgreSQL is running locally.
2. Start the backend API.
3. Verify `/health` and a few core endpoints.
4. Wire the frontend pages to the backend client layer.
5. Add or tighten tests around ranking/champion logic and data edge cases.

## Quick commands

### Start backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Run backend tests
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

### Start frontend
```powershell
cd frontend
npm install
npm run dev
```

### Check DB connectivity
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); print(conn.execute(text('SELECT 1')).scalar()); conn.close()"
```

## Summary

This repo is a working monorepo with a real PostgreSQL-backed backend and a Vite React frontend. The backend is the more mature and verified half of the project; the frontend is in a progressive integration phase. The data model and API are real, not placeholder mocks, and the project is ready for iterative feature work as long as local PostgreSQL and the matching `.env` values are available.

