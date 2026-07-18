#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_WAIT_ATTEMPTS="${DOCKER_WAIT_ATTEMPTS:-60}"

if ! docker info >/dev/null 2>&1; then
  if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Docker is not available. Start the Docker engine and retry." >&2
    exit 1
  fi
  echo "Starting Docker Desktop ..."
  open -a Docker
  for ((attempt = 1; attempt <= DOCKER_WAIT_ATTEMPTS; attempt++)); do
    if docker info >/dev/null 2>&1; then
      break
    fi
    if ((attempt == DOCKER_WAIT_ATTEMPTS)); then
      echo "Docker Desktop did not become ready within 120 seconds." >&2
      exit 1
    fi
    sleep 2
  done
fi

echo "Docker is ready."
"$REPOSITORY_ROOT/scripts/postgres-start.sh"
"$REPOSITORY_ROOT/scripts/start.sh"

if curl -fsS --max-time 3 http://127.0.0.1:8000/health \
  | jq -e '.status == "ok" and .service == "ai-strategy-factory"' \
  >/dev/null 2>&1; then
  echo "FastAPI is already healthy at http://127.0.0.1:8000"
  exit 0
fi

echo "Starting FastAPI in the foreground. Press Ctrl-C to stop FastAPI."
exec "$REPOSITORY_ROOT/scripts/agent-start.sh"
