
#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_DIR="$HOME/Development/docker/n8n"
N8N_COMPOSE_FILE="$N8N_DIR/docker-compose.yml"
AUTH_COMPOSE_FILE="$REPOSITORY_ROOT/compose.n8n-auth.yml"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"
require_factory_auth_env

docker compose \
  -f "$N8N_COMPOSE_FILE" \
  -f "$AUTH_COMPOSE_FILE" \
  up -d

docker compose \
  -f "$N8N_COMPOSE_FILE" \
  -f "$AUTH_COMPOSE_FILE" \
  ps

echo

echo "n8n should now be available at:"

echo "http://localhost:5678"

echo

"$REPOSITORY_ROOT/scripts/ollama-start.sh"
