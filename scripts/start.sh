
#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_DIR="$HOME/Development/docker/n8n"

cd "$N8N_DIR"

docker compose up -d

docker compose ps

echo

echo "n8n should now be available at:"

echo "http://localhost:5678"

echo

"$REPOSITORY_ROOT/scripts/ollama-start.sh"
