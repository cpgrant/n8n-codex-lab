#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_CONTAINER="codex-test-ai-factory-postgres"
TEST_DATABASE="ai_factory_p1_verify_$$"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
  exit 2
fi

cleanup() {
  docker exec "$POSTGRES_CONTAINER" \
    dropdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    --if-exists "$TEST_DATABASE" >/dev/null
}
trap cleanup EXIT

docker exec "$POSTGRES_CONTAINER" \
  createdb -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" "$TEST_DATABASE"

DATABASE_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${TEST_DATABASE}"

AI_FACTORY_DATABASE_URL="$DATABASE_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.migrations

revision="$(
  docker exec "$POSTGRES_CONTAINER" \
    psql -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    -d "$TEST_DATABASE" -Atc \
    "SELECT version_num FROM alembic_version"
)"
table_count="$(
  docker exec "$POSTGRES_CONTAINER" \
    psql -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    -d "$TEST_DATABASE" -Atc \
    "SELECT count(*) FROM pg_tables WHERE schemaname = 'public'"
)"

if [[ "$revision" != "0001_current_factory_schema" ]]; then
  echo "Unexpected Alembic revision: $revision" >&2
  exit 1
fi
if [[ "$table_count" != "8" ]]; then
  echo "Expected 8 public tables; found $table_count." >&2
  exit 1
fi

AI_FACTORY_TEST_POSTGRES_URL="$DATABASE_URL" \
UV_CACHE_DIR="$REPOSITORY_ROOT/agent-service/.uv-cache" \
  uv run --project "$REPOSITORY_ROOT/agent-service" \
  pytest -q \
    "$REPOSITORY_ROOT/agent-service/tests/test_database_portability.py" \
    "$REPOSITORY_ROOT/agent-service/tests/test_postgresql.py"

echo "PostgreSQL P1.1-P1.3 verified on an isolated synthetic database."
echo "Alembic revision: $revision"
echo "Public tables: $table_count"
