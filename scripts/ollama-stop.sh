#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$REPOSITORY_ROOT/tmp/ollama.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No repository-managed Ollama process is recorded."
  exit 0
fi

OLLAMA_PID="$(cat "$PID_FILE")"
if kill -0 "$OLLAMA_PID" 2>/dev/null; then
  echo "Stopping repository-managed Ollama process $OLLAMA_PID ..."
  kill "$OLLAMA_PID"
  for _ in {1..10}; do
    if ! kill -0 "$OLLAMA_PID" 2>/dev/null; then
      break
    fi
    sleep 1
  done
fi

rm -f "$PID_FILE"
echo "Repository-managed Ollama process stopped."
