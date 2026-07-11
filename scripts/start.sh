
#!/usr/bin/env bash

set -euo pipefail

N8N_DIR="$HOME/Development/docker/n8n"

cd "$N8N_DIR"

docker compose up -d

docker compose ps

echo

echo "n8n should now be available at:"

echo "http://localhost:5678"

