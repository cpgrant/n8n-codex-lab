#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
source "$REPOSITORY_ROOT/scripts/auth-headers.sh"
load_service_auth
IDEMPOTENCY_KEY="stage2-smoke-$(date +%Y%m%d%H%M%S)"
RESPONSE_FILE="$(mktemp)"

trap 'rm -f "$RESPONSE_FILE"' EXIT

curl -fsS --max-time 10 \
  "${SERVICE_AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$RESPONSE_FILE"

RUN_ID="$(jq -er '.data.run_id' "$RESPONSE_FILE")"
jq -e '.data.status == "awaiting_review" and .data.strategy.provider == "fake"' \
  "$RESPONSE_FILE" >/dev/null

curl -fsS --max-time 10 \
  "${SERVICE_AUTH_ARGS[@]}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID" \
  | jq -e '.data.status == "awaiting_review" and .data.strategy.provider == "fake"' \
  >/dev/null

echo "Stage 2 smoke test passed for synthetic run: $RUN_ID"
