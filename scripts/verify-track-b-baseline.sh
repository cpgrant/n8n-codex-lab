#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
ARTIFACT_DIR="$REPOSITORY_ROOT/artifacts/evaluations/track-b"
REPORT_FILE="$ARTIFACT_DIR/baseline-$STAMP.md"
LOG_DIR="$REPOSITORY_ROOT/tmp/track-b-baseline-$STAMP"
OVERALL_STATUS="PASS"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"
require_factory_auth_env

AI_FACTORY_PROVIDER="${AI_FACTORY_PROVIDER:-fake}"
AI_FACTORY_QUALITY_MODE="${AI_FACTORY_QUALITY_MODE:-basic}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11888}"
OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:31b}"
OLLAMA_QUALITY_MODEL="${OLLAMA_QUALITY_MODEL:-$OLLAMA_MODEL}"

mkdir -p "$ARTIFACT_DIR" "$LOG_DIR"

for command in curl docker git jq node uv; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is not available: $command" >&2
    exit 2
  fi
done

BRANCH="$(git -C "$REPOSITORY_ROOT" branch --show-current)"
COMMIT="$(git -C "$REPOSITORY_ROOT" rev-parse --short HEAD)"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$REPORT_FILE" <<EOF
# Track B baseline verification

- Started: \`$STARTED_AT\`
- Git branch: \`$BRANCH\`
- Git commit: \`$COMMIT\`
- Strategy provider: \`$AI_FACTORY_PROVIDER\`
- Quality mode: \`$AI_FACTORY_QUALITY_MODE\`
- Generation model: \`$OLLAMA_MODEL\`
- Quality model: \`$OLLAMA_QUALITY_MODEL\`
- Data boundary: synthetic test data only

No authentication token values are written to this report.

## Automated checks

| Check | Result | Duration |
| --- | --- | ---: |
EOF

finish_report() {
  local exit_status=$?
  local finished_at
  finished_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  if [[ $exit_status -ne 0 ]]; then
    OVERALL_STATUS="FAIL"
  fi

  cat >> "$REPORT_FILE" <<EOF

## Result

- Overall status: **$OVERALL_STATUS**
- Finished: \`$finished_at\`
- Detailed command logs: \`tmp/$(basename "$LOG_DIR")/\`

The detailed logs and this report are ignored by Git. Review the first failed
check before proceeding with Track B implementation.
EOF

  echo
  echo "Track B baseline result: $OVERALL_STATUS"
  echo "Report: $REPORT_FILE"
  echo "Logs: $LOG_DIR"
}
trap finish_report EXIT

run_check() {
  local slug="$1"
  local label="$2"
  shift 2

  local started elapsed log_file
  log_file="$LOG_DIR/$slug.log"
  started=$SECONDS

  echo
  echo "==> $label"
  if "$@" >"$log_file" 2>&1; then
    elapsed=$((SECONDS - started))
    cat "$log_file"
    printf '| %s | PASS | %ss |\n' "$label" "$elapsed" >> "$REPORT_FILE"
    return 0
  fi

  elapsed=$((SECONDS - started))
  OVERALL_STATUS="FAIL"
  cat "$log_file" >&2
  printf '| %s | FAIL | %ss |\n' "$label" "$elapsed" >> "$REPORT_FILE"
  echo "Failed: $label" >&2
  return 1
}

check_runtime_configuration() {
  if [[ "$AI_FACTORY_PROVIDER" != "ollama" ]]; then
    echo "Track B baseline requires AI_FACTORY_PROVIDER=ollama; found $AI_FACTORY_PROVIDER." >&2
    return 1
  fi
  if [[ "$AI_FACTORY_QUALITY_MODE" != "pro" ]]; then
    echo "Track B baseline requires AI_FACTORY_QUALITY_MODE=pro; found $AI_FACTORY_QUALITY_MODE." >&2
    return 1
  fi

  curl -fsS --max-time 5 http://127.0.0.1:8000/health \
    | jq -e '.status == "ok"' >/dev/null
  curl -fsS --max-time 5 "$OLLAMA_BASE_URL/api/tags" \
    | jq -e --arg generation "$OLLAMA_MODEL" --arg quality "$OLLAMA_QUALITY_MODEL" '
        (.models | map(.name) | index($generation) != null)
        and (.models | map(.name) | index($quality) != null)
      ' >/dev/null
  docker inspect -f '{{.State.Running}}' n8n | grep -Fxq true
  docker exec n8n sh -c '
    test "${#AI_FACTORY_SERVICE_TOKEN}" -ge 32 &&
    test "${#AI_FACTORY_REVIEW_TOKEN}" -ge 32 &&
    test "$AI_FACTORY_SERVICE_TOKEN" != "$AI_FACTORY_REVIEW_TOKEN"
  '

  echo "Runtime configuration is healthy (secret values not displayed)."
}

run_python_tests() {
  cd "$REPOSITORY_ROOT/agent-service"
  uv run pytest -q
}

run_live_ollama_baseline() {
  EXPECTED_QUALITY_MODE="$AI_FACTORY_QUALITY_MODE" \
    "$REPOSITORY_ROOT/scripts/agent-smoke-stage7.sh"
}

echo "Track B baseline verification"
echo "This performs one synthetic Ollama generation and quality critique."
echo "With gemma4:31b, the live check may take several minutes."

run_check runtime "Runtime configuration and service health" \
  check_runtime_configuration
run_check stage4 "Stage 4 workflow safety and connectivity" \
  "$REPOSITORY_ROOT/scripts/verify-stage4.sh"
run_check stage8 "Stage 8 flexible-intake contract" \
  node "$REPOSITORY_ROOT/scripts/verify-stage8-intake.js"
run_check tests "Automated FastAPI and Stage 9.1 tests" \
  run_python_tests
run_check live-ollama "Live Ollama generation and pro quality report" \
  run_live_ollama_baseline

if [[ -n "$(git -C "$REPOSITORY_ROOT" status --short)" ]]; then
  printf '| Git working tree cleanliness | INFO: changes present | 0s |\n' \
    >> "$REPORT_FILE"
  echo
  echo "Working tree changes are present; inspect them before committing."
else
  printf '| Git working tree cleanliness | PASS | 0s |\n' >> "$REPORT_FILE"
fi

echo
echo "Automated baseline checks passed."
echo "One manual synthetic n8n form walkthrough remains before Stage 9.5-lite."
