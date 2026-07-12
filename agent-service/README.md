# AI Strategy Factory service

Stage 2 provides the local FastAPI and SQLite strategy-generation slice. It
exposes health plus create/read run endpoints backed by the deterministic fake
provider. Review, artifacts, real model calls, and n8n integration are later
stages.

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

The service listens on `http://127.0.0.1:8000`. The future n8n workflow, running
inside Docker Desktop, will use `http://host.docker.internal:8000`.

## Verify

```bash
scripts/agent-check.sh
cd agent-service
uv run pytest
```

With the service running, execute the synthetic Stage 2 API smoke test:

```bash
scripts/agent-smoke-stage2.sh
```

Runtime SQLite files are written beneath `AI_FACTORY_DATA_DIR` and ignored by
Git. Use synthetic data only.
