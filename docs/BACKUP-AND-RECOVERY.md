# Backup and Recovery

## AI Strategy Factory Stage 9.3-lite

The local synthetic factory has a repository-managed, non-destructive backup
tool:

```bash
cd ~/Development/codex/n8n-codex-lab
scripts/factory-backup.sh create
```

The command:

- uses SQLite's online backup API, so FastAPI does not need to stop;
- normalizes the snapshot to one standalone database file without transient
  WAL/SHM sidecars;
- copies ignored local artifacts;
- records SHA-256 hashes and sizes in `manifest.json`;
- stores the backup beneath ignored
  `backups/ai-strategy-factory/factory-backup-<timestamp>/`;
- applies owner-only directory and file permissions.

Avoid generating or approving a strategy during the short backup operation.
The database snapshot is created before artifacts are copied, so every artifact
record present in the snapshot must have an immutable file available for the
later copy.

Verify a backup:

```bash
scripts/factory-backup.sh verify \
  backups/ai-strategy-factory/REPLACE-WITH-BACKUP-DIRECTORY
```

Test restoration into automatically removed temporary storage:

```bash
scripts/factory-backup.sh restore-test \
  backups/ai-strategy-factory/REPLACE-WITH-BACKUP-DIRECTORY
```

The restore test does not replace `data/` or `artifacts/`. It copies the backup
into a temporary directory, runs SQLite integrity checks, verifies the manifest,
and reconciles recorded strategy and quality-report artifact checksums.

Audit backups older than the local 30-day synthetic retention period:

```bash
scripts/factory-backup.sh audit-expired --retention-days 30
```

The audit prints candidate directories and never deletes them. Before removing
an expired backup manually, verify that a newer backup passes both `verify` and
`restore-test`.

Stage 9.3-lite does not implement encrypted/offline backup custody, automated
expiry, per-run deletion, tenant-aware restore, or restoring into the active
service. Those remain full Stage 9.2/9.3 operationalization work.

## Important warning

Do not casually run:

```bash
docker compose down -v
```

The `-v` option can delete the persistent n8n data volume.

## Workflow backups

Export important workflows from n8n and save the JSON files in:

```text
workflows/
```

## Files to preserve

Keep backups of:

- `docker-compose.yml`
- `Dockerfile`
- `AGENTS.md`
- exported workflow JSON files
- repository documentation

## MCP token recovery

If an MCP token is exposed:

1. Open n8n.
2. Go to **Settings → Instance-level MCP**.
3. Open **Connection details**.
4. Regenerate the access token.
5. Export the replacement token in Terminal.
6. Restart VS Code or Codex from that Terminal session.

## Find the Docker volume

```bash
docker volume ls | grep n8n
```

The volume is likely named:

```text
n8n_n8n_data
```

Verify the exact name before backing up or restoring.

## Create a data-volume backup

```bash
mkdir -p ~/Backups/n8n

docker run --rm \
  -v n8n_n8n_data:/data \
  -v "$HOME/Backups/n8n:/backup" \
  alpine \
  tar czf "/backup/n8n-data-$(date +%Y-%m-%d-%H%M).tar.gz" -C /data .
```

Verify:

```bash
ls -lh ~/Backups/n8n
```

The volume archive is a whole-instance n8n backup and may contain workflows,
credentials, users, settings, and execution history. Keep it private. For
cross-database migration, n8n also documents `export:entities`; execution
history is excluded unless explicitly requested.

## Restore a backup

Stop n8n:

```bash
cd ~/Development/docker/n8n
docker compose down
```

Restore the selected archive:

```bash
docker run --rm \
  -v n8n_n8n_data:/data \
  -v "$HOME/Backups/n8n:/backup" \
  alpine \
  sh -c 'rm -rf /data/* && tar xzf /backup/REPLACE-WITH-BACKUP-FILENAME.tar.gz -C /data'
```

Restart:

```bash
docker compose up -d
```

## Recover after a failed image update

If the previous custom image still exists:

```bash
cd ~/Development/docker/n8n
docker compose up -d --no-build
```

Verify:

```bash
docker compose ps
docker exec -it n8n n8n --version
docker exec -it n8n ffmpeg -version
```
