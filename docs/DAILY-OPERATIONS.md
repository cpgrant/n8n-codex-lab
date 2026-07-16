# Daily operations

## Start

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/start.sh
scripts/agent-start.sh
```

Run `scripts/agent-start.sh` in its own terminal because FastAPI remains in the
foreground. Both startup scripts automatically load the ignored `.env`.
`scripts/start.sh` supplies the distinct Stage 9.1 tokens to n8n, and
`scripts/agent-start.sh` supplies them to FastAPI. Missing, short, or identical
tokens stop startup safely.

In another terminal:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/status.sh
scripts/agent-check.sh
codex mcp list
```

For workflow work, use only names beginning `CODEX TEST`. Keep AI Strategy
Factory inactive and unpublished, and submit only synthetic data. The temporary
`/form-test/...` URL exists only while an editor test execution is listening.
The form requires the user to be signed in to n8n.

## Verify current milestones

```bash
scripts/verify-stage4.sh
node scripts/verify-stage8-intake.js
node scripts/verify-stage9-5-lite.js
cd agent-service && .venv/bin/pytest tests -q
```

Track B-Q1 strategy-quality regression cases are stored in
`examples/quality-objective-measure-cases.synthetic.json`. The full service
suite validates their deterministic findings and the enhanced approved
Markdown artifact. Live Ollama verification evidence is recorded in
`docs/TRACK-B-Q1-VERIFICATION.md`.

## Track B baseline

After n8n, Ollama, and FastAPI are running with the repository `.env` set to
`AI_FACTORY_PROVIDER=ollama` and `AI_FACTORY_QUALITY_MODE=pro`, run:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/verify-track-b-baseline.sh
```

The verifier performs service-health, workflow-safety, flexible-intake,
Stage 9.5-lite workflow-contract, test-suite, and one live synthetic Ollama
generation/quality check. The live check can take several minutes. It writes an
ignored Markdown report under
`artifacts/evaluations/track-b/` and detailed ignored logs under `tmp/`.

It does not start or stop services, activate or publish the workflow, delete
data, or print authentication tokens. After it passes, perform one manual
synthetic n8n form walkthrough to record the current browser experience before
implementing Stage 9.5-lite.

## Recover a strategy run

After the workflow displays a run ID, the draft exists independently of the
temporary browser form. Check its safe status and artifact locations with:

```bash
scripts/strategy-run-status.sh <run-id>
```

The command automatically loads the ignored `.env`, authenticates to FastAPI,
and prints only status and service-owned repository-relative artifact paths. It
does not print the brief, strategy content, prompts, or token values. Do not
create another run merely because a form tab closed after a run ID appeared.

## Shut down

Stop FastAPI with `Ctrl-C` in its terminal, then:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/stop.sh
```

This stops the repository-managed Ollama process and local n8n stack. It does
not delete SQLite data or artifacts.
