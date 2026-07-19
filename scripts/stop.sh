
#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_COMPOSE_FILE="$REPOSITORY_ROOT/compose.n8n.yml"

"$REPOSITORY_ROOT/scripts/ollama-stop.sh"

echo

docker compose \
  --project-name n8n \
  -f "$N8N_COMPOSE_FILE" \
  down

echo

echo "Remaining running containers:"

docker ps
