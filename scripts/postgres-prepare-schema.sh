#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_DATABASE="${AI_FACTORY_POSTGRES_MIGRATION_DATABASE:-ai_factory}"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
  exit 2
fi
if [[ ! "$POSTGRES_DATABASE" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
  echo "Invalid PostgreSQL migration database name." >&2
  exit 2
fi

export AI_FACTORY_DATABASE_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${POSTGRES_DATABASE}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPOSITORY_ROOT/agent-service/.uv-cache}"

exec uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.migrations
