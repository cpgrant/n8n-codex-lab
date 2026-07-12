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

The host-side URL is `http://127.0.0.1:8000`. A future n8n HTTP Request node
will use `http://host.docker.internal:8000` because n8n runs in Docker Desktop.
