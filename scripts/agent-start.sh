#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPOSITORY_ROOT/agent-service/.uv-cache}"

cd "$REPOSITORY_ROOT/agent-service"

exec uv run uvicorn ai_factory.main:app \
  --host "${AI_FACTORY_HOST:-127.0.0.1}" \
  --port "${AI_FACTORY_PORT:-8000}" \
  --workers 1
