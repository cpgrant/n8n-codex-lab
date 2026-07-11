
#!/usr/bin/env bash

set -euo pipefail

echo "Checking n8n..."

curl -fsS http://localhost:5678 >/dev/null

echo "n8n is reachable."

echo

echo "Checking MCP registration..."

codex mcp list | grep -q "n8n"

echo "n8n MCP server is registered with Codex."

echo

if [[ -n "${N8N_MCP_TOKEN:-}" ]]; then

  echo "N8N_MCP_TOKEN is set in this shell."

else

  echo "N8N_MCP_TOKEN is not set in this shell."

  exit 1

fi

