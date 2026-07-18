# PostgreSQL P1.4 verification

Verified on 2026-07-18 using synthetic local data only.

## Automated result

```text
108 passed, 8 skipped, 1 warning
```

The skips are opt-in PostgreSQL integration cases. The warning is the existing
Starlette/httpx test-client deprecation warning.

## Live migration and recovery rehearsal

`scripts/verify-postgres-migration.sh` used SQLite's online backup mechanism to
copy the current synthetic database. It did not import directly from or write
to the original file.

The copied source contained:

| Table | Rows |
| --- | ---: |
| `strategy_runs` | 31 |
| `idempotency_requests` | 65 |
| `run_reviews` | 19 |
| `run_artifacts` | 16 |
| `run_quality_reports` | 15 |
| `run_quality_artifacts` | 13 |

The rehearsal:

1. created and migrated an isolated empty PostgreSQL database;
2. confirmed the dry run performed no application writes;
3. verified 16 strategy artifacts and 13 quality artifacts against their
   recorded SHA-256 checksums;
4. imported all six application tables in one transaction;
5. matched every table by count and deterministic content fingerprint;
6. rejected a second import because the target was no longer empty;
7. created and validated a custom-format `pg_dump` backup;
8. restored the dump into isolated temporary storage;
9. reconciled the restored database exactly with the SQLite copy;
10. removed all temporary databases and files through exit traps.

The original SQLite SHA-256 remained:

```text
8b49b587c7e59a07bb7b9c76ad428aefe18b655ed2fa95aa792dd05ea0a32929
```

The primary `ai_factory` PostgreSQL database remained empty with zero public
tables. No backend configuration changed.

## Decision

P1.4 is complete. The remaining P1.5 gate is a controlled synthetic cutover,
API and Ollama smoke verification, service/PostgreSQL restart persistence,
n8n connectivity verification without activation, and demonstrated switch
back to the unchanged SQLite backend.
