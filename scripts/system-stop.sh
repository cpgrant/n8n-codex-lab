#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Stop FastAPI with Ctrl-C in the terminal running system-start.sh."
echo
"$REPOSITORY_ROOT/scripts/stop.sh"
echo
"$REPOSITORY_ROOT/scripts/postgres-stop.sh"

echo
echo "The n8n and PostgreSQL volumes, SQLite rollback file, and backups were retained."
