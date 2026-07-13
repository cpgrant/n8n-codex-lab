# SETUP

## Startup
```bash
cd ~/Development/docker/n8n
docker compose up -d
docker compose ps
docker exec -it n8n n8n --version
docker exec -it n8n ffmpeg -version
```

Start project:
```bash
cd ~/Development/codex/n8n-codex-lab
code .
export N8N_MCP_TOKEN='YOUR_TOKEN'
codex mcp list
```

The repository startup script starts n8n and a repository-managed Ollama
server on port `11888`:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/start.sh
curl -fsS http://127.0.0.1:11888/api/tags | jq
```

It is safe to run `scripts/start.sh` again when Ollama is already healthy. The
matching `scripts/stop.sh` stops only the Ollama PID started and recorded by
this repository, then stops n8n. Logs and the PID file are stored under the
Git-ignored `tmp/` directory.

## Stage 1 agent service

Install the isolated development environment:

```bash
cd ~/Development/codex/n8n-codex-lab/agent-service
uv sync --extra dev
```

Start the service directly on the Mac:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/agent-start.sh
```

In another terminal, verify it:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/agent-check.sh
```

Run the tests:

```bash
cd ~/Development/codex/n8n-codex-lab/agent-service
uv run pytest
```

With the service running, verify the Stage 2 create/read path using only the
checked-in synthetic brief:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/agent-smoke-stage2.sh
```

Verify Stage 3 approval, durable review state, Markdown generation, and artifact
retrieval using only synthetic data:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/agent-smoke-stage3.sh
```

## Stage 4 n8n workflow

Start Docker Desktop and n8n, then keep the agent service running on the Mac.
Verify both network paths:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/verify-stage4.sh
```

Import `workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json` into n8n as an
inactive workflow. Use the editor's test form URL for synthetic manual testing.
Do not activate or publish the workflow without explicit approval.

## Stage 5 operational verification

With Docker Desktop, n8n, and the Mac-local agent service running, execute:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/verify-stage5.sh
```

The script verifies Stage 4 safety/connectivity plus create and review
idempotency, rejection semantics, durable retrieval, and the absence of an
artifact for a rejected synthetic run. Follow the restart-persistence procedure
in `docs/STAGE-5-VERIFICATION.md` to confirm the same run remains available
after restarting FastAPI.

The n8n `/form-test/...` URL is temporary. If it expires during manual entry,
click **Execute workflow** again and use the newly opened form. Do not publish
the workflow merely to avoid the test-listener timeout without making that
separate operational decision explicitly.

## Stage 6 Ollama strategy generation

Ensure `scripts/start.sh` has made Ollama available at port `11888`. Stop the
currently running fake-provider FastAPI process with `Ctrl-C`, then start it in
Ollama mode:

```bash
cd ~/Development/codex/n8n-codex-lab
AI_FACTORY_PROVIDER=ollama \
OLLAMA_BASE_URL=http://127.0.0.1:11888 \
OLLAMA_MODEL=gemma4:31b \
OLLAMA_TIMEOUT_SECONDS=300 \
scripts/agent-start.sh
```

In a second terminal:

```bash
scripts/agent-smoke-stage6-ollama.sh
```

The first `gemma4:31b` request may be slow while the model loads. To return to
deterministic operation, restart FastAPI without `AI_FACTORY_PROVIDER=ollama`.
The n8n workflow requires no modification and remains inactive/unpublished.

The Stage 6.1 exported workflow prefills every form field with
`examples/strategy-brief.synthetic.json`. This avoids hurried manual entry on
the temporary test URL while still allowing each value to be overwritten with
other synthetic data.

## Stage 7 quality report

`basic` mode is the default and requires no additional model call:

```bash
AI_FACTORY_QUALITY_MODE=basic scripts/agent-start.sh
```

For a separate Ollama critique after generation:

```bash
AI_FACTORY_PROVIDER=ollama \
AI_FACTORY_QUALITY_MODE=pro \
OLLAMA_BASE_URL=http://127.0.0.1:11888 \
OLLAMA_MODEL=gemma4:31b \
OLLAMA_QUALITY_MODEL=gemma4:31b \
OLLAMA_TIMEOUT_SECONDS=300 \
scripts/agent-start.sh
```

Run the synthetic verification in another terminal:

```bash
EXPECTED_QUALITY_MODE=pro scripts/agent-smoke-stage7.sh
```

The exported `CODEX TEST — AI Strategy Factory v0.1` workflow calls the quality
endpoint and displays its advisory findings before the human decision. Keep the
workflow inactive and unpublished.

Stage 8 begins with an intake-mode page. The example branch is fastest; the
manual branch is intentionally blank; and the JSON branch accepts one
synthetic `.json` brief up to 64 KiB. Uploaded data must satisfy the same strict
API schema and is not retained as a file by the workflow.

Each quality call also writes an advisory Markdown copy to
`artifacts/quality-reports/quality-report-<run_id>.md`. Retrieve it through
`GET /v1/strategy-runs/<run_id>/quality-report/artifact`. It is not an approved
strategy artifact and is created before the review decision.

The host-side URL is `http://127.0.0.1:8000`. n8n uses
`http://host.docker.internal:8000` because it runs in Docker Desktop.
