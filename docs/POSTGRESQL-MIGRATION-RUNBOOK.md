# SQLite to PostgreSQL migration runbook

This runbook applies only to the local synthetic AI Factory database. It does
not migrate n8n, activate a workflow, authorize real data, or enable multiple
FastAPI workers.

## Safety contract

- Stop FastAPI before the final plan and keep it stopped through import.
- Create and verify a SQLite/artifact backup first.
- Never delete or overwrite the SQLite database during migration.
- The PostgreSQL target must have the current Alembic schema and zero
  application rows.
- Review the dry-run JSON before applying.
- Do not put the PostgreSQL password in a command; scripts load the ignored
  `.env` without printing it.
- Only one database is authoritative for a FastAPI process. There is no
  dual-write mode.

## Prepare and inspect

Start PostgreSQL and back up the current SQLite database and artifacts:

```bash
scripts/postgres-start.sh
scripts/factory-backup.sh create
```

Verify the printed backup path with both commands:

```bash
scripts/factory-backup.sh verify <backup-path>
scripts/factory-backup.sh restore-test <backup-path>
```

Create or upgrade the empty PostgreSQL schema, then run the no-write plan:

```bash
scripts/postgres-prepare-schema.sh
scripts/factory-migrate-postgres.sh plan \
  --source data/ai-strategy-factory.db \
  --artifact-dir artifacts
```

Proceed only when `target_empty` and `eligible_to_apply` are `true`,
`writes_performed` is `false`, and the reported source counts are expected.

## Import and reconcile

Keep FastAPI stopped. Apply requires the explicit confirmation flag:

```bash
scripts/factory-migrate-postgres.sh apply \
  --source data/ai-strategy-factory.db \
  --artifact-dir artifacts \
  --confirm-empty-target
```

The importer rechecks that every application table is empty inside the target
transaction. Any import error rolls back that transaction. It then compares
every table by row count and deterministic content fingerprint.

Run reconciliation independently:

```bash
scripts/factory-migrate-postgres.sh reconcile \
  --source data/ai-strategy-factory.db \
  --artifact-dir artifacts
```

Proceed only when `matched` is `true` for the overall result and every table.

## PostgreSQL backup and restore test

Choose a new ignored backup filename. The backup command refuses to overwrite
an existing file:

```bash
scripts/postgres-backup.sh \
  --database ai_factory \
  --output backups/ai-strategy-factory/postgresql-before-cutover.dump

scripts/postgres-restore-test.sh \
  --backup backups/ai-strategy-factory/postgresql-before-cutover.dump
```

The restore test creates and removes a uniquely named temporary database. It
does not restore over `ai_factory`.

## Select PostgreSQL

Only after reconciliation and restore verification, select PostgreSQL in the
ignored `.env` without duplicating the password:

```text
AI_FACTORY_DEFAULT_DATABASE=postgresql
```

The normal launcher constructs the URL in memory from the existing PostgreSQL
component variables. An explicit `AI_FACTORY_DATABASE_URL` remains available
as an advanced process-level override.

## Roll back to SQLite

Stop FastAPI, set `AI_FACTORY_DEFAULT_DATABASE=sqlite` in the ignored `.env`,
and start FastAPI again. FastAPI then uses the unchanged
`data/ai-strategy-factory.db` and existing artifact directory.

Do not delete the PostgreSQL database during rollback. Retain both database
backups until the rehearsal and review period are complete.
