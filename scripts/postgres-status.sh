#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_COMPOSE_FILE="$REPOSITORY_ROOT/compose.postgres.yml"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD is not configured." >&2
  exit 2
fi

docker compose \
  --project-name codex-test-ai-factory \
  -f "$POSTGRES_COMPOSE_FILE" \
  ps postgres

docker compose \
  --project-name codex-test-ai-factory \
  -f "$POSTGRES_COMPOSE_FILE" \
  exec -T postgres \
  pg_isready \
    -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
    -d "${AI_FACTORY_POSTGRES_DB:-ai_factory}"
