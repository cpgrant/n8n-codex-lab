#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW_FILE="$REPOSITORY_ROOT/workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json"

echo "Checking the repository workflow safety flags..."
jq -e '
  .name == "CODEX TEST — AI Strategy Factory v0.1"
  and .active == false
  and .settings.availableInMCP == false
  and ([.nodes[].credentials?] | all(. == null))
' "$WORKFLOW_FILE" >/dev/null

echo "Checking n8n on the Mac..."
curl -fsS --max-time 5 http://127.0.0.1:5678 >/dev/null

echo "Checking the agent service on the Mac..."
curl -fsS --max-time 5 http://127.0.0.1:8000/health >/dev/null

echo "Checking the agent service from the n8n container..."
docker exec n8n \
  node -e "fetch('http://host.docker.internal:8000/health').then(async (response) => { if (!response.ok) process.exit(1); const body = await response.json(); if (body.status !== 'ok') process.exit(1); }).catch(() => process.exit(1))"

echo "Checking the inactive workflow is present in n8n..."
docker exec n8n n8n list:workflow \
  | grep -Fq 'CodexStrategyV01|CODEX TEST — AI Strategy Factory v0.1'

echo "Checking the production form remains unpublished..."
FORM_STATUS="$(curl -sS -o /dev/null -w '%{http_code}' \
  http://127.0.0.1:5678/form/codex-test-ai-strategy-factory-v01)"
if [[ "$FORM_STATUS" != "404" ]]; then
  echo "Expected unpublished form status 404, received $FORM_STATUS."
  exit 1
fi

echo "Stage 4 connectivity checks passed."
