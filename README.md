# Labor Market Intelligence Platform

MVP scaffold for a legally safer job market intelligence platform built around:

- public ATS APIs
- public company career pages
- open datasets
- reproducible enrichment pipelines

## Stack

- Python 3.12
- FastAPI
- Prefect
- PostgreSQL
- Docker Compose

## Current MVP scope

- ingest jobs from Greenhouse Job Board API
- normalize canonical job records
- store raw payloads plus append-only snapshots
- expose a simple analytics-ready API

## Project layout

```text
api/          FastAPI application
pipelines/    Prefect flows, connectors, normalizers
sql/          Database bootstrap SQL
```

## Quick start

1. Copy `.env.example` to `.env`
2. Set `GREENHOUSE_BOARD_TOKEN` to a public Greenhouse board token such as `openai`
3. Start services:

```bash
docker compose up --build
```

4. Ingest jobs:

```bash
docker compose run --rm pipelines python -m flows.ingest_greenhouse
```

5. Open API docs at `http://localhost:8000/docs`

## Initial data model

- `job_postings`: current canonical view per `(source, source_job_id)`
- `job_snapshots`: append-only historical snapshots of observed postings

This keeps the MVP simple while preserving history for downstream trend analysis.

## Suggested next steps

- add Lever and Ashby connectors
- add salary normalization and seniority detection
- add dbt models for marts
- add ClickHouse for heavier analytics
- add embeddings and semantic search with `pgvector`
