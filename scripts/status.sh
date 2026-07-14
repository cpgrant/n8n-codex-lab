#!/usr/bin/env bash
set -euo pipefail

echo "Docker status:"
docker compose \
  -f "$HOME/Development/docker/n8n/docker-compose.yml" \
  ps

echo
echo "n8n version:"
docker exec n8n n8n --version

echo
echo "FFmpeg version:"
docker exec n8n ffmpeg -version 2>&1 | head -n 1

echo
echo "Stage 9.1 n8n authentication environment:"
docker exec n8n sh -c '
  if [ "${#AI_FACTORY_SERVICE_TOKEN}" -ge 32 ] &&
     [ "${#AI_FACTORY_REVIEW_TOKEN}" -ge 32 ] &&
     [ "$AI_FACTORY_SERVICE_TOKEN" != "$AI_FACTORY_REVIEW_TOKEN" ]; then
    echo configured
  else
    echo not-configured
    exit 1
  fi
'

echo
echo "Codex MCP servers:"
codex mcp list
