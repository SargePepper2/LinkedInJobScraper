# LinkedIn Job Skills Analyzer

Scrape job postings, extract in-demand skills, and get personalized career intelligence.

**What it does:**
- Extracts tech skills from job descriptions using taxonomy-based NLP
- Ranks skills by market demand across all collected jobs
- Shows skill co-occurrence (which skills appear together)
- Compares your skills against market demand (gap analysis)
- Suggests LinkedIn profile optimizations based on trending skills

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Recharts |
| Database | PostgreSQL 16 |
| CLI | Typer + Rich |
| CI/CD | GitHub Actions, Docker Compose |

## Quick Start

```bash
# Start everything with Docker
docker compose up

# Or run locally:

# Backend
cd backend
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:5173

## CLI Usage

```bash
# Import a job description
echo "Senior React Developer needed with TypeScript..." | jobscan import-paste --title "Sr React Dev"

# Import from CSV
jobscan import-csv jobs.csv

# View skill rankings
jobscan rankings

# Gap analysis
jobscan gap 1  # profile ID
```

## Project Structure

```
backend/          Python FastAPI backend
  app/
    models/       SQLAlchemy models (skills, jobs, profiles)
    routers/      API route handlers
    services/     Business logic (extractor, analyzer, importer)
  cli/            Typer CLI commands
  data/           Skill taxonomy JSON
  migrations/     Alembic database migrations
  tests/          pytest test suite
frontend/         React TypeScript frontend
  src/
    pages/        Dashboard, Rankings, Gap Analysis, Import, Profile, Optimizer
    components/   Shared UI components
    api/          TanStack Query hooks + typed API client
```

## License

MIT
