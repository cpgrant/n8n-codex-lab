# TROUBLESHOOTING

- Docker 429: use FROM n8nio/n8n:latest
- Verify `codex mcp list`
- Verify `echo ${N8N_MCP_TOKEN:+TOKEN_IS_SET}`

## Token is not exported

Load the ignored repository environment in the current shell:

```bash
set -a
source .env
set +a
echo ${N8N_MCP_TOKEN:+TOKEN_IS_SET}
```

Restart any process that must inherit changed environment variables. Never
print or commit the token itself.

## Form URL returns 404 or submission expires

The workflow is intentionally inactive, so `/form/...` returns 404. Click
**Execute workflow** in n8n and use the current `/form-test/...` URL. Start a
new test execution if its listener expires.

## Stage 8 JSON upload is rejected

Confirm there is exactly one `.json` file no larger than 65,536 bytes, its root
is an object, it follows `examples/strategy-brief.synthetic.json`, and it has no
unknown fields. Arrays, YAML, multiple files, and non-synthetic data are not
accepted.

## FastAPI or Ollama is unavailable

```bash
scripts/status.sh
scripts/agent-check.sh
curl -fsS http://127.0.0.1:11888/api/tags | jq
```

n8n reaches FastAPI at `http://host.docker.internal:8000`; host-side commands
use `http://127.0.0.1:8000`.
