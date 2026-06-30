# EvalForge

**Continuous Evaluation, Observability & CI/CD for AI Systems.**

Think *GitHub Actions + MLflow + LangSmith + Grafana*, built specifically for LLM
applications. Create a project, configure your model/RAG stack, upload an evaluation
dataset, run an evaluation, and watch accuracy, latency, cost, hallucination rate and
more on a live dashboard. Compare runs, version prompts and datasets, track experiments,
and catch quality regressions in CI — like failing a unit test, but for AI quality.

## Status

Built as a runnable vertical slice first (full user journey end-to-end), with advanced
infrastructure layered on. Every commit runs.

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, Celery, Redis
- **Frontend:** Next.js, TypeScript, Tailwind
- **Data:** PostgreSQL (SQLite locally), object storage for artifacts
- **Ops:** Docker, GitHub Actions, Prometheus + Grafana

## Local dev (zero external services required)

The backend defaults to **SQLite** and a **mock LLM provider**, and runs background jobs
**synchronously** — so it works with no Postgres, Redis, or API keys.

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API.

To enable real services, set in `.env`:
- `DATABASE_URL` — a Postgres URL
- `REDIS_URL` — switches Celery to async workers
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` — real model calls

## Repo layout

```
backend/    FastAPI service, evaluation engine, workers
frontend/   Next.js dashboard
docs/       architecture & design notes
```
