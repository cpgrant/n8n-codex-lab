# SETUP

## Startup

Open the project:

```bash
cd ~/Development/codex/n8n-codex-lab
code .
codex mcp list
```

Keep secrets only in the ignored `.env`; never copy the real token into
`.env.example`, documentation, or Git.

Stage 9.1 requires distinct `AI_FACTORY_SERVICE_TOKEN` and
`AI_FACTORY_REVIEW_TOKEN` values of at least 32 characters. Put them in the
ignored repository `.env`. Never place them in workflow JSON or n8n variables
intended for non-secret data. Optional expiry variables are documented in
`.env.example`. See `docs/AUTHENTICATION-TOKENS.md` for generation, expiration,
startup, and rotation instructions.

The repository startup script starts n8n and a repository-managed Ollama
server on port `11888`:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/start.sh
curl -fsS http://127.0.0.1:11888/api/tags | jq
```

`scripts/start.sh` loads `.env`, validates both tokens, and passes them to n8n
through the repository-owned `compose.n8n-auth.yml` override. It fails before
starting services when authentication configuration is missing or invalid.
Explicit environment values take precedence over matching `.env` entries.

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

`scripts/agent-start.sh` loads the same ignored `.env` and validates both Stage
9.1 tokens. Missing or invalid configuration stops startup instead of running a
partially configured API. Explicit environment values take precedence over
matching `.env` entries. The synthetic smoke scripts also require the tokens.

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

The Form Trigger requires a signed-in n8n user. `scripts/start.sh` supplies the
Stage 9.1 token variables to n8n. Later form pages inherit n8n User Auth, and
reviewer identity is taken from the authenticated user's opaque ID rather than
an editable field.

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

Stage 8 replaces the formerly prefilled first page with an intake-mode chooser.
Choose **Load synthetic example** for the fast path, **Enter a blank manual
form** for synthetic manual entry, or **Upload structured JSON** for one
synthetic `.json` object up to 64 KiB.

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

For a customized synthetic brief, create an ignored working copy and select
**Upload structured JSON**:

```bash
cp examples/strategy-brief.synthetic.json tmp/company-brief.synthetic.json
code tmp/company-brief.synthetic.json
```

The built-in **Load synthetic example** payload is embedded in the workflow and
does not change when the source example file is edited. Real or confidential
data remains prohibited until Stage 9.

Each quality call also writes an advisory Markdown copy to
`artifacts/quality-reports/quality-report-<run_id>.md`. Retrieve it through
`GET /v1/strategy-runs/<run_id>/quality-report/artifact`. It is not an approved
strategy artifact and is created before the review decision.

The host-side URL is `http://127.0.0.1:8000`. n8n uses
`http://host.docker.internal:8000` because it runs in Docker Desktop.
