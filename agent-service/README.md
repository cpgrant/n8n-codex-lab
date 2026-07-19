# AI Strategy Factory service

The local FastAPI service exposes health, create/read runs, approval/rejection,
and approved Markdown retrieval. PostgreSQL is the active local database;
SQLite is retained as the verified rollback path. Generation supports the
deterministic fake provider and the opt-in local Ollama provider.

## Setup on macOS

From this directory:

```bash
uv sync --extra dev
```

## Run

From the repository root:

```bash
scripts/agent-start.sh
```

The service listens on `http://127.0.0.1:8000`. The n8n workflow, running inside
Docker Desktop, uses `http://host.docker.internal:8000`.

Platform P1.1-P1.5 provides portable SQLAlchemy repositories, Alembic
migrations, a dual-backend verification matrix, migration/recovery tooling,
and a completed synthetic PostgreSQL cutover. Normal repository startup uses
the ignored `AI_FACTORY_DEFAULT_DATABASE` selection and never migrates data
automatically. The unchanged SQLite file remains available for rollback. See
`../docs/POSTGRESQL-MIGRATION-RUNBOOK.md`.

Stage 9.1 requires two distinct environment-backed tokens of at least 32
characters. Store them in the repository's ignored `.env`; the startup scripts
load and validate that file automatically:

```bash
scripts/start.sh
scripts/agent-start.sh
```

`scripts/start.sh` injects the same values into n8n through the repository-owned
Compose override. Do not store them in workflow JSON, Git, n8n variables
intended for non-secret data, or shell history. The workflow uses n8n User Auth
for human form access and sends only the authenticated user's opaque ID to the
review API.

## Verify

```bash
scripts/agent-check.sh
cd agent-service
uv run pytest
```

With the tokens loaded in the verification shell, execute the synthetic Stage
2 API smoke test:

```bash
scripts/agent-smoke-stage2.sh
```

Execute the synthetic Stage 3 approval and artifact smoke test:

```bash
scripts/agent-smoke-stage3.sh
```

Runtime SQLite files are written beneath `AI_FACTORY_DATA_DIR` and ignored by
Git. Use synthetic data only.

## Ollama provider

Start n8n and repository-managed Ollama:

```bash
scripts/start.sh
```

Stop any existing fake-provider FastAPI process, then start the service with
the local model explicitly selected:

```bash
AI_FACTORY_PROVIDER=ollama \
OLLAMA_BASE_URL=http://127.0.0.1:11888 \
OLLAMA_MODEL=gemma4:31b \
OLLAMA_TIMEOUT_SECONDS=300 \
scripts/agent-start.sh
```

In another terminal, run the opt-in live smoke test:

```bash
scripts/agent-smoke-stage6-ollama.sh
```

The normal Python test suite never calls Ollama. `fake` remains the default.

## Stage 7 quality report

Quality reports are generated separately from strategy drafts and remain
advisory. `basic` mode runs deterministic checks. `pro` adds a separate Ollama
critic call:

```bash
AI_FACTORY_PROVIDER=ollama \
AI_FACTORY_QUALITY_MODE=pro \
OLLAMA_QUALITY_MODEL=gemma4:31b \
scripts/agent-start.sh
```

Verify with synthetic data:

```bash
EXPECTED_QUALITY_MODE=pro scripts/agent-smoke-stage7.sh
```
Each quality report is also written atomically as
`artifacts/quality-reports/quality-report-<run_id>.md` and can be retrieved at
`GET /v1/strategy-runs/<run_id>/quality-report/artifact`. It remains advisory
and distinct from the approved strategy artifact.

## Stage 7.1 local model evaluation

Benchmark the installed local candidates with the checked-in synthetic brief:

```bash
agent-service/.venv/bin/python scripts/evaluate-stage7-1.py
```

Results and the blinded human-review packet are written below
`artifacts/evaluations/stage-7.1/`. See
`docs/STAGE-7.1-VERIFICATION.md` for the review and finalization procedure.
