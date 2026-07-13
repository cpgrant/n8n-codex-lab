# AI Strategy Factory service

The local FastAPI and SQLite service exposes health, create/read runs,
approval/rejection, and approved Markdown retrieval. Generation supports the
deterministic fake provider and the opt-in local Ollama provider introduced in
Stage 6.

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
