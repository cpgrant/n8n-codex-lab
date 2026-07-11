
#!/usr/bin/env bash

set -euo pipefail

cd "$HOME/Development/docker/n8n"

docker compose down

echo

echo "Remaining running containers:"

docker ps

