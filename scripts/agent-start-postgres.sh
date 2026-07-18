#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
  exit 2
fi

export AI_FACTORY_DATABASE_URL="postgresql+psycopg://${AI_FACTORY_POSTGRES_USER:-ai_factory}:${AI_FACTORY_POSTGRES_PASSWORD}@${AI_FACTORY_POSTGRES_HOST:-127.0.0.1}:${AI_FACTORY_POSTGRES_PORT:-5432}/${AI_FACTORY_POSTGRES_DB:-ai_factory}"

exec "$REPOSITORY_ROOT/scripts/agent-start.sh"
