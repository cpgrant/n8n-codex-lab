#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
EXPECTED_QUALITY_MODE="${EXPECTED_QUALITY_MODE:-basic}"
STAMP="$(date +%Y%m%d%H%M%S)-$$"
CREATE_RESPONSE="$(mktemp)"
QUALITY_RESPONSE="$(mktemp)"
QUALITY_REPLAY="$(mktemp)"
READ_RESPONSE="$(mktemp)"

trap 'rm -f "$CREATE_RESPONSE" "$QUALITY_RESPONSE" "$QUALITY_REPLAY" "$READ_RESPONSE"' EXIT

echo "Creating one synthetic strategy draft ..."
curl -fsS --max-time 330 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage7-create-$STAMP" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$CREATE_RESPONSE"

RUN_ID="$(jq -er '.data.run_id' "$CREATE_RESPONSE")"

echo "Generating the $EXPECTED_QUALITY_MODE quality report ..."
curl -fsS --max-time 330 \
  -X POST \
  -H "Idempotency-Key: stage7-quality-$STAMP" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/quality-report" \
  > "$QUALITY_RESPONSE"

jq -e --arg mode "$EXPECTED_QUALITY_MODE" '
  .data.status == "awaiting_review"
  and .data.quality_report.mode == $mode
  and (.data.quality_report.overall_score >= 0)
  and (.data.quality_report.overall_score <= 100)
  and ([.data.quality_report.checks[] | (. >= 0 and . <= 10)] | all)
  and (.data.quality_report.checks | length) == 7
  and (.data.quality_report.draft_checksum | test("^sha256:[0-9a-f]{64}$"))
  and .meta.idempotent_replay == false
' "$QUALITY_RESPONSE" >/dev/null

echo "Checking quality-report idempotency ..."
curl -fsS --max-time 330 \
  -X POST \
  -H "Idempotency-Key: stage7-quality-$STAMP" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID/quality-report" \
  > "$QUALITY_REPLAY"

jq -e --slurpfile original "$QUALITY_RESPONSE" '
  .data == $original[0].data
  and .meta.idempotent_replay == true
' "$QUALITY_REPLAY" >/dev/null

echo "Checking durable report retrieval ..."
curl -fsS --max-time 15 \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID" > "$READ_RESPONSE"

jq -e --slurpfile quality "$QUALITY_RESPONSE" '
  .data.status == "awaiting_review"
  and .data.quality_report == $quality[0].data.quality_report
' "$READ_RESPONSE" >/dev/null

echo "Stage 7 quality-report smoke test passed for synthetic run: $RUN_ID"
