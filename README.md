<p align="center">
  <img src="./docs/images/branding/banner.png" alt="Labor Market Intelligence Platform banner" width="100%" />
</p>

<h1 align="center">Labor Market Intelligence Platform</h1>

<p align="center">
  <strong>Legal-first job intelligence infrastructure for analytics, enrichment, and AI-ready market insights.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Prefect-Orchestration-1F3A8A?style=flat-square" alt="Prefect" />
  <img src="https://img.shields.io/badge/PostgreSQL-Storage-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/status-MVP%20in%20progress-2E7D32?style=flat-square" alt="Status" />
</p>

<p align="center">
  <strong>Public ATS APIs</strong> • <strong>Historical Tracking</strong> • <strong>Normalization</strong> • <strong>AI Hooks</strong>
</p>

<p align="center">
  Building a production-oriented foundation for labor market intelligence using safer public sources instead of brittle, high-risk scraping.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#roadmap">Roadmap</a>
</p>

<hr/>

<table>
  <tr>
    <td width="25%" align="center">
      <strong>Source Strategy</strong><br/>
      Public ATS APIs
    </td>
    <td width="25%" align="center">
      <strong>Storage Model</strong><br/>
      Canonical + Historical
    </td>
    <td width="25%" align="center">
      <strong>Primary Goal</strong><br/>
      Analytics-ready jobs data
    </td>
    <td width="25%" align="center">
      <strong>Future Layer</strong><br/>
      Search + AI enrichment
    </td>
  </tr>
</table>

<hr/>

## EN | About

This repository is a serious MVP for a **labor market intelligence platform**.

It is designed to ingest, normalize, preserve, and serve job-market data in a way that is:

- safer from a compliance perspective
- easier to scale technically
- ready for analytics
- ready for future AI layers
- strong as a portfolio-grade engineering project

Instead of starting with aggressive scraping from fragile platforms, this project begins with:

- public ATS APIs
- public company careers pages
- open datasets
- structured normalization
- append-only historical storage

> The core idea is simple: build the data platform first, then layer intelligence and AI on top of clean, reproducible pipelines.

## ES | Sobre el proyecto

Este repositorio es un MVP serio de una **plataforma de inteligencia del mercado laboral**.

Esta pensado para ingestar, normalizar, conservar y exponer datos de empleo de una forma:

- mas segura desde lo legal
- mas escalable tecnicamente
- lista para analitica
- preparada para futuras capas de AI
- fuerte como proyecto de portfolio

En lugar de arrancar con scraping agresivo sobre plataformas fragiles, el proyecto empieza con:

- APIs publicas de ATS
- paginas publicas de careers
- datasets abiertos
- normalizacion estructurada
- almacenamiento historico append-only

> La idea central es clara: construir primero la base de datos y los pipelines, y despues sumar inteligencia y AI arriba.

<hr/>

## Highlights

<table>
  <tr>
    <td width="33%">
      <h3>Safer by design</h3>
      <p>Starts from public ATS APIs and durable public sources instead of brittle scraping workflows.</p>
    </td>
    <td width="33%">
      <h3>History from day one</h3>
      <p>Stores canonical records and append-only snapshots so trend analysis is possible later.</p>
    </td>
    <td width="33%">
      <h3>AI-ready foundation</h3>
      <p>Structured data prepared for enrichment, embeddings, semantic search, and reporting.</p>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="50%">
      <h3>Implemented now</h3>
      <ul>
        <li>FastAPI backend</li>
        <li>PostgreSQL persistence</li>
        <li>Prefect ingestion flow</li>
        <li>Greenhouse connector</li>
        <li>Normalization layer</li>
        <li>Historical snapshots</li>
      </ul>
    </td>
    <td width="50%">
      <h3>Next layers</h3>
      <ul>
        <li>Lever and Ashby connectors</li>
        <li>Salary normalization</li>
        <li>Skill extraction</li>
        <li>Remote classification</li>
        <li>Embeddings and semantic search</li>
        <li>Analytics marts and dashboards</li>
      </ul>
    </td>
  </tr>
</table>

<hr/>

## Why this approach

<table>
  <tr>
    <th align="left">Brittle path</th>
    <th align="left">This project's path</th>
  </tr>
  <tr>
    <td>Aggressive scraping first</td>
    <td>Public APIs and durable public sources first</td>
  </tr>
  <tr>
    <td>Low traceability</td>
    <td>Raw payload preservation and snapshots</td>
  </tr>
  <tr>
    <td>Fast prototype, weak foundation</td>
    <td>Serious MVP, stronger production path</td>
  </tr>
  <tr>
    <td>Harder compliance posture</td>
    <td>Cleaner legal-first strategy</td>
  </tr>
  <tr>
    <td>Rebuild later for analytics</td>
    <td>Analytics-ready from the start</td>
  </tr>
</table>

<hr/>

## Architecture

```text
                 +-----------------+
                 | Job Sources     |
                 |-----------------|
                 | Greenhouse API  |
                 | Lever API       |
                 | Ashby           |
                 | Company sites   |
                 | Public datasets |
                 +--------+--------+
                          |
                    Ingestion Layer
                          |
             +------------+------------+
             |                         |
       Raw JSON Storage          Metadata Queue
             |                         |
             +------------+------------+
                          |
                    Normalization
                          |
                    NLP Enrichment
                          |
                 Deduplication Layer
                          |
                      Warehouse
                          |
          +---------------+---------------+
          |                               |
      Analytics API                  Search API
          |                               |
      Dashboards                   Semantic Search
```

<details>
<summary><strong>MVP slice implemented today</strong></summary>

- ingestion
- normalization
- historical persistence
- API exposure

</details>

<hr/>

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| API | FastAPI | Serve job records and future analytics endpoints |
| Orchestration | Prefect | Run ingestion and enrichment flows |
| Database | PostgreSQL | Store canonical jobs and historical snapshots |
| Local Infra | Docker Compose | Portable local environment |
| ORM | SQLAlchemy | Data models and persistence |
| Future NLP | spaCy + LLMs | Skill extraction and text enrichment |
| Future Search | pgvector | Embeddings and semantic retrieval |
| Future Analytics | dbt + ClickHouse | Dimensional models and heavy analytics |

<hr/>

## Repository Structure

```text
.
|-- api/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- repositories/
|   |   |-- schemas/
|   |   `-- services/
|   |-- Dockerfile
|   `-- requirements.txt
|-- pipelines/
|   |-- connectors/
|   |-- flows/
|   |-- normalizers/
|   |-- Dockerfile
|   `-- requirements.txt
|-- sql/
|   `-- init.sql
|-- tests/
|   `-- test_normalizers.py
|-- docker-compose.yml
|-- CONTRIBUTING.md
|-- LICENSE
`-- .env.example
```

<hr/>

## Data Model

<table>
  <tr>
    <td width="50%">
      <h3><code>job_postings</code></h3>
      <p>Canonical current-state table for the latest known version of each posting.</p>
      <ul>
        <li>Powers the API</li>
        <li>Represents active records</li>
        <li>Keeps normalized fields</li>
        <li>Tracks first and last seen timestamps</li>
      </ul>
    </td>
    <td width="50%">
      <h3><code>job_snapshots</code></h3>
      <p>Append-only historical observations stored over time.</p>
      <ul>
        <li>Enables trend analysis</li>
        <li>Supports auditability</li>
        <li>Allows historical comparisons</li>
        <li>Preserves raw and normalized payloads</li>
      </ul>
    </td>
  </tr>
</table>

<hr/>

## Use cases

This repository can grow into:

- a recruiting intelligence SaaS
- a labor market analytics dashboard
- a salary insights engine
- a structured jobs API
- an AI-ready recruiting data layer
- a semantic search backend for job discovery

<hr/>

## Legal-first strategy

### Preferred sources

- Greenhouse Job Board API
- Lever Postings API
- Ashby public endpoints when available
- public careers pages
- open labor datasets
- internal enrichment on top of legally collected data

### Not the initial priority

- aggressive LinkedIn scraping
- aggressive Indeed scraping
- high-maintenance anti-bot flows

### Why this matters

- lower operational friction
- lower maintenance cost
- better production durability
- stronger long-term platform design

<hr/>

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/bentancourtfiorellanahir-bot/job-market-intelligence.git
cd job-market-intelligence
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Run the ingestion flow

```bash
docker compose run --rm pipelines python -m flows.ingest_greenhouse
```

### 5. Explore the API

- `http://localhost:8000/health`
- `http://localhost:8000/docs`
- `GET /v1/jobs`

### 6. Run basic checks

```bash
python -m unittest discover -s tests -p "test_*.py"
```

<hr/>

## Repository health

The repository now includes:

- CI workflow for lint, compile, and test checks
- issue templates
- contribution guide
- MIT license
- editor configuration
- a smoke-test suite for normalization logic

<hr/>

## Roadmap

### Phase 1 | Serious MVP

- [x] ingest jobs
- [x] normalize records
- [x] store historical snapshots
- [x] expose a simple API
- [ ] add dashboard layer

### Phase 2 | Intelligence

- [ ] skill extraction
- [ ] salary normalization
- [ ] remote classification
- [ ] seniority detection improvements
- [ ] trend analysis

### Phase 3 | AI Layer

- [ ] embeddings
- [ ] semantic search
- [ ] market report generation
- [ ] hiring trend prediction

<hr/>

## Project direction

<table>
  <tr>
    <td width="50%">
      <h3>What it is today</h3>
      <ul>
        <li>A clean MVP</li>
        <li>A structured ingestion platform</li>
        <li>An analytics-ready backend</li>
        <li>A strong portfolio project</li>
      </ul>
    </td>
    <td width="50%">
      <h3>What it can become</h3>
      <ul>
        <li>A productized market-intelligence platform</li>
        <li>A search and insights API</li>
        <li>A recruiting analytics engine</li>
        <li>An AI-assisted labor market system</li>
      </ul>
    </td>
  </tr>
</table>

<hr/>

## Status

This is an **active MVP foundation** with a clear direction:

- practical
- extensible
- analytics-ready
- portfolio-strong
- aligned with real-world data engineering work
