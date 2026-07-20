# Documentation freshness audit

Audit date: **2026-07-20**

## Scope

This audit compared the judge-facing, setup, operational, architecture, product,
environment, migration, security, workflow, and video documentation with the
current repository configuration and executable evidence. It focused on stale
status claims, dependency versions, backend selection, provider availability,
paths, commands, workflow safety boundaries, and public demonstration links.

Historical stage-verification records were treated as point-in-time evidence.
They were not rewritten merely because later stages changed the current system.

## Sources of truth checked

| Subject | Repository source of truth |
| --- | --- |
| n8n version | `Dockerfile.n8n` (`n8nio/n8n:2.29.10`) |
| PostgreSQL version | `compose.postgres.yml` (`postgres:18.4-bookworm`) |
| FastAPI and Uvicorn | `agent-service/uv.lock` (`0.139.0` and `0.51.0`) |
| Provider and model defaults | `.env.example` (`fake`, `gemma4:31b`) |
| Active database selection | startup scripts, `.env.example`, migration and P1.5 records |
| Workflow name and inactive state | `workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json` |
| Verification commands | repository scripts and `docs/DAILY-OPERATIONS.md` |
| Public demonstration | `https://www.youtube.com/watch?v=QKJJM996nmI` |
| Installed local CLI versions | direct `--version` commands on 2026-07-20 |

## Findings and disposition

| Finding | Severity | Resolution |
| --- | --- | --- |
| The product contract said the Python service and provider were future work | High | Updated `docs/AI-STRATEGY-FACTORY.md` to describe the implemented FastAPI service and fake/Ollama providers |
| The same contract listed PostgreSQL as a current non-goal and described SQLite as the normal data path | High | Marked the early stages as historical, documented PostgreSQL as active, and retained SQLite only as the controlled rollback path |
| Authentication-dependent idempotency text still said “when authentication is introduced” | Medium | Updated it to the implemented authenticated-caller behavior |
| Current environment and quality-report text still reflected the 16-node/SQLite checkpoint | Medium | Updated the current workflow metric to 20 nodes and current persistence wording to the active PostgreSQL-backed repository; retained dated checkpoint figures |
| The tested-environment record listed Codex CLI `0.139.0` | Low | Updated `docs/ENVIRONMENT.md` to the installed `0.144.6` |
| The public video URL appeared repeatedly within judge-facing files | Medium | Consolidated each document around a `demo-video` reference and added a replacement checklist to the video README |
| Historical verification files describe SQLite or opt-in PostgreSQL at earlier checkpoints | None | Preserved as dated stage evidence; their historical context is accurate |
| The local Ollama service was not running during the audit | Operational note | No documentation change required; the installed client reports `0.32.1`, and startup guidance already covers the service |

## Confirmed current claims

- AI Strategy Factory remains synthetic-data-only.
- The checked-in n8n workflow remains a `CODEX TEST` workflow and must stay
  inactive and unpublished unless explicitly approved.
- PostgreSQL is the normal local FastAPI backend; SQLite is retained as the
  verified rollback snapshot.
- The runtime provider boundary supports deterministic fake generation and
  opt-in local Ollama generation.
- Human approval remains required before creation of the approved Markdown
  artifact.
- Judge entry points consistently reference the current public narrated video.
- The setup guide's pinned n8n, PostgreSQL, FastAPI, and Uvicorn versions match
  the repository source files.

## Audit commands

Representative read-only checks:

```bash
rg -n "later implementation|will own|SQLite|PostgreSQL|gemma4|youtube.com" README.md docs agent-service/README.md ai-strategy-factory-video/README.md
codex --version
ollama --version
uv --version
jq --version
python3 --version
git diff --check
```

For a live service audit, start the configured system and use the health and
milestone checks in `docs/JUDGE-GUIDE.md`. This audit did not activate or
publish a workflow and did not use real client data.
