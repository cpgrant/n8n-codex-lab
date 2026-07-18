#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_COMPOSE_FILE="$REPOSITORY_ROOT/compose.postgres.yml"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ -z "${AI_FACTORY_POSTGRES_PASSWORD:-}" || ${#AI_FACTORY_POSTGRES_PASSWORD} -lt 32 ]]; then
  echo "AI_FACTORY_POSTGRES_PASSWORD must be set to at least 32 characters." >&2
  echo "Generate one with: openssl rand -hex 32" >&2
  exit 2
fi

docker compose \
  --project-name codex-test-ai-factory \
  -f "$POSTGRES_COMPOSE_FILE" \
  up -d --wait postgres

"$REPOSITORY_ROOT/scripts/postgres-status.sh"
