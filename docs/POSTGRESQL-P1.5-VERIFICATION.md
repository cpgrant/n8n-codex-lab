# PostgreSQL P1.5 cutover verification

Completed on 2026-07-18 using synthetic local data only. The n8n workflow was
never activated or published.

## Backup and migration

FastAPI was stopped before migration. The SQLite/artifact backup contained 31
runs, 16 approved strategy artifacts, and 13 quality-report artifacts; both
manifest verification and temporary restore testing passed.

The primary PostgreSQL dry run reported an empty eligible target and no data
writes. The confirmed import then matched all six application tables by count
and deterministic fingerprint and verified all 29 physical artifact checksums.
A custom-format pre-cutover PostgreSQL dump passed an isolated restore test.

The retained SQLite SHA-256 is:

```text
8b49b587c7e59a07bb7b9c76ad428aefe18b655ed2fa95aa792dd05ea0a32929
```

## Deterministic and restart verification

FastAPI ran with one worker against PostgreSQL. A deterministic synthetic run
reached `awaiting_review`; a separate run received an explicit synthetic
approval and created a retrievable Markdown artifact.

Both records survived a FastAPI restart. FastAPI was then stopped, the
PostgreSQL container was stopped and restarted without removing its named
volume, and both records remained retrievable afterward.

## Ollama and quality verification

The first two attempts failed safely with sanitized `502` responses because
the repository-specific Ollama listener was not persistent in the launching
shell. This confirmed durable provider-failure behavior without a partial
draft. The listener was then held in an attached session at
`127.0.0.1:11888`.

Run `b03d36e1-9218-4315-b438-03152eeb51ee` then completed with:

- `gemma4:31b` structured strategy generation;
- a separate `gemma4:31b` pro-quality critique;
- quality-report idempotent replay and durable retrieval;
- a retrievable advisory quality Markdown artifact;
- explicit approval by `synthetic-p15-reviewer`;
- a retrievable approved strategy Markdown artifact.

## n8n boundary

The existing n8n container was started with its authentication override. Stage
4 verification confirmed:

- Mac and container connectivity to the PostgreSQL-backed FastAPI service;
- presence of `CODEX TEST — AI Strategy Factory v0.1` in n8n;
- the checked-in workflow remained inactive and unavailable through MCP;
- the production form remained unpublished and returned HTTP 404.

No workflow execution, activation, publication, credential modification, or
real data was involved.

## Rollback and final selection

FastAPI was started normally with no database URL override and SQLite selected.
Pre-cutover run `11648de5-6e57-46bb-bfb0-cba94c217aa5` remained retrievable,
the PostgreSQL-only Ollama run returned HTTP 404, and the SQLite checksum was
unchanged.

The ignored `.env` was then set to
`AI_FACTORY_DEFAULT_DATABASE=postgresql`. The ordinary
`scripts/agent-start.sh` path retrieved the PostgreSQL-only Ollama run,
confirming PostgreSQL as the active local default without storing a second
password-bearing URL.

The post-cutover PostgreSQL database contained:

| Record type | Count |
| --- | ---: |
| Strategy runs | 36 |
| Idempotency records | 73 |
| Reviews | 21 |
| Strategy artifacts | 18 |
| Quality reports | 16 |
| Quality artifacts | 14 |

A post-cutover custom-format dump containing those records passed an isolated
restore test. SQLite and both PostgreSQL dumps are retained in ignored local
backup storage.

## Decision

P1.5 and Platform P1 are complete. PostgreSQL is the normal local FastAPI
backend. SQLite remains a tested rollback snapshot, but it no longer receives
new writes and will diverge from PostgreSQL after cutover.

PostgreSQL readiness does not authorize multiple workers by itself. Durable
job ownership, leases, bounded retries, and Ollama concurrency controls remain
a separate scaling checkpoint.
