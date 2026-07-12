#!/usr/bin/env bash

set -euo pipefail

AI_FACTORY_HOST_URL="${AI_FACTORY_HOST_URL:-http://127.0.0.1:8000}"

curl -fsS --max-time 5 "${AI_FACTORY_HOST_URL%/}/health"
echo
