# n8n Codex Lab

Purpose: AI-assisted workflow engineering using Codex, n8n, MCP, Docker and Git.

The lab is evolving incrementally into a lightweight AI Factory Platform. AI
Strategy Factory v0.1 is the first reference factory and now includes the
Mac-local FastAPI/SQLite service, local Ollama generation, advisory quality
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

## Optional local PostgreSQL container

PostgreSQL can run as an isolated, optional database alongside the current
SQLite-backed factory. Installing the container does not switch FastAPI away
from SQLite and does not migrate n8n.

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
