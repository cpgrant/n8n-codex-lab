# AI Strategy Factory

**From structured brief to human-approved strategy artifact—locally,
repeatably, and with a visible audit trail.**

AI Strategy Factory is a working, local-first product for independent strategy
consultants and small internal teams. It turns a structured brief into an
AI-generated strategy draft, evaluates the draft, pauses for an explicit human
decision, and creates a checksummed Markdown artifact only after approval.

It addresses a practical gap between unstructured AI chat, which is difficult
to reproduce and govern, and heavyweight enterprise strategy systems, which can
be expensive and slow to adopt. The current repository is a synthetic-data
demonstration—not a production system approved for confidential client data.

## Judge quick start

- **Watch:** [90-second narrated product demonstration][demo-video]
- **Evaluate:** [judge guide with a five-minute verification path](docs/JUDGE-GUIDE.md)
- **Measure:** [existing technical and benchmark metrics](docs/METRICS-SUMMARY.md)
- **Eligibility evidence:** [prior work and submission-period development](docs/SUBMISSION-PERIOD-EVIDENCE.md)
- **Install:** [clean-machine setup and verification](docs/SETUP.md)
- **Inspect:** [public source repository](https://github.com/cpgrant/n8n-codex-lab)

[demo-video]: https://www.youtube.com/watch?v=QKJJM996nmI

## Prior Work and Submission-Period Development

AI Strategy Factory existed before the OpenAI Build Week submission period, so
judges should evaluate only the meaningful extensions made after the official
cutoff: **2026-07-13 09:00 PDT (16:00 UTC / 18:00 CEST)**.

At the cutoff, the repository already contained its safety and MCP lab
foundation, an early FastAPI strategy pipeline, an inactive n8n workflow,
local Ollama generation, structured intake, initial quality evaluation, and a
synthetic-data policy. After the cutoff, Codex powered by GPT-5.6 was used to
extend that baseline with authenticated service and review boundaries,
workflow recovery and responsive review forms, stronger quality contracts,
retention and backup controls, PostgreSQL portability and cutover tooling,
coordinated system operations, reproducible setup, demonstration assets, and
judge-facing verification material.

As of the public audit head
[`87ace2b`](https://github.com/cpgrant/n8n-codex-lab/commit/87ace2b4a681facf8e69a0a37310fa72484a4b9d),
the `main` history contains **38 commits after the cutoff**, compared with **21
commits at or before the baseline**. The eligible change set spans 136 files,
with 15,907 insertions and 529 deletions relative to cutoff commit
[`698badc`](https://github.com/cpgrant/n8n-codex-lab/commit/698badc443889556e179fad7d7445430fd12dd77).
See the [dated submission-period evidence table](docs/SUBMISSION-PERIOD-EVIDENCE.md)
and the [public comparison from the cutoff baseline to the audit head](https://github.com/cpgrant/n8n-codex-lab/compare/698badc443889556e179fad7d7445430fd12dd77...87ace2b4a681facf8e69a0a37310fa72484a4b9d).

## Problem, audience, and differentiation

### The problem

Strategy work rarely ends with generating text. A usable strategy must connect
evidence to choices, make trade-offs visible, assign ownership, survive review,
and leave behind an artifact that others can revisit. General AI chat can help
with drafting, but its conversational output does not by itself provide a
repeatable intake contract, durable run state, an approval boundary, or a
traceable final deliverable.

For a small practice, assembling those controls from enterprise platforms is
often disproportionate to the task. This creates a practical gap: AI can make
drafting faster, but the surrounding strategy process can remain informal,
opaque, and difficult to reproduce.

### The initial audience

The primary audience is **independent strategy consultants and small internal
strategy teams** conducting bounded strategy engagements. Their immediate job
is to convert a client or organizational brief into a consistent first draft
without surrendering professional judgment or losing the review trail.

The system is especially relevant when the team wants:

- a reusable intake structure instead of starting every engagement in chat;
- local model inference as an option;
- a clear distinction between AI advice and human authorization;
- reproducible outputs that can be inspected after the workflow completes; and
- lightweight infrastructure that can be run and understood by a small team.

The current version proves this workflow with fictional inputs. Moving from a
synthetic lab to real client use would require the pilot-gated privacy,
security, operations, and governance work identified in the roadmap.

### How the product differs

| Approach | Useful for | Missing for this use case | AI Strategy Factory |
| --- | --- | --- | --- |
| General AI chat | Fast exploration and drafting | Structured intake, durable state, enforced review, reproducible artifact creation | Wraps generation in an explicit strategy lifecycle |
| Basic workflow demo | Showing that tools can be connected | Domain contract, state invariants, recovery, tests, and approval semantics | Implements and verifies the full brief-to-artifact path |
| Cloud-only AI workflow | Convenient hosted inference | A local inference option and a clear local processing boundary | Supports Ollama locally behind a provider interface |
| Fully autonomous agent | Reducing human intervention | Appropriate decision authority for consequential strategy choices | Keeps approval exclusively human-controlled |

The novelty is not a claim that AI can replace a strategist. It is the opposite:
AI Strategy Factory makes the boundary between machine contribution and human
accountability explicit and executable. Generation, quality advice, review,
state transition, and artifact creation are separate concerns rather than one
opaque model response.

### Why this is more than a prompt wrapper

1. The strategy brief is structured and validated before generation.
2. The model can draft and advise, but it cannot approve its own work.
3. Quality checks do not silently change workflow state.
4. An authenticated human reviewer must approve or reject the draft.
5. PostgreSQL preserves run state and review history.
6. Only an approved draft becomes a durable, checksummed artifact.

The runnable implementation combines an inactive n8n workflow, a typed
FastAPI service, PostgreSQL persistence, optional local Ollama inference,
Docker-managed infrastructure, authentication boundaries, synthetic fixtures,
and automated verification. Deterministic evaluation can use the fake provider
without requiring an external AI API.

For the intended audience, the potential impact is a shorter and more
consistent path to a review-ready first draft, with less process reinvention
between engagements and clearer evidence of who approved the result. The
repository demonstrates the mechanism and its safeguards; it does not yet make
a measured claim about time saved or strategy quality in real engagements.

```text
Structured brief → validation → AI draft → quality advice
                                              ↓
Approved Markdown artifact ← human review ← review-ready draft
```

The repository retains the technical name `n8n-codex-lab`; presentation-facing
material uses the product name **AI Strategy Factory**.

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

### Codex contribution evidence

The following evidence is checked into the repository so the use of Codex can
be assessed from working artifacts, not only from this description.

| Contribution | What Codex helped produce or improve | Inspectable evidence | How a judge can verify it |
| --- | --- | --- | --- |
| Product architecture and staged planning | Converted the product concept into bounded stages, explicit component responsibilities, and decision gates | [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/AI-FACTORY-PLATFORM.md`](docs/AI-FACTORY-PLATFORM.md) | Compare completed stages with the corresponding code, workflow, and verification records |
| FastAPI application engineering | Implemented typed contracts, API routes, run-state behavior, provider boundaries, review decisions, artifacts, and error handling | [`agent-service/src/ai_factory/`](agent-service/src/ai_factory/), [`docs/API.md`](docs/API.md) | Run `cd agent-service && uv run pytest -q` and inspect the generated FastAPI API surface |
| n8n workflow orchestration | Built and iterated the inactive intake-to-review workflow while preserving the `CODEX TEST` safety boundary | [`workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json`](workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json), [`workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.md`](workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.md) | Import the workflow into local n8n or run `node scripts/verify-stage8-intake.js` |
| PostgreSQL migration and persistence | Evolved the initial SQLite slice into a portable PostgreSQL-backed service with schema migration, reconciliation, backup, and rollback paths | [`docs/POSTGRESQL-MIGRATION-PLAN.md`](docs/POSTGRESQL-MIGRATION-PLAN.md), [`agent-service/migrations/`](agent-service/migrations/), [`agent-service/tests/test_postgresql.py`](agent-service/tests/test_postgresql.py) | Run the database verification scripts documented in the migration plan |
| Test and failure-driven iteration | Added tests for APIs, schemas, state transitions, providers, idempotency, review, artifacts, backup, workflow export, and database portability | [`agent-service/tests/`](agent-service/tests/), [`scripts/verify-stage4.sh`](scripts/verify-stage4.sh), [`scripts/verify-stage9-5-lite.js`](scripts/verify-stage9-5-lite.js) | Run the test suite and lightweight milestone checks from the [judge guide](docs/JUDGE-GUIDE.md) |
| Safety and authentication | Made synthetic-only operation, inactive workflow handling, human approval, token boundaries, and fail-closed behavior explicit and testable | [`AGENTS.md`](AGENTS.md), [`docs/SECURITY.md`](docs/SECURITY.md), [`docs/STAGE-9.1-VERIFICATION.md`](docs/STAGE-9.1-VERIFICATION.md) | Inspect the durable agent rules and run `scripts/verify-stage9-1-auth.sh` on a configured system |
| Local operations and reproducibility | Created coordinated startup, health, status, shutdown, and recovery paths for the multi-service system | [`scripts/system-start.sh`](scripts/system-start.sh), [`scripts/agent-check.sh`](scripts/agent-check.sh), [`docs/DAILY-OPERATIONS.md`](docs/DAILY-OPERATIONS.md) | Follow the five-minute configured-machine path in the [judge guide](docs/JUDGE-GUIDE.md) |
| Demonstration and communication | Helped turn the implementation into a narrated Remotion video and supporting visual explanation | [`ai-strategy-factory-video/src/Composition.tsx`](ai-strategy-factory-video/src/Composition.tsx), [`docs/ai-strategy-factory-infographic-v3.png`](docs/ai-strategy-factory-infographic-v3.png) | Watch the [90-second demonstration][demo-video] and compare its flow with the checked-in workflow |

This evidence shows the breadth of the collaboration, but not autonomous
authorship. The human supplied the product direction and constraints, approved
scope and architecture, reviewed results, and retained control over workflow
activation, publication, and acceptance.

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

- `docs/JUDGE-GUIDE.md` — judge-oriented demonstration and verification path
- `docs/METRICS-SUMMARY.md` — existing results and measurement gaps
- `docs/SETUP.md` — canonical clean-machine installation and verification
- `docs/DOCUMENTATION-AUDIT.md` — current documentation-freshness findings
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
