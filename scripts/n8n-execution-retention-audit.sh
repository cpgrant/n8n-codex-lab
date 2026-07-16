#!/usr/bin/env bash

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RETENTION_DAYS="${N8N_SYNTHETIC_EXECUTION_RETENTION_DAYS:-14}"
WAITING_HOURS="${N8N_SYNTHETIC_WAITING_RETENTION_HOURS:-24}"

if [[ ! "$RETENTION_DAYS" =~ ^[1-9][0-9]*$ ]]; then
  echo "Retention days must be a positive integer." >&2
  exit 2
fi
if [[ ! "$WAITING_HOURS" =~ ^[1-9][0-9]*$ ]]; then
  echo "Waiting retention hours must be a positive integer." >&2
  exit 2
fi

SNAPSHOT="$(mktemp "${TMPDIR:-/tmp}/n8n-stage9-3-audit.XXXXXX.sqlite")"
trap 'rm -f "$SNAPSHOT"' EXIT

docker cp n8n:/home/node/.n8n/database.sqlite "$SNAPSHOT" >/dev/null

echo "Stage 9.3-lite n8n execution-retention audit"
echo "Scope: workflows named CODEX TEST%"
echo "Completed retention: ${RETENTION_DAYS} days"
echo "Stale waiting threshold: ${WAITING_HOURS} hours"
echo

sqlite3 -header -column "$SNAPSHOT" "
SELECT
  e.id,
  e.mode,
  e.status,
  e.startedAt,
  e.stoppedAt,
  w.name AS workflow_name
FROM execution_entity e
JOIN workflow_entity w ON w.id = e.workflowId
WHERE w.name LIKE 'CODEX TEST%'
  AND e.deletedAt IS NULL
  AND (
    (
      e.status <> 'waiting'
      AND COALESCE(e.stoppedAt, e.startedAt, e.createdAt)
        < datetime('now', '-${RETENTION_DAYS} days')
    )
    OR (
      e.status = 'waiting'
      AND COALESCE(e.startedAt, e.createdAt)
        < datetime('now', '-${WAITING_HOURS} hours')
    )
  )
ORDER BY e.id;
"

COUNT="$(sqlite3 "$SNAPSHOT" "
SELECT COUNT(*)
FROM execution_entity e
JOIN workflow_entity w ON w.id = e.workflowId
WHERE w.name LIKE 'CODEX TEST%'
  AND e.deletedAt IS NULL
  AND (
    (
      e.status <> 'waiting'
      AND COALESCE(e.stoppedAt, e.startedAt, e.createdAt)
        < datetime('now', '-${RETENTION_DAYS} days')
    )
    OR (
      e.status = 'waiting'
      AND COALESCE(e.startedAt, e.createdAt)
        < datetime('now', '-${WAITING_HOURS} hours')
    )
  );
")"

echo
echo "Candidates: $COUNT"
echo "This command is read-only. Delete only confirmed candidates from n8n's"
echo "Executions view after checking that no form test is still active."
