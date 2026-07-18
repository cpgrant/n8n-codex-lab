# PostgreSQL P1.1 verification

## Result

Platform P1.1, the database configuration and migration foundation, was
verified on 2026-07-18 using synthetic infrastructure only.

At the P1.1 checkpoint, PostgreSQL was not yet enabled for FastAPI and selection
failed closed. P1.2 later superseded that temporary boundary by porting both
repositories. SQLite still remains the default.

## Implemented

- `AI_FACTORY_DATABASE_URL` validation and normalization for SQLite and
  PostgreSQL;
- SQLite default and explicit database-backend reporting;
- SQLAlchemy synchronous engine creation with SQLite foreign-key, busy-timeout,
  and WAL configuration;
- SQLAlchemy connection verification for SQLite and PostgreSQL;
- Alembic configuration and revision `0001_current_factory_schema`;
- the current seven application tables plus Alembic's version table on a fresh
  database;
- locked SQLAlchemy, Alembic, and psycopg dependencies;
- a repeatable isolated PostgreSQL verifier;
- fail-closed FastAPI startup for PostgreSQL until P1.2.

## Automated evidence

The complete suite passed:

```text
98 passed, 1 pre-existing Starlette/httpx deprecation warning
```

New coverage verifies:

- default SQLite URL resolution;
- PostgreSQL URL normalization to the psycopg driver;
- rejection of unsupported or incomplete database URLs;
- portable SQLite engine connectivity;
- repeatable Alembic migration of an empty SQLite database;
- the expected schema and legacy schema-version records;
- deliberate FastAPI refusal to use PostgreSQL before P1.2.

## Live PostgreSQL evidence

`scripts/verify-postgres-foundation.sh`:

1. created a uniquely named synthetic database in the local PostgreSQL 18.4
   container;
2. applied Alembic migration `0001_current_factory_schema` through psycopg;
3. verified the migration revision and eight public tables;
4. removed the temporary database through an exit trap.

Observed result:

```text
PostgreSQL P1.1 foundation verified on an isolated synthetic database.
Alembic revision: 0001_current_factory_schema
Public tables: 8
```

Post-verification checks found zero `ai_factory_p1_1_*` databases and zero
public tables in the primary `ai_factory` database. Existing SQLite data was
not read, copied, changed, or deleted.

## Boundary

At this checkpoint, P1.2 still had to port `RunRepository` and
`IdempotencyRepository` before FastAPI could use PostgreSQL. P1.2 has since
completed that work; see `docs/POSTGRESQL-P1.2-VERIFICATION.md`. Data migration,
backup/restore, cutover, multiple workers, Redis, n8n database migration, and
real data remain outside P1.1.
