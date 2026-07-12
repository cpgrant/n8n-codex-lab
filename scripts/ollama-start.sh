#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11888}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://$OLLAMA_HOST}"
PID_FILE="$REPOSITORY_ROOT/tmp/ollama.pid"
LOG_FILE="$REPOSITORY_ROOT/tmp/ollama.log"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed or is not available on PATH."
  exit 1
fi

mkdir -p "$REPOSITORY_ROOT/tmp"

if curl -fsS --max-time 2 "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; then
  echo "Ollama is already available at $OLLAMA_BASE_URL"
  exit 0
fi

if [[ -f "$PID_FILE" ]]; then
  EXISTING_PID="$(cat "$PID_FILE")"
  if kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "A repository-managed Ollama process is running but is not healthy."
    echo "Inspect $LOG_FILE or run scripts/ollama-stop.sh before retrying."
    exit 1
  fi
  rm -f "$PID_FILE"
fi

echo "Starting Ollama at $OLLAMA_BASE_URL ..."
OLLAMA_HOST="$OLLAMA_HOST" nohup ollama serve >"$LOG_FILE" 2>&1 &
OLLAMA_PID=$!
echo "$OLLAMA_PID" > "$PID_FILE"

for _ in {1..30}; do
  if curl -fsS --max-time 2 "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; then
    echo "Ollama is available at $OLLAMA_BASE_URL (PID $OLLAMA_PID)"
    exit 0
  fi
  if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
    echo "Ollama exited during startup. Inspect $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
  sleep 1
done

echo "Ollama did not become ready within 30 seconds. Inspect $LOG_FILE"
exit 1
