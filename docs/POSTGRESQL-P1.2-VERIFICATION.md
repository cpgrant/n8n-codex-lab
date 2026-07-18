# PostgreSQL P1.2 verification

## Result

Platform P1.2, portable run and idempotency repositories, was verified on
2026-07-18 with SQLite as the unchanged default and an isolated synthetic
PostgreSQL database as the opt-in backend.

P1.2 enables FastAPI to use a fresh PostgreSQL database. It does not migrate
the existing SQLite dataset, make PostgreSQL the default, or enable
PostgreSQL-aware backup commands.

## Implemented

- `RunRepository` uses SQLAlchemy transactions and named parameters on SQLite
  and PostgreSQL;
- `IdempotencyRepository` uses the same portable engine and preserves reserve,
  conflict, in-progress, completion, replay, and release semantics;
- PostgreSQL review, artifact, and quality operations lock their parent row;
- run-state changes use conditional updates and reject concurrent changes;
- simultaneous idempotency inserts use the unique key as the final arbiter and
  recover the committed reservation safely;
- FastAPI shares one configured engine across both repositories and disposes
  it at shutdown;
- explicit SQLite and PostgreSQL URLs receive Alembic migrations before use;
- the repository-local SQLite path retains its existing startup behavior;
- the SQLite-only backup command fails closed when PostgreSQL is configured,
  pending P1.4.

## Automated evidence

The default suite passed:

```text
99 passed, 3 PostgreSQL-only tests skipped, 1 pre-existing warning
```

All existing API, repository, idempotency, quality, review, artifact, backup,
and workflow-export tests therefore remain green on SQLite after the repository
port.

The isolated PostgreSQL suite passed three tests:

1. complete FastAPI lifecycle: create, replay, retrieve, deterministic quality
   report, quality artifact, explicit approval, and strategy artifact;
2. two simultaneous reservations for one idempotency key, with one winner and
   one safe `IDEMPOTENCY_IN_PROGRESS` response;
3. two simultaneous transitions from the same run state, with one winner and
   one `run status changed concurrently` rejection.

## Live PostgreSQL evidence

`scripts/verify-postgres-foundation.sh` created a unique temporary database,
applied revision `0001_current_factory_schema`, verified eight public tables,
ran the three PostgreSQL integration tests, and removed the database through
its exit trap.

Observed result:

```text
3 passed
PostgreSQL P1.1-P1.2 verified on an isolated synthetic database.
Alembic revision: 0001_current_factory_schema
Public tables: 8
```

Post-verification checks found zero `ai_factory_p1_verify_*` databases and zero
public tables in the primary `ai_factory` database. The existing SQLite file
and artifacts were not migrated or modified by the PostgreSQL verifier.

## Boundary

P1.3 expands the dual-backend failure and concurrency matrix. P1.4 remains
responsible for SQLite export/import, reconciliation, PostgreSQL backup and
restore, and rollback. No production cutover, n8n database migration, Redis,
multiple workers, or real data is authorized by P1.2.
