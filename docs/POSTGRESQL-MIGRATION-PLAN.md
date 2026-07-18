# PostgreSQL database portability plan

## Decision and current state

PostgreSQL is accepted as an optional AI Factory database backend and as the
preferred durable database before multiple FastAPI workers or multiple human
users are introduced. SQLite remains the active and default backend until the
application migration and verification gates in this plan pass.

Infrastructure checkpoint `debf6d4`, completed on 2026-07-18, provides:

- the pinned ARM64-compatible `postgres:18.4-bookworm` image;
- a repository-owned Docker Compose service;
- a localhost-only `127.0.0.1:5432` binding;
- a persistent named Docker volume and container health check;
- separate start, status, and non-destructive stop scripts;
- an ignored, environment-backed PostgreSQL password.

The container was verified healthy and its synthetic persistence marker
survived a stop/start before the marker was removed. The `ai_factory` database
is currently empty. FastAPI still reads and writes
`data/ai-strategy-factory.db`; n8n continues to use its own SQLite database.

P1.1 is also complete. The service now recognizes validated SQLite and
PostgreSQL URLs, the portable engine and Alembic foundation are installed, and
a fresh isolated PostgreSQL database was migrated successfully. FastAPI now
uses PostgreSQL when it is selected explicitly because P1.2 has ported both
repositories. SQLite remains the default, and no existing data is migrated
automatically.

## Objective

Make the FastAPI service portable between SQLite and PostgreSQL without
changing its API contracts, run-state rules, idempotency semantics, human
review boundary, artifact checksums, or synthetic-only operating policy.

PostgreSQL support should provide a safe foundation for later durable jobs and
multiple workers. It does not by itself implement asynchronous execution,
multi-agent orchestration, tenant isolation, or pilot readiness.

## Scope

Included:

- an explicit database URL and backend selection;
- a shared database access layer for SQLite and PostgreSQL;
- versioned schema migrations;
- portable run, review, quality-report, artifact, and idempotency operations;
- atomic state transitions and concurrency tests;
- automated test coverage for both backends;
- synthetic SQLite-to-PostgreSQL migration and reconciliation tooling;
- PostgreSQL backup, restore, and rollback procedures;
- a synthetic end-to-end verification with the workflow kept inactive.

Excluded from this checkpoint:

- migrating n8n from its own SQLite database;
- Redis or n8n queue mode;
- background job workers or API contract changes to `202 Accepted`;
- run ownership, tenants, or other Stage 9.2 controls;
- real or confidential data;
- workflow activation or publication;
- automatic deletion or production high availability.

## Target architecture

During portability verification:

```text
                         +-> SQLite (default and rollback backend)
n8n -> FastAPI service --|
                         +-> PostgreSQL (explicit opt-in backend)
```

Only one backend is authoritative for a service process. The application must
not dual-write to SQLite and PostgreSQL. A cutover changes configuration only
after a stopped-service migration and reconciliation has passed.

## Implementation plan and estimate

Estimates are focused engineering time for one contributor and include tests,
documentation, and review. They assume the current 99-test baseline and the
existing synthetic dataset remain stable. Live Ollama verification can add
one to three hours of elapsed time without adding equivalent engineering work.

| Phase | Deliverable | Estimate |
| --- | --- | ---: |
| P1.0 | Container, secret, health, and persistent-volume foundation | Complete |
| P1.1 | Database URL, driver, common connection layer, and migration framework | Complete 2026-07-18 |
| P1.2 | Portable repositories, transactions, state transitions, and idempotency | Complete 2026-07-18 |
| P1.3 | Dual-backend schema, API, failure, and concurrency test matrix | 1-1.5 days |
| P1.4 | SQLite export/import, reconciliation, PostgreSQL backup, and restore | 0.75-1 day |
| P1.5 | Synthetic cutover rehearsal, end-to-end verification, and documentation | 0.5-1 day |

Remaining total: **2.25-3.5 focused engineering days**, approximately **16-25
hours**. Allow **3-5 calendar days** when review, live local-model runs, and a
one-day contingency for backend-specific transaction behavior are included.

### P1.1 — Database foundation

- add an `AI_FACTORY_DATABASE_URL` contract while retaining the current
  repository-local SQLite path as the default;
- add a maintained PostgreSQL driver and a common SQL access layer;
- introduce versioned migrations rather than running SQLite-only schema text
  at service startup;
- fail closed on invalid URLs or unavailable configured databases;
- keep credentials out of logs, health responses, Git, and workflow exports;
- document local host-to-container and later container-to-container addresses.

Completion evidence:

- complete on 2026-07-18 with 98 passing automated tests;
- an isolated PostgreSQL database migrated to revision
  `0001_current_factory_schema` with eight public tables;
- the temporary database was removed and the primary `ai_factory` database
  remained empty;
- verification details are in `docs/POSTGRESQL-P1.1-VERIFICATION.md`.

### P1.2 — Repository portability

- port `RunRepository` and `IdempotencyRepository` behind the common layer;
- preserve foreign keys, uniqueness, immutable draft behavior, and terminal
  review states;
- implement conditional state updates that fail when another worker changed
  the run concurrently;
- make idempotency reservation, completion, replay, and release transactional;
- preserve stored JSON payloads and all public API response shapes.

Completion evidence:

- complete on 2026-07-18 with 99 passing default-backend tests;
- three isolated PostgreSQL tests passed the full basic API/artifact lifecycle,
  concurrent idempotency reservation, and competing run-state transitions;
- cleanup removed the temporary database and left the primary database empty;
- verification details are in `docs/POSTGRESQL-P1.2-VERIFICATION.md`.

### P1.3 — Dual-backend verification

- parameterize database, repository, idempotency, review, quality, artifact,
  backup-boundary, and API tests across both backends where applicable;
- add PostgreSQL-specific transaction and connection-failure cases;
- exercise restart persistence and unavailable-database startup behavior;
- retain fast SQLite tests while adding an isolated PostgreSQL integration
  suite that never uses real data.

Completion evidence:

- the complete SQLite suite remains green;
- the PostgreSQL integration suite is repeatable from an empty database;
- test teardown removes only databases or schemas created by the test run.

### P1.4 — Migration, backup, and recovery

- create a dry-run-first SQLite export and PostgreSQL import command;
- require an empty PostgreSQL target unless an explicit, separately reviewed
  recovery mode is selected;
- preserve run IDs, timestamps, statuses, checksums, reviews, reports, artifact
  metadata, and idempotency records;
- reconcile table counts, foreign keys, draft checksums, and artifact files;
- add `pg_dump` backup and temporary-database restore verification;
- leave the original SQLite database intact as the rollback snapshot.

Completion evidence:

- a synthetic copy migrates without changing source data;
- reconciliation reports zero missing or unexpected records;
- a PostgreSQL dump restores successfully into temporary storage;
- switching configuration back to SQLite restores the prior service state.

### P1.5 — Synthetic cutover rehearsal

- stop FastAPI before migration and prevent writes during the cutover window;
- back up SQLite and artifacts, migrate, reconcile, then start FastAPI with the
  PostgreSQL URL;
- run deterministic API smoke tests first;
- run one synthetic Ollama generation, pro critique, explicit review, and
  artifact retrieval flow;
- verify n8n connectivity without activating or publishing the workflow;
- record the evidence and keep SQLite available for rollback.

Completion evidence:

- all API and workflow contracts behave identically on PostgreSQL;
- the synthetic run survives service and PostgreSQL restarts;
- backups and artifact checksums verify;
- Git is clean and the roadmap records the final decision.

## Decision gates

1. **Foundation gate:** merge portable schema and repository work only when
   SQLite remains green and a fresh PostgreSQL database passes integration
   tests.
2. **Migration gate:** do not import the current synthetic lab database until
   dry-run reconciliation and PostgreSQL restore tests pass.
3. **Default-backend gate:** do not make PostgreSQL the local default until the
   synthetic cutover rehearsal passes and rollback is demonstrated.
4. **Scaling gate:** do not add multiple workers merely because PostgreSQL is
   available. First implement durable job ownership, leases, retry limits, and
   Ollama concurrency controls as a separate checkpoint.

## Risks and controls

| Risk | Control |
| --- | --- |
| SQLite and PostgreSQL transaction behavior differs | Explicit transactions, conditional updates, and concurrent integration tests |
| Migration silently loses relationships or metadata | Empty-target import plus counts, foreign-key, checksum, and artifact reconciliation |
| Database URL leaks a password | Redacted configuration, safe errors, ignored `.env`, and log assertions |
| PostgreSQL becomes a single unverified dependency | Health checks, `pg_dump`, restore rehearsal, and retained SQLite rollback copy |
| More workers overload local Ollama | Keep model concurrency at one until measured; database scaling is not model scaling |
| n8n migration becomes entangled with the factory | Keep separate databases and defer n8n PostgreSQL/Redis work |

## Follow-on work

After P1 is complete, the next independent checkpoint may introduce durable
background jobs and bounded workers. Redis remains optional unless n8n queue
mode or measured broker requirements justify it. Full multi-user use still
requires the Stage 9.2-9.6 operationalization controls.
