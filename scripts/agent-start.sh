#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPOSITORY_ROOT/agent-service/.uv-cache}"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"
require_factory_auth_env

if [[ -z "${AI_FACTORY_DATABASE_URL:-}" && "${AI_FACTORY_DEFAULT_DATABASE:-sqlite}" == "postgresql" ]]; then
  if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
    echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
    exit 2
  fi
  export AI_FACTORY_DATABASE_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${AI_FACTORY_POSTGRES_DB:-ai_factory}"
fi

cd "$REPOSITORY_ROOT/agent-service"

exec uv run uvicorn ai_factory.main:app \
  --host "${AI_FACTORY_HOST:-127.0.0.1}" \
  --port "${AI_FACTORY_PORT:-8000}" \
  --workers 1
