
#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$REPOSITORY_ROOT/scripts/ollama-stop.sh"

echo

cd "$HOME/Development/docker/n8n"

docker compose down

echo

echo "Remaining running containers:"

docker ps
