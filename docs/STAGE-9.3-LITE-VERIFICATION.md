# Stage 9.3-lite verification

Date: 2026-07-16

Status: **Complete for local, inactive, unpublished, synthetic-only
housekeeping and backup verification.**

## Scope

Stage 9.3-lite provides a bounded local housekeeping layer:

- explicit n8n execution-retention settings;
- read-only identification of expired `CODEX TEST` executions;
- safe manual cleanup guidance;
- online backup of the factory SQLite database and Markdown artifacts;
- manifest and checksum verification;
- a basic restore test in temporary storage;
- read-only backup-expiry auditing.

It does not implement full deletion governance or pilot-grade recovery.

## Retention contract

| Data category | Stage 9.3-lite rule | Enforcement |
| --- | --- | --- |
| Completed `CODEX TEST` executions | 14 days | n8n rolling pruning plus audit |
| Waiting form-test executions | Audit after 24 hours | Read-only candidate report |
| SQLite runs and Markdown artifacts | Review after 30 days | No direct-SQL or automatic deletion |
| Factory backups | 30 days | Read-only expired-backup audit |
| Temporary restore data | One verification session | Automatic temporary-directory removal |

The 30-day factory-run target is intentionally not enforced with direct SQL.
Run ownership, authorized per-run deletion, coordinated artifact removal, and
audit tombstones remain full Stage 9.2/9.3 work.

## n8n audit

The installed n8n version supports rolling execution pruning with these
defaults:

```text
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=336
EXECUTIONS_DATA_PRUNE_MAX_COUNT=10000
```

The repository overlay now records the same 336-hour maximum age and lowers the
local saved-execution cap to 500. The count cap takes effect on the next normal
n8n restart; no special restart was required for verification.

The read-only command:

```bash
scripts/n8n-execution-retention-audit.sh
```

copies the live n8n SQLite database to a temporary file, queries only execution
ID, mode, status, timestamps, and workflow name, and removes the snapshot on
exit. It never issues SQL `DELETE`, deletes a workflow, or modifies the Docker
volume.

The 2026-07-16 audit found four stale waiting candidates:

```text
65
66
67
75
```

They were deliberately not deleted. The operator must first confirm that no
form test is still active, then remove only confirmed IDs through n8n's
**Executions** view.

## Factory backup contract

`scripts/factory-backup.sh create`:

1. creates a SQLite online backup before copying artifacts;
2. checkpoints the backup and removes transient WAL/SHM sidecars;
3. copies local artifacts without following symlinks;
4. creates a versioned `manifest.json` with file sizes and SHA-256 hashes;
5. applies owner-only permissions;
6. atomically renames the completed backup directory.

`verify` checks:

- exact manifest inventory;
- file size and SHA-256 hashes;
- SQLite `PRAGMA integrity_check`;
- availability and checksum of every strategy artifact recorded in SQLite;
- availability and checksum of every quality-report artifact recorded in
  SQLite.

`restore-test` copies the backup to temporary storage and repeats the database,
manifest, and artifact checks. It never overwrites active storage.

## Verification results

The following passed:

```text
91 FastAPI/service tests
Stage 9.3-lite static and live backup verifier
Shell syntax checks
Git whitespace checks
Live read-only n8n execution audit
```

The retained local verification backup is:

```text
backups/ai-strategy-factory/factory-backup-20260716T084833418802Z
```

It is ignored by Git and contains a version `0.1` manifest for 39 files. Both
direct verification and temporary restoration reported:

```json
{"quality_artifacts": 13, "runs": 31, "strategy_artifacts": 16}
```

The backup directory permission is `0700`; the manifest, database, and copied
files use `0600`.

## Reference behavior

n8n documents rolling execution pruning as enabled by default, with a
336-hour maximum age and a default 10,000-execution count cap:
<https://docs.n8n.io/hosting/configuration/environment-variables/executions/>.
Its server CLI documentation also distinguishes database-entity exports from
workflow/credential exports:
<https://docs.n8n.io/hosting/cli-commands/>.

The first live restore test found that SQLite's transient `-wal` and `-shm`
files could enter the manifest and disappear after a verification connection.
Backup creation was corrected to checkpoint and normalize the snapshot to one
standalone SQLite file. A regression assertion now requires both sidecars to be
absent, and the live verify/restore sequence passes.

## Safety state

- No workflow was deleted, activated, published, or made available through
  MCP.
- No n8n execution was deleted during implementation or verification.
- No credential was modified, exported, or printed.
- No active SQLite database or artifact was overwritten.
- Backup and restore-test data remained local and ignored by Git.
- All input and stored content remained synthetic.

## Deferred full Stage 9.3 controls

- trusted owner/tenant scope and deletion authorization;
- per-run coordinated deletion across SQLite, artifacts, logs, and indexes;
- content-free deletion tombstones;
- encrypted or offline backup custody and access review;
- automatic backup expiration;
- restore approval, active-storage replacement, and rollback;
- tests preventing restored data from reviving a governed deletion.
