#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11888}"
OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:31b}"
STAMP="$(date +%Y%m%d%H%M%S)-$$"
RESPONSE_FILE="$(mktemp)"

trap 'rm -f "$RESPONSE_FILE"' EXIT

echo "Checking Ollama at $OLLAMA_BASE_URL ..."
curl -fsS --max-time 5 "$OLLAMA_BASE_URL/api/tags" \
  | jq -e --arg model "$OLLAMA_MODEL" \
      '.models | map(.name) | index($model) != null' >/dev/null

echo "Generating one synthetic strategy with $OLLAMA_MODEL ..."
curl -fsS --max-time 330 \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: stage6-ollama-$STAMP" \
  --data-binary "@$REPOSITORY_ROOT/examples/strategy-brief.synthetic.json" \
  "$AI_FACTORY_HOST_URL/v1/strategy-runs" > "$RESPONSE_FILE"

RUN_ID="$(jq -er '.data.run_id' "$RESPONSE_FILE")"
jq -e '
  .data.status == "awaiting_review"
  and .data.strategy.provider == "ollama"
  and (.data.strategy.executive_summary | length > 0)
  and ((.data.strategy.objectives | length) >= 2)
  and ((.data.strategy.strategic_choices | length) >= 2)
  and ((.data.strategy.recommended_initiatives | length) >= 3)
  and ((.data.strategy.success_measures | length) >= 2)
  and ((.data.strategy.next_steps | length) >= 3)
' "$RESPONSE_FILE" >/dev/null

echo "Stage 6 Ollama smoke test passed for synthetic run: $RUN_ID"
