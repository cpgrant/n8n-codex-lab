# AI Strategy Factory

AI Strategy Factory is a local, synthetic-data strategy workflow built with
Codex, n8n, MCP, FastAPI, PostgreSQL, Ollama, and Docker. The repository retains
the technical name `n8n-codex-lab`.

> **Public code repository:**
> <https://github.com/cpgrant/n8n-codex-lab>

## How Codex and GPT-5.6 were used

**Codex powered by GPT-5.6 was the development collaborator for this project.**
It worked directly against the repository and local development environment,
while the human developer set the product direction, approved changes, made
architecture and safety decisions, and performed the final workflow reviews.

Codex and GPT-5.6 were used to:

- turn the AI Strategy Factory concept into an incremental implementation plan
  and maintain the project roadmap;
- design, inspect, and safely export the inactive `CODEX TEST` n8n workflow;
- implement and refactor the FastAPI service, schemas, lifecycle rules,
  authentication boundaries, quality checks, artifacts, and provider adapters;
- build the SQLite-to-PostgreSQL portability layer, Alembic migration,
  reconciliation, backup, restore, and rollback tooling;
- create repository-owned Docker Compose configuration and operational scripts
  for n8n, PostgreSQL, Ollama, and FastAPI;
- generate synthetic test fixtures and expand unit, API, integration,
  idempotency, concurrency, workflow-contract, and recovery tests;
- diagnose failures from local logs and test output, then verify each change
  before it was committed; and
- write and maintain the setup, architecture, API, security, operations, and
  verification documentation, including the project infographic.

The collaboration remained human-controlled: Codex explained planned changes
before applying them, used synthetic data only, preserved credentials, and did
not activate or publish the n8n workflow. The checked-in `AGENTS.md` records
these operating constraints.

GPT-5.6 is part of the **development process**, not a hidden runtime dependency.
The submitted application runs locally and uses the configured Ollama model for
strategy generation and optional critique; deterministic tests use the fake
provider.

The lab is evolving incrementally into a lightweight AI Factory Platform. AI
Strategy Factory v0.1 is the first reference factory and now includes the
Mac-local FastAPI service with PostgreSQL persistence, local Ollama generation, advisory quality
reports and Markdown copies, explicit human review, approved strategy
artifacts, Stage 8 flexible synthetic intake, and Stage 9.1 human/service
authentication.

The confirmed portfolio direction includes Strategy, Podcast, and Job
Application factories. Research and Briefing and Content Repurposing are
candidate ideas. Only Strategy is implemented; the others remain planned or
proposed synthetic vertical slices. See `docs/AI-FACTORY-PLATFORM.md` for the
platform objective, shared lifecycle, boundaries, and recommended sequence.

The inactive `CODEX TEST — AI Strategy Factory v0.1` workflow offers a
checked-in synthetic example, a genuinely blank manual form, and a size-limited
structured JSON upload. It must remain inactive and unpublished unless
activation is approved explicitly. Real or confidential client data remains
out of scope until the Stage 9 controls exist.

Current roadmap status:

- Stages 0-7.0.1 and Stage 8 are complete;
- Stage 7.1 benchmarking is implemented, with blind human preference deferred;
- Stages 9.0 and 9.1 complete the local synthetic-lab security baseline. The
  roadmap is now at a decision gate: local usability, housekeeping, and product
  quality are recommended next, while Stages 9.2-9.6 remain available as the
  pilot-gated operationalization track;
- Platform P1.0-P1.5 PostgreSQL portability and cutover are complete.
  PostgreSQL is the active local FastAPI backend; the unchanged SQLite file is
  retained as the verified rollback snapshot.

See:

- `docs/SETUP.md` — canonical clean-machine installation and verification
- `docs/AI-FACTORY-PLATFORM.md`
- `docs/ROADMAP.md`
- `docs/Professional-n8n-Codex-Lab-Manual.md`
- `docs/AI-STRATEGY-FACTORY.md`
- `docs/API.md`
- `docs/STAGE-8-VERIFICATION.md`
- `docs/STAGE-9.0-DATA-POLICY.md`
- `docs/STAGE-9.0-VERIFICATION.md`
- `docs/STAGE-9.1-AUTH-DESIGN.md`
- `docs/STAGE-9.1-VERIFICATION.md`
- `docs/AUTHENTICATION-TOKENS.md`
- `docs/POSTGRESQL-MIGRATION-PLAN.md`
- `docs/POSTGRESQL-P1.1-VERIFICATION.md`
- `docs/POSTGRESQL-P1.2-VERIFICATION.md`
- `docs/POSTGRESQL-P1.3-VERIFICATION.md`
- `docs/POSTGRESQL-P1.4-VERIFICATION.md`
- `docs/POSTGRESQL-P1.5-VERIFICATION.md`
- `docs/POSTGRESQL-MIGRATION-RUNBOOK.md`
- `agent-service/README.md`

## Local PostgreSQL database

PostgreSQL is the active local FastAPI database after the completed P1.5
cutover. The unchanged SQLite database remains a verified rollback snapshot;
n8n continues to use its own separate persistence.

1. Add a new, distinct secret to the ignored `.env`:

   ```text
   AI_FACTORY_POSTGRES_PASSWORD=<output of openssl rand -hex 32>
   ```

2. Start and verify PostgreSQL:

   ```bash
   scripts/postgres-start.sh
   ```

3. Inspect or stop it without deleting its data volume:

   ```bash
   scripts/postgres-status.sh
   scripts/postgres-stop.sh
   ```

The container listens only on `127.0.0.1:5432`, uses the pinned
`postgres:18.4-bookworm` image, and stores database files in the Docker named
volume `codex_test_ai_factory_postgres_data`. Do not use Docker Compose with
the `down --volumes` option for routine shutdown because that removes the
database volume.

Migration and recovery commands are intentionally separate from normal
startup. Review `docs/POSTGRESQL-MIGRATION-RUNBOOK.md` before using them. The
dry run does not write application rows, an import requires an explicit
`--confirm-empty-target`, and PostgreSQL backups never overwrite an existing
file.

After the P1.5 gate, normal `scripts/agent-start.sh` startup uses
`AI_FACTORY_DEFAULT_DATABASE=postgresql` from the ignored `.env`. Set that
value to `sqlite` for a controlled rollback; do not delete either database.

For normal Mac startup, one command handles Docker Desktop readiness and the
service order:

```bash
scripts/system-start.sh
```

It starts Docker Desktop if needed, PostgreSQL, n8n, Ollama, and then FastAPI.
The manual equivalent is `open -a Docker`, followed by
`scripts/postgres-start.sh`, `scripts/start.sh`, and
`scripts/agent-start.sh` after Docker is ready.
