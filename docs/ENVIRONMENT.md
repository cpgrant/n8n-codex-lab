
# Tested Environment

- macOS

- Docker Desktop

- n8n 2.29.10

- FFmpeg 7.1

- Codex CLI 0.139.0

- MCP URL: http://localhost:5678/mcp-server/http

- n8n Docker directory: ~/Development/docker/n8n

- Codex lab directory: ~/Development/codex/n8n-codex-lab

- Python: 3.11+

- Python project runner: uv

- AI Factory host URL: http://127.0.0.1:8000

- AI Factory URL from n8n Docker: http://host.docker.internal:8000

- AI Factory persistence: local SQLite under `data/`

- n8n-to-Mac agent URL: http://host.docker.internal:8000

- AI Strategy Factory workflow: 16-node Stage 8 export, inactive and unpublished

- Workflow MCP availability: disabled

- Workflow execution-data persistence: production success/error disabled;
  manual enabled for n8n 2.29 multi-page form tests

- Stage 9.3-lite n8n retention: rolling pruning enabled, 336-hour maximum age,
  500-execution cap; stale waiting `CODEX TEST` runs audited after 24 hours

- Stage 9.3-lite factory backups: ignored local
  `backups/ai-strategy-factory/`, SHA-256 manifest, SQLite integrity check, and
  temporary restore test

- Ollama host URL: http://127.0.0.1:11888

- Stage 6 Ollama model: `gemma4:31b`

- Stage 7 quality mode default: `basic`

- Stage 7 pro critic model: `gemma4:31b`

- Stage 8 intake: synthetic example, blank manual form, or JSON up to 64 KiB

- Stage 7.1 candidates installed: `gemma4:12b`, `gemma4:26b`, `gemma4:31b`

- Stage 7.1 model preference: human review pending; current baseline unchanged

- Stage 9.1 human authentication: n8n User Auth on Form Trigger v2.6

- Stage 9.1 API authentication: distinct environment-backed service and review
  bearer tokens; no tokens stored in the workflow export

- Stage 9.1 authorization boundary: service operations and human review use
  separate scopes; run ownership/tenant isolation remains pending Stage 9.2
