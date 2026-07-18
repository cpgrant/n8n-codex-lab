#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTGRES_CONTAINER="codex-test-ai-factory-postgres"
POSTGRES_DATABASE="ai_factory"
OUTPUT=""

source "$REPOSITORY_ROOT/scripts/load-env.sh"
load_repository_env "$REPOSITORY_ROOT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --database)
      POSTGRES_DATABASE="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 [--database NAME] --output FILE" >&2
      exit 2
      ;;
  esac
done

if [[ ! "$POSTGRES_DATABASE" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
  echo "Invalid PostgreSQL database name." >&2
  exit 2
fi
if [[ -z "$OUTPUT" ]]; then
  echo "--output is required." >&2
  exit 2
fi
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing backup: $OUTPUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
docker exec "$POSTGRES_CONTAINER" \
  pg_dump -U "${AI_FACTORY_POSTGRES_USER:-ai_factory}" \
  -d "$POSTGRES_DATABASE" --format=custom --no-owner --no-privileges \
  > "$OUTPUT"
chmod 600 "$OUTPUT"
docker exec -i "$POSTGRES_CONTAINER" pg_restore --list < "$OUTPUT" >/dev/null
echo "$OUTPUT"
