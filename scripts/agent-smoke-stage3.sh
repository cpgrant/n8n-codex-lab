#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
STAMP="$(date +%Y%m%d%H%M%S)"
CREATE_RESPONSE="$(mktemp)"
REVIEW_RESPONSE="$(mktemp)"
ARTIFACT_RESPONSE="$(mktemp)"

trap 'rm -f "$CREATE_RESPONSE" "$REVIEW_RESPONSE" "$ARTIFACT_RESPONSE"' EXIT

curl -fsS --max-time 10 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage3-create-$STAMP" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$CREATE_RESPONSE"

RUN_ID="$(jq -er '.data.run_id' "$CREATE_RESPONSE")"

curl -fsS --max-time 10 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage3-approve-$STAMP" \
  --data-binary '{"decision":"approved","reviewer":"synthetic-stage3-reviewer","comment":"Approved by the synthetic Stage 3 smoke test."}' \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review" > "$REVIEW_RESPONSE"

jq -e '.data.status == "artifact_created" and .data.review.decision == "approved" and .data.artifact.media_type == "text/markdown"' \
  "$REVIEW_RESPONSE" >/dev/null

curl -fsS --max-time 10 \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/artifact" \
  > "$ARTIFACT_RESPONSE"

rg -q '^## Executive summary$' "$ARTIFACT_RESPONSE"
rg -q '^## Next steps$' "$ARTIFACT_RESPONSE"
rg -q 'synthetic Stage 3 smoke test' "$ARTIFACT_RESPONSE"

echo "Stage 3 smoke test passed for approved synthetic run: $RUN_ID"
