# TROUBLESHOOTING

- Docker 429: use FROM n8nio/n8n:latest
- Verify `codex mcp list`
- Verify `echo ${N8N_MCP_TOKEN:+TOKEN_IS_SET}`

## Codex MCP token is not exported

This check is specifically for `N8N_MCP_TOKEN`. Load the ignored repository
environment in the current shell:

```bash
set -a
source .env
set +a
echo ${N8N_MCP_TOKEN:+TOKEN_IS_SET}
```

Restart any process that must inherit changed environment variables. Never
print or commit the token itself. For the separate Stage 9.1 service and review
tokens, follow `docs/AUTHENTICATION-TOKENS.md`; the repository startup scripts
load those values automatically.

## Form URL returns 404 or submission expires

The workflow is intentionally inactive, so `/form/...` returns 404. Click
**Execute workflow** in n8n and use the current `/form-test/...` URL. Start a
new test execution if its listener expires.

Stage 9.5-lite distinguishes recovery before and after a run ID exists:

- before a run ID appears, a closed or expired test form has no durable run to
  resume; return to n8n, click **Execute workflow**, and start one new synthetic
  run;
- after a run ID appears, do not create another run automatically. The draft
  is already stored in SQLite. From the repository, run:

```bash
scripts/strategy-run-status.sh <run-id>
```

An `awaiting_review` run without a quality-report path needs the quality step.
An `awaiting_review` run with a quality-report path needs human review. An
`artifact_created` run is complete. Rejection is terminal. Full browser-session
resumption and background polling remain outside the Stage 9.5-lite scope.

## Form reports a problem submitting the response

Check recent n8n logs without printing environment values:

```bash
docker logs --since 10m --tail 300 n8n
```

If the log contains `access to env vars denied`, restart n8n with
`scripts/start.sh`. The repository-owned Compose override explicitly enables
the `$env` expressions required for the service and review tokens. This access
is limited by policy to the local synthetic lab; see `docs/SECURITY.md`.

For n8n 2.29 multi-page test forms, **Save manual executions** must remain
enabled so the form can poll and resume its waiting execution. Keep production
success/error saving disabled, keep the workflow inactive and unpublished, and
submit synthetic data only. The local operator may delete completed manual
test executions from n8n's **Executions** view after verification evidence is
recorded and the trace is no longer needed.

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

If a slow request fails, copy any displayed run ID before retrying. Check that
ID with `scripts/strategy-run-status.sh` first. The workflow uses a 330-second
n8n timeout for both generation and quality critique. Do not repeatedly submit
the form while its spinner is active.
