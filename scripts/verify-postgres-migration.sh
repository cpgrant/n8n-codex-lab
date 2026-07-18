#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_CONTAINER="codex-test-ai-factory-postgres"
SOURCE_DATABASE="$REPOSITORY_ROOT/data/ai-strategy-factory.db"
IMPORT_DATABASE="ai_factory_p14_import_$$"
RESTORE_DATABASE="ai_factory_p14_restore_$$"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/ai-factory-p14.XXXXXX")"
SOURCE_COPY="$TEMP_ROOT/source.db"
DUMP_FILE="$TEMP_ROOT/import.dump"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
  exit 2
fi
if [[ ! -f "$SOURCE_DATABASE" ]]; then
  echo "Synthetic SQLite source does not exist: $SOURCE_DATABASE" >&2
  exit 2
fi

cleanup() {
  docker exec "$POSTGRES_CONTAINER" \
    dropdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    --if-exists "$RESTORE_DATABASE" >/dev/null
  docker exec "$POSTGRES_CONTAINER" \
    dropdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    --if-exists "$IMPORT_DATABASE" >/dev/null
  rm -rf "$TEMP_ROOT"
}
trap cleanup EXIT

sqlite3 "$SOURCE_DATABASE" ".backup '$SOURCE_COPY'"
SOURCE_HASH_BEFORE="$(shasum -a 256 "$SOURCE_DATABASE" | awk '{print $1}')"

docker exec "$POSTGRES_CONTAINER" \
  createdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" "$IMPORT_DATABASE"

IMPORT_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${IMPORT_DATABASE}"
RESTORE_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${RESTORE_DATABASE}"

AI_FACTORY_POSTGRES_MIGRATION_DATABASE="$IMPORT_DATABASE" \
  "$REPOSITORY_ROOT/scripts/postgres-prepare-schema.sh"

AI_FACTORY_POSTGRES_MIGRATION_URL="$IMPORT_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.data_migration plan --source "$SOURCE_COPY" \
  --artifact-dir "$REPOSITORY_ROOT/artifacts" \
  > "$TEMP_ROOT/plan.json"
jq -e '.eligible_to_apply == true and .writes_performed == false' \
  "$TEMP_ROOT/plan.json" >/dev/null

AI_FACTORY_POSTGRES_MIGRATION_URL="$IMPORT_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.data_migration apply --source "$SOURCE_COPY" \
  --artifact-dir "$REPOSITORY_ROOT/artifacts" \
  --confirm-empty-target > "$TEMP_ROOT/apply.json"
jq -e '.matched == true' "$TEMP_ROOT/apply.json" >/dev/null

if AI_FACTORY_POSTGRES_MIGRATION_URL="$IMPORT_URL" \
  UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.data_migration apply --source "$SOURCE_COPY" \
  --artifact-dir "$REPOSITORY_ROOT/artifacts" \
  --confirm-empty-target >/dev/null 2>&1; then
  echo "A second import unexpectedly succeeded against a non-empty target." >&2
  exit 1
fi

AI_FACTORY_POSTGRES_MIGRATION_URL="$IMPORT_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.data_migration reconcile --source "$SOURCE_COPY" \
  --artifact-dir "$REPOSITORY_ROOT/artifacts" \
  > "$TEMP_ROOT/reconcile.json"
jq -e '.matched == true' "$TEMP_ROOT/reconcile.json" >/dev/null

"$REPOSITORY_ROOT/scripts/postgres-backup.sh" \
  --database "$IMPORT_DATABASE" --output "$DUMP_FILE" >/dev/null
"$REPOSITORY_ROOT/scripts/postgres-restore-test.sh" \
  --backup "$DUMP_FILE" >/dev/null

docker exec "$POSTGRES_CONTAINER" \
  createdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" "$RESTORE_DATABASE"
docker exec -i "$POSTGRES_CONTAINER" \
  pg_restore -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
  -d "$RESTORE_DATABASE" --no-owner --no-privileges < "$DUMP_FILE"

AI_FACTORY_POSTGRES_MIGRATION_URL="$RESTORE_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.data_migration reconcile --source "$SOURCE_COPY" \
  --artifact-dir "$REPOSITORY_ROOT/artifacts" \
  > "$TEMP_ROOT/restore-reconcile.json"
jq -e '.matched == true' "$TEMP_ROOT/restore-reconcile.json" >/dev/null

SOURCE_HASH_AFTER="$(shasum -a 256 "$SOURCE_DATABASE" | awk '{print $1}')"
if [[ "$SOURCE_HASH_BEFORE" != "$SOURCE_HASH_AFTER" ]]; then
  echo "SQLite source changed during verification." >&2
  exit 1
fi

jq -c '.source_counts' "$TEMP_ROOT/plan.json"
echo "P1.4 migration, reconciliation, PostgreSQL dump, and restore verified."
echo "The original SQLite database was unchanged."
