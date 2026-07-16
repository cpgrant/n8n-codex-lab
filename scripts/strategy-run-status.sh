#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
RUN_ID="${1:-}"
RESPONSE_FILE="$(mktemp)"

trap 'rm -f "$RESPONSE_FILE"' EXIT

if [[ ! "$RUN_ID" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$ ]]; then
  echo "Usage: scripts/strategy-run-status.sh <run-id>" >&2
  echo "The run ID must be a UUID displayed by the strategy workflow." >&2
  exit 2
fi

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"
require_factory_auth_env
source "$REPOSITORY_ROOT/scripts/auth-headers.sh"
load_service_auth

curl -fsS --max-time 15 \
  "${SERVICE_AUTH_ARGS[@]}" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs/$RUN_ID" \
  > "$RESPONSE_FILE"

jq -e --arg run_id "$RUN_ID" '.data.run_id == $run_id' \
  "$RESPONSE_FILE" >/dev/null

STATUS="$(jq -er '.data.status' "$RESPONSE_FILE")"
QUALITY_FILENAME="$(jq -r '.data.quality_artifact.filename // empty' "$RESPONSE_FILE")"
STRATEGY_FILENAME="$(jq -r '.data.artifact.filename // empty' "$RESPONSE_FILE")"

echo "Run ID: $RUN_ID"
echo "Status: $STATUS"

if [[ -n "$QUALITY_FILENAME" ]]; then
  echo "Quality report: artifacts/quality-reports/$QUALITY_FILENAME"
else
  echo "Quality report: not created"
fi

if [[ -n "$STRATEGY_FILENAME" ]]; then
  echo "Approved strategy: artifacts/$STRATEGY_FILENAME"
else
  echo "Approved strategy: not created"
fi

case "$STATUS" in
  awaiting_review)
    if [[ -n "$QUALITY_FILENAME" ]]; then
      echo "Next action: resume or repeat only the human-review step; do not create a new run."
    else
      echo "Next action: generate the quality report for this stored draft; do not create a new run."
    fi
    ;;
  artifact_created)
    echo "Next action: open the approved strategy path shown above."
    ;;
  rejected)
    echo "Next action: none; rejection is terminal and no approved strategy is created."
    ;;
  failed)
    echo "Next action: inspect the local service logs before deciding whether to create a new run."
    ;;
  approved)
    echo "Next action: retry the original review request to resume artifact rendering; do not create a new decision."
    ;;
  *)
    echo "Next action: consult docs/TROUBLESHOOTING.md before retrying."
    ;;
esac
