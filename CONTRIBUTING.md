# Contributing

Thanks for contributing to this project.

## Development principles

- Keep source connectors modular and source-specific.
- Preserve raw payloads whenever possible.
- Normalize into shared internal schemas.
- Prefer legal-first and reproducible ingestion patterns.
- Avoid mixing source-specific parsing into the API layer.

## Local setup

1. Copy `.env.example` to `.env`.
2. Start the stack with `docker compose up --build`.
3. Run the Greenhouse ingestion flow with:

```bash
docker compose run --rm pipelines python -m flows.ingest_greenhouse
```

## Suggested validation

- Confirm `http://localhost:8000/health` returns `ok`.
- Confirm `http://localhost:8000/docs` loads.
- Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Pull request expectations

- Keep changes focused and minimal.
- Update documentation when behavior changes.
- Add or update tests for logic changes.
- Do not commit secrets or populated `.env` files.
