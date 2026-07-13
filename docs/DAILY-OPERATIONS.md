# Daily operations

## Start

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/start.sh
set -a
source .env
set +a
scripts/agent-start.sh
```

Run `scripts/agent-start.sh` in its own terminal because FastAPI remains in the
foreground. The ignored `.env` selects the local provider and quality mode.

In another terminal:

```bash
cd ~/Development/codex/n8n-codex-lab
set -a
source .env
set +a
scripts/status.sh
scripts/agent-check.sh
codex mcp list
```

For workflow work, use only names beginning `CODEX TEST`. Keep AI Strategy
Factory inactive and unpublished, and submit only synthetic data. The temporary
`/form-test/...` URL exists only while an editor test execution is listening.

## Verify current milestones

```bash
scripts/verify-stage4.sh
node scripts/verify-stage8-intake.js
cd agent-service && .venv/bin/pytest tests -q
```

## Shut down

Stop FastAPI with `Ctrl-C` in its terminal, then:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/stop.sh
```

This stops the repository-managed Ollama process and local n8n stack. It does
not delete SQLite data or artifacts.
