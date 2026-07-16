#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/stage9-3-lite.XXXXXX")"
trap 'rm -rf "$TEMP_ROOT"' EXIT

echo "Checking explicit n8n retention configuration ..."
grep -Fq 'EXECUTIONS_DATA_PRUNE=true' "$REPOSITORY_ROOT/compose.n8n-auth.yml"
grep -Fq 'EXECUTIONS_DATA_MAX_AGE=336' "$REPOSITORY_ROOT/compose.n8n-auth.yml"
grep -Fq 'EXECUTIONS_DATA_PRUNE_MAX_COUNT=500' \
  "$REPOSITORY_ROOT/compose.n8n-auth.yml"

echo "Checking read-only n8n retention audit ..."
grep -Fq "This command is read-only." \
  "$REPOSITORY_ROOT/scripts/n8n-execution-retention-audit.sh"
if grep -Eq 'DELETE FROM|docker compose down -v' \
  "$REPOSITORY_ROOT/scripts/n8n-execution-retention-audit.sh"; then
  echo "The retention audit contains a destructive operation." >&2
  exit 1
fi

echo "Creating an isolated factory backup ..."
BACKUP="$(
  "$REPOSITORY_ROOT/scripts/factory-backup.sh" create \
    --backup-root "$TEMP_ROOT/backups"
)"

echo "Verifying backup manifest, SQLite, and artifact checksums ..."
"$REPOSITORY_ROOT/scripts/factory-backup.sh" verify "$BACKUP" >/dev/null

echo "Testing restore into temporary storage ..."
"$REPOSITORY_ROOT/scripts/factory-backup.sh" restore-test "$BACKUP" >/dev/null

echo "Checking backup-retention audit ..."
"$REPOSITORY_ROOT/scripts/factory-backup.sh" audit-expired \
  --backup-root "$TEMP_ROOT/backups" \
  --retention-days 30 >/dev/null

echo "Stage 9.3-lite backup and restore verification passed."
