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
echo "Codex MCP servers:"
codex mcp list
