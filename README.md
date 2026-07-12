# VisaSponsor Jobs

VisaSponsor Jobs is a full-stack sponsor-search application focused on two different signals:

- Historical employment-based sponsorship evidence from U.S. Department of Labor OFLC PERM disclosure data
- Current job openings and whether their text explicitly mentions or rejects sponsorship

The application does **not** claim that a historical PERM filing means a worker received a green card, and it does **not** claim that a current job offers sponsorship unless the job source says so directly.

## Current scope

This repository now matches the requested product direction:

- React + TypeScript + Vite frontend with routing
- FastAPI + SQLAlchemy backend
- SQLite-friendly local development with PostgreSQL-ready configuration
- Demo seed data for Phase 1 workflows
- Dynamic metadata endpoints
- Sponsor search and employer detail endpoints
- Current-job sponsorship classification with negative-language override
- PERM importer scaffolding with year mapping files
- Admin import endpoints with token-based protection
- Docker Compose setup for local infrastructure

External government-download automation and third-party job API credentials are intentionally scaffolded, not hardcoded.

## Important data disclaimer

Results are based on historical and current public filing data. A previous filing does not guarantee that an employer or current position will provide immigration sponsorship.

## Project structure

```text
backend/
  alembic.ini
  app/
    api/
    config.py
    database.py
    demo_seed.py
    importers/
    main.py
    migrations/
    models/
    schemas/
    services/
    sources/
    utils/
  requirements.txt
  tests/

frontend/
  package.json
  src/
    api/
    components/
    pages/
    types/
    App.tsx
    main.tsx
```

## Local backend setup

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs on `http://127.0.0.1:8000`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173`.

## Docker setup

```bash
docker compose up --build
```

This starts:

- PostgreSQL
- Redis
- FastAPI backend
- Vite frontend

## Environment variables

Copy `.env.example` to `.env` and adjust as needed.

Key values:

- `DATABASE_URL`: SQLite for local demo or PostgreSQL for production
- `REDIS_URL`: Redis connection string
- `ADMIN_TOKEN`: required for administration import endpoints
- `CORS_ORIGINS`: allowed frontend origins
- `VITE_API_BASE_URL`: frontend API base URL
- `ENABLE_DEMO_SEED`: enables synthetic demo records on startup

## Running the demo

The backend seeds a clearly labeled synthetic dataset on startup when `ENABLE_DEMO_SEED=true`.

The demo data includes:

- Multiple fiscal years
- Multiple employers
- Certified, denied, and withdrawn outcomes
- IT occupations
- Current jobs with positive sponsorship language
- Current jobs with negative sponsorship language
- Current jobs with unclear language

## API overview

Health:

- `GET /api/health`

Metadata:

- `GET /api/metadata/fiscal-years`
- `GET /api/metadata/it-professions`
- `GET /api/metadata/states`
- `GET /api/metadata/case-statuses`
- `GET /api/metadata/data-freshness`

Sponsor search:

- `POST /api/sponsors/search`

Employer details:

- `GET /api/employers/{employerId}`
- `GET /api/employers/{employerId}/perm-cases`
- `GET /api/employers/{employerId}/occupations`
- `GET /api/employers/{employerId}/statistics`
- `GET /api/employers/{employerId}/current-jobs`

Current jobs:

- `POST /api/jobs/search`

Comparison:

- `POST /api/employers/compare`

Administration:

- `POST /api/admin/imports/perm/upload`
- `POST /api/admin/imports/perm/from-source`
- `GET /api/admin/imports`
- `GET /api/admin/imports/{importId}`
- `POST /api/admin/imports/{importId}/retry`

## Importing official PERM files

The PERM importer currently supports:

- CSV and Excel uploads
- File checksum generation
- Duplicate import detection
- Year-based column mapping
- Canonical field conversion
- Employer normalization
- Occupation extraction
- Import logging

Mapping files live in:

- `backend/app/importers/mappings/perm_fy2023.py`
- `backend/app/importers/mappings/perm_fy2024.py`
- `backend/app/importers/mappings/perm_fy2025.py`
- `backend/app/importers/mappings/perm_fy2026.py`

## Running tests

```bash
cd backend
pytest
```

## Starting scheduled imports

Scheduled refresh behavior is scaffolded through configuration and service layout. The current codebase exposes refresh timing metadata and import infrastructure, and is ready for APScheduler or Celery job registration in a follow-up step.

## Configuring job APIs

The current-jobs system is intentionally adapter-based. Add legally accessible sources under `backend/app/sources/` and wire them through service orchestration without bypassing terms of use, robots restrictions, authentication controls, or anti-bot protections.

## Production deployment notes

- Use PostgreSQL instead of SQLite
- Set a strong `ADMIN_TOKEN`
- Restrict `CORS_ORIGINS`
- Disable demo seed data
- Run Alembic migrations before starting the API
- Front the API with TLS termination and request-size limits

## Known limitations in this revision

- This revision prioritizes the requested Phase 1 flow and Phase 2 scaffolding
- Saved searches, exports, and richer comparison workflows are scaffolded rather than fully completed
- Official-source background downloading is intentionally conservative and not wired to arbitrary remote URLs
- Redis caching and scheduled workers are configured but not fully activated yet
