#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_CONTAINER="codex-test-ai-factory-postgres"
BACKUP=""
RESTORE_DATABASE="ai_factory_restore_test_$$"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup)
      BACKUP="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 --backup FILE" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$BACKUP" ]]; then
  echo "PostgreSQL backup does not exist: $BACKUP" >&2
  exit 2
fi

cleanup() {
  docker exec "$POSTGRES_CONTAINER" \
    dropdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    --if-exists "$RESTORE_DATABASE" >/dev/null
}
trap cleanup EXIT

docker exec "$POSTGRES_CONTAINER" \
  createdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" "$RESTORE_DATABASE"
docker exec -i "$POSTGRES_CONTAINER" \
  pg_restore -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
  -d "$RESTORE_DATABASE" --no-owner --no-privileges < "$BACKUP"

revision="$(
  docker exec "$POSTGRES_CONTAINER" \
    psql -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    -d "$RESTORE_DATABASE" -Atc "SELECT version_num FROM alembic_version"
)"
if [[ "$revision" != "0001_current_factory_schema" ]]; then
  echo "Restored database has unexpected Alembic revision: $revision" >&2
  exit 1
fi

echo "PostgreSQL backup restored successfully into isolated temporary storage."
