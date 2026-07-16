#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPOSITORY_ROOT/agent-service/.uv-cache}"

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

if [[ "${AI_FACTORY_DATA_DIR:-}" != /* ]]; then
  export AI_FACTORY_DATA_DIR="$REPOSITORY_ROOT/agent-service/${AI_FACTORY_DATA_DIR:-../data}"
fi
if [[ "${AI_FACTORY_ARTIFACT_DIR:-}" != /* ]]; then
  export AI_FACTORY_ARTIFACT_DIR="$REPOSITORY_ROOT/agent-service/${AI_FACTORY_ARTIFACT_DIR:-../artifacts}"
fi

cd "$REPOSITORY_ROOT"
exec uv run --project "$REPOSITORY_ROOT/agent-service" \
  python -m ai_factory.backup "$@"
