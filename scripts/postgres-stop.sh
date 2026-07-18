#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_COMPOSE_FILE="$REPOSITORY_ROOT/compose.postgres.yml"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

docker compose \
  --project-name codex-test-ai-factory \
  -f "$POSTGRES_COMPOSE_FILE" \
  stop postgres

echo "PostgreSQL stopped. The named data volume was retained."
