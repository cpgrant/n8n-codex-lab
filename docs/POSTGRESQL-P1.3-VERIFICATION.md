# PostgreSQL P1.3 verification

Verified on 2026-07-18 using synthetic data only.

## Scope

P1.3 expands the database tests beyond the basic PostgreSQL lifecycle and the
initial concurrency checks. The same portability cases now run on SQLite and,
when an isolated test URL is supplied, PostgreSQL.

The matrix covers:

- repository and completed-idempotency persistence after engine disposal and
  recreation;
- durable, sanitized generation failures;
- atomic rollback when artifact metadata violates a uniqueness constraint;
- pending idempotency release followed by an exact retry;
- the complete API, quality-report, review, and artifact lifecycle;
- concurrent idempotency reservation and competing state transitions;
- fail-closed application startup when the selected PostgreSQL endpoint is
  unavailable.

## Automated SQLite result

The default suite completed with:

```text
103 passed, 8 skipped, 1 warning
```

The skips are opt-in PostgreSQL integration cases. The warning is the existing
Starlette/httpx test-client deprecation warning.

## Isolated PostgreSQL result

`scripts/verify-postgres-foundation.sh` created a uniquely named temporary
database, applied Alembic revision `0001_current_factory_schema`, verified the
eight expected public tables, and ran both the portability matrix and the
PostgreSQL-specific integration suite.

```text
12 passed, 1 warning
Alembic revision: 0001_current_factory_schema
Public tables: 8
```

The script's exit trap removed only the temporary database it created. It did
not import the current SQLite data or change the configured default backend.

## Decision

P1.3 is complete. SQLite remains the default and rollback backend. P1.4 may
now add dry-run-first SQLite export/import, reconciliation, PostgreSQL backup,
restore, and rollback procedures.
