# AI Strategy Factory

AI Strategy Factory is a local, synthetic-data strategy workflow built with
Codex, n8n, MCP, FastAPI, PostgreSQL, Ollama, and Docker. The repository retains
the technical name `n8n-codex-lab`.

> **Public code repository:**
> <https://github.com/cpgrant/n8n-codex-lab>

## What I built, and how I used Codex and GPT-5.6

I built **AI Strategy Factory**, a local-first, human-in-the-loop system that
turns a structured strategy brief into an AI-generated draft, evaluates its
quality, presents it for explicit human review, and creates an immutable
Markdown artifact only after approval. The solution combines an inactive n8n
workflow, a Python/FastAPI application service, PostgreSQL persistence, local
Ollama inference, Docker-managed infrastructure, authentication boundaries,
and a reproducible test and operations layer.

I used **Codex powered by GPT-5.6 as the development collaborator across the
entire repository**. I supplied the product intent, constraints, priorities,
approval decisions, and final review. Codex used GPT-5.6 to reason about the
repository, propose scoped changes, write and edit files, run commands and
tests, inspect failures, compare results, and iteratively improve the solution.

Rather than using Codex as a single assistant in a single chat, I used a
**coordinated virtual engineering crew across multiple Codex surfaces**:

- **Codex in the VS Code IDE extension** worked closest to the source code for
  repository inspection, implementation, refactoring, testing, and debugging.
- **Codex in ChatGPT on the web** supported longer-running planning, research,
  review, and parallel work away from the local editor.
- **Codex in the ChatGPT desktop app on macOS** provided a workspace-oriented
  environment for coordinating repository work, reviewing changes, operating
  local tools, and producing supporting assets such as the summary video.

These were different working surfaces for the same human-directed development
effort. I coordinated their tasks, supplied repository context and durable
instructions, reviewed their output, and decided what entered the codebase.
They should be understood as a virtual crew of Codex collaborators, not as
independent human contributors or an autonomous software team.

That collaboration covered:

- **Product and architecture:** turning the initial idea into staged delivery,
  defining the platform boundary, recording architecture decisions, and
  maintaining the roadmap from the first MCP sandbox through the PostgreSQL
  cutover and wider multi-factory vision.

- **Workflow-engine selection and orchestration:** evaluating the needs of a
  visual, human-reviewable workflow and using n8n for form intake,
  orchestration, review, recovery, and result presentation. Codex helped build,
  inspect, test, and export the `CODEX TEST` workflows while keeping them
  inactive, unpublished, credential-free, and unavailable through MCP.

- **Application-service selection:** choosing FastAPI with Uvicorn for a small,
  typed local HTTP service with validation and generated API documentation,
  then implementing its endpoints, configuration, dependency boundaries, and
  startup tooling.

- **Python engineering:** implementing Pydantic contracts, the run-state
  machine, provider adapters, idempotency, review and artifact services,
  quality checks, error handling, authentication, repositories, migrations,
  evaluation utilities, and backup support.

- **Database evolution:** starting with SQLite for the smallest deterministic
  vertical slice, evaluating the durability and portability needs, and then
  selecting PostgreSQL for the active backend. Codex helped build the
  SQLAlchemy portability layer, Alembic schema, transactional import,
  reconciliation, concurrency verification, backup/restore, cutover, and
  rollback procedures.

- **Local-model selection:** integrating Ollama behind a provider interface and
  evaluating `gemma4:12b`, `gemma4:26b`, and `gemma4:31b` on synthetic strategy
  tasks. The current baseline remains `gemma4:31b`; the repository records
  latency, schema validity, quality results, and the still-pending blind human
  preference step rather than claiming a broader benchmark result.

- **Container and environment management:** creating Docker Compose definitions
  and operational scripts for n8n and PostgreSQL, plus coordinated startup,
  status, health-check, shutdown, persistence, and recovery flows for Docker,
  Ollama, FastAPI, and the database.

- **Infrastructure startup and live operations:** using Codex powered by
  GPT-5.6 to start the complete local stack, monitor startup output, diagnose
  service-process issues, and verify PostgreSQL, n8n, FastAPI, Ollama,
  authentication, installed models, and health endpoints through repository
  CLI commands.

- **Safety and security:** defining synthetic-data-only rules, secret handling,
  separate service and review tokens, fail-closed authentication, artifact
  integrity checks, workflow restrictions, retention policy, trust boundaries,
  and explicit human approval semantics.

- **Testing and evaluation:** creating synthetic fixtures and unit, API,
  integration, workflow-contract, dual-database, idempotency, concurrency,
  restart, migration, backup, restore, and local-model evaluation checks. Codex
  repeatedly used test output and service logs to diagnose and correct issues.

- **Documentation and communication:** writing the setup guide, architecture,
  API reference, security model, operating procedures, troubleshooting,
  verification records, migration runbooks, roadmap, diagrams, and project
  infographic.

- **Presentation production:** creating the Remotion-based project video,
  including its TypeScript/React structure, scenes, animation, layout,
  messaging, captured clips, provenance, and render preparation.

- **Git and GitHub delivery:** organizing the work into reviewable changes,
  checking diffs, preserving unrelated work, writing meaningful commits,
  managing branches, pushing to GitHub, and preparing and merging the project
  pull request.

The three AI roles are deliberately separate:

1. **Codex** was the coding agent that interacted with the repository and local
   tools during development.

2. **GPT-5.6** was the reasoning model powering that Codex collaboration; it is
   part of how the solution was designed and built.

3. **Ollama with Gemma 4** is the application's local runtime inference path for
   strategy generation and optional critique. Deterministic tests use the fake
   provider instead.

GPT-5.6 is therefore **not a hidden production dependency** of AI Strategy
Factory. The running application does not call GPT-5.6, and no OpenAI API key
is required for its implemented local path.

The work remained human-controlled throughout. Codex explained planned changes
before applying them; I retained authority over scope, architecture, safety,
workflow activation, publication, and final acceptance. The checked-in
`AGENTS.md` makes those operating constraints durable for repository work.

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

## License

Original AI Strategy Factory source code, scripts, workflow definitions, tests,
templates, and technical documentation are licensed under the
[Apache License 2.0](LICENSE).

The Remotion video project, rendered videos, captured clips, screenshots,
infographics, and other presentation or promotional media are excluded from
the Apache License 2.0 and remain all rights reserved. See
[ASSET-LICENSE.md](ASSET-LICENSE.md).

Third-party software, models, container images, and services retain their
respective licenses and terms. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [NOTICE](NOTICE).

## OpenAI Build Week submission

This repository supports the **Work and Productivity** submission for OpenAI
Build Week. It contains synthetic examples, setup and verification commands,
the inactive `CODEX TEST` workflow export, and evidence of how Codex powered by
GPT-5.6 accelerated product, engineering, testing, documentation, operations,
and presentation work.

The hackathon permits either of these repository-access options:

- keep the repository public with the included licensing; or
- keep it private and grant repository access to `testing@devpost.com` and
  `build-week-event@openai.com`.

Access to the working project must remain free and unrestricted for testing
through the judging period. For this submission, retain judge access until the
winners have been announced before making a public repository private or
removing private collaborators. A public repository cannot be made
retroactively confidential: forks and clones created while it was public may
remain available.

Submission-specific items that are not stored as credentials in this
repository must be supplied in Devpost: a public YouTube demonstration of less
than three minutes with a clear demo and audio explaining what was built and
how Codex and GPT-5.6 were used; the primary `/feedback` Codex Session ID; the
repository URL; and any concise testing instructions needed by the judges.
