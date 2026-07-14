#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
ACTOR_ID="synthetic-stage9-reviewer"
STAMP="$(date +%Y%m%d%H%M%S)-$$"
RESPONSE_FILE="$(mktemp)"

source "$REPOSITORY_ROOT/scripts/auth-headers.sh"
load_service_auth
load_review_auth "$ACTOR_ID"

trap 'rm -f "$RESPONSE_FILE"' EXIT

expect_error() {
  local expected_status="$1"
  local expected_code="$2"
  shift 2
  local actual_status
  actual_status="$(curl -sS --max-time 15 -o "$RESPONSE_FILE" -w '%{http_code}' "$@")"
  if [[ "$actual_status" != "$expected_status" ]]; then
    echo "Expected HTTP $expected_status, received $actual_status." >&2
    return 1
  fi
  jq -e --arg code "$expected_code" '.error.code == $code' \
    "$RESPONSE_FILE" >/dev/null
}

echo "Checking fail-closed authentication paths ..."
expect_error 401 AUTHENTICATION_REQUIRED \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/00000000-0000-0000-0000-000000000000"
expect_error 401 AUTHENTICATION_INVALID \
  -H "Authorization: Bearer invalid-synthetic-token" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/00000000-0000-0000-0000-000000000000"
expect_error 403 AUTHORIZATION_DENIED \
  -X POST \
  -H "Authorization: Bearer $AI_FACTORY_REVIEW_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs"

echo "Creating an authenticated synthetic run ..."
curl -fsS --max-time 30 \
  "${SERVICE_AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage9-auth-create-$STAMP" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$RESPONSE_FILE"
RUN_ID="$(jq -er '.data.run_id' "$RESPONSE_FILE")"

echo "Checking the separate review scope and actor binding ..."
expect_error 403 AUTHORIZATION_DENIED \
  -X POST \
  "${SERVICE_AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  --data-binary "{\"decision\":\"rejected\",\"reviewer\":\"$ACTOR_ID\",\"comment\":\"Synthetic denial check.\"}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review"
expect_error 403 AUTHORIZATION_DENIED \
  -X POST \
  -H "Authorization: Bearer $AI_FACTORY_REVIEW_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary "{\"decision\":\"rejected\",\"reviewer\":\"$ACTOR_ID\",\"comment\":\"Synthetic missing actor check.\"}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review"
expect_error 403 AUTHORIZATION_DENIED \
  -X POST \
  "${REVIEW_AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  --data-binary '{"decision":"rejected","reviewer":"different-synthetic-actor","comment":"Synthetic mismatch check."}' \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review"

curl -fsS --max-time 15 \
  -X POST \
  "${REVIEW_AUTH_ARGS[@]}" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage9-auth-review-$STAMP" \
  --data-binary "{\"decision\":\"rejected\",\"reviewer\":\"$ACTOR_ID\",\"comment\":\"Rejected by the synthetic Stage 9.1 verification.\"}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/review" > "$RESPONSE_FILE"
jq -e --arg actor "$ACTOR_ID" '
  .data.status == "rejected"
  and .data.review.decision == "rejected"
  and .data.review.reviewer == $actor
  and .data.artifact == null
' "$RESPONSE_FILE" >/dev/null

curl -fsS --max-time 15 \
  "${SERVICE_AUTH_ARGS[@]}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID" > "$RESPONSE_FILE"
jq -e --arg actor "$ACTOR_ID" '
  .data.status == "rejected"
  and .data.review.reviewer == $actor
  and .data.artifact == null
' "$RESPONSE_FILE" >/dev/null

echo "Checking the exported workflow authentication boundary ..."
jq -e '
  .name | startswith("CODEX TEST")
' "$REPOSITORY_ROOT/workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json" >/dev/null
jq -e '
  .active == false
  and .settings.availableInMCP == false
  and .settings.saveDataErrorExecution == "none"
  and .settings.saveDataSuccessExecution == "none"
  and .settings.saveManualExecutions == true
  and ([.nodes[] | select(has("credentials"))] | length) == 0
  and ([.nodes[] | select(.name == "Strategy Brief Form")][0].typeVersion >= 2.6)
  and ([.nodes[] | select(.name == "Strategy Brief Form")][0].parameters.authentication == "n8nUserAuth")
' "$REPOSITORY_ROOT/workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json" >/dev/null

echo "Stage 9.1 authentication verification passed for synthetic run: $RUN_ID"
