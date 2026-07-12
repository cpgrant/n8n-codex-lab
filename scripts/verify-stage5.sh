#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
STAMP="$(date +%Y%m%d%H%M%S)-$$"
CREATE_KEY="stage5-create-$STAMP"
REVIEW_KEY="stage5-reject-$STAMP"
CREATE_RESPONSE="$(mktemp)"
CREATE_REPLAY="$(mktemp)"
REVIEW_RESPONSE="$(mktemp)"
REVIEW_REPLAY="$(mktemp)"
READ_RESPONSE="$(mktemp)"
ARTIFACT_RESPONSE="$(mktemp)"

trap 'rm -f "$CREATE_RESPONSE" "$CREATE_REPLAY" "$REVIEW_RESPONSE" "$REVIEW_REPLAY" "$READ_RESPONSE" "$ARTIFACT_RESPONSE"' EXIT

echo "Running Stage 4 safety and connectivity checks..."
"$REPOSITORY_ROOT/scripts/verify-stage4.sh"

echo "Creating one synthetic strategy run..."
curl -fsS --max-time 15 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $CREATE_KEY" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$CREATE_RESPONSE"

RUN_ID="$(jq -er '.data.run_id' "$CREATE_RESPONSE")"
jq -e '
  .data.status == "awaiting_review"
  and .data.strategy.provider == "fake"
  and .meta.idempotent_replay == false
' "$CREATE_RESPONSE" >/dev/null

echo "Checking create idempotency replay..."
curl -fsS --max-time 15 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $CREATE_KEY" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$CREATE_REPLAY"

jq -e --arg run_id "$RUN_ID" '
  .data.run_id == $run_id
  and .data.status == "awaiting_review"
  and .meta.idempotent_replay == true
' "$CREATE_REPLAY" >/dev/null

echo "Rejecting the synthetic draft..."
curl -fsS --max-time 15 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $REVIEW_KEY" \
  --data-binary '{"decision":"rejected","reviewer":"synthetic-stage5-reviewer","comment":"Rejected by the synthetic Stage 5 operational verification."}' \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review" > "$REVIEW_RESPONSE"

jq -e '
  .data.status == "rejected"
  and .data.review.decision == "rejected"
  and .data.artifact == null
  and .meta.idempotent_replay == false
' "$REVIEW_RESPONSE" >/dev/null

echo "Checking review idempotency replay..."
curl -fsS --max-time 15 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $REVIEW_KEY" \
  --data-binary '{"decision":"rejected","reviewer":"synthetic-stage5-reviewer","comment":"Rejected by the synthetic Stage 5 operational verification."}' \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review" > "$REVIEW_REPLAY"

jq -e '
  .data.status == "rejected"
  and .meta.idempotent_replay == true
' "$REVIEW_REPLAY" >/dev/null

echo "Checking durable rejected-run retrieval..."
curl -fsS --max-time 15 \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID" > "$READ_RESPONSE"

jq -e '
  .data.status == "rejected"
  and .data.review.decision == "rejected"
  and .data.artifact == null
' "$READ_RESPONSE" >/dev/null

echo "Checking that rejection produced no approved artifact..."
ARTIFACT_STATUS="$(curl -sS --max-time 15 -o "$ARTIFACT_RESPONSE" -w '%{http_code}' \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/artifact")"
if [[ "$ARTIFACT_STATUS" != "409" ]]; then
  echo "Expected rejected artifact request status 409, received $ARTIFACT_STATUS."
  exit 1
fi
jq -e '.error.code == "ARTIFACT_NOT_READY"' "$ARTIFACT_RESPONSE" >/dev/null

if [[ -e "$REPOSITORY_ROOT/artifacts/strategy-$RUN_ID.md" ]]; then
  echo "A rejected run unexpectedly created an artifact."
  exit 1
fi

echo "Stage 5 operational checks passed for rejected synthetic run: $RUN_ID"
echo "Use this run ID for the documented restart-persistence check."
