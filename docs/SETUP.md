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

The host-side URL is `http://127.0.0.1:8000`. A future n8n HTTP Request node
will use `http://host.docker.internal:8000` because n8n runs in Docker Desktop.
