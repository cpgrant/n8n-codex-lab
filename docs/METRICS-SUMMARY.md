# Existing metrics summary

Snapshot date: **2026-07-20**

This page consolidates measurements that already exist in the repository. It
does not treat synthetic technical checks as evidence of real-world strategy
quality, user adoption, or commercial impact.

## At a glance

| Area | Existing result | Scope and evidence |
| --- | ---: | --- |
| Automated service tests | **108 passed, 8 skipped, 0 failed** | Local run on 2026-07-20; the eight skips require an opt-in live PostgreSQL test URL. Source: `agent-service/tests/` |
| API surface | **8 HTTP operations** | One health operation and seven strategy lifecycle operations. Source: `agent-service/src/ai_factory/main.py` and `docs/API.md` |
| Current n8n workflow | **20 nodes** | Six Code, seven Form, one Form Trigger, three HTTP Request, two Switch, and one Sticky Note node. Source: tracked workflow export |
| Workflow safety flags | **0 credential-bearing nodes; inactive; unavailable through MCP** | Current export has `active: false`, `availableInMCP: false`, and production success/error execution saving disabled |
| Local models benchmarked | **3** | `gemma4:12b`, `gemma4:26b`, and `gemma4:31b`; one synthetic generation and critique per model |
| Benchmark structural success | **100% schema and critique success for all three trials** | Directional Stage 7.1 benchmark, not a statistically conclusive evaluation |
| Unsupported claims in benchmark | **0 across the three recorded trials** | Repository evaluator result for one checked-in synthetic brief |
| Migration reconciliation | **31 synthetic runs migrated; 29 artifact checksums verified** | P1.5 pre-cutover backup/import record dated 2026-07-18 |
| Post-cutover persistence snapshot | **36 runs, 21 reviews, 18 strategy artifacts, 16 quality reports, 14 quality artifacts** | P1.5 PostgreSQL snapshot; historical evidence, not a live counter |

## Current automated verification

The local FastAPI suite completed in **0.87 seconds** with:

```text
108 passed, 8 skipped, 1 warning
```

The skipped cases are the opt-in PostgreSQL portability and integration tests,
which require `AI_FACTORY_TEST_POSTGRES_URL`. The warning is a dependency
deprecation warning from the FastAPI/Starlette test client, not a test failure.
Earlier stage documents contain lower test totals because they are historical
snapshots taken before later functionality and tests were added.

Reproduce the local result:

```bash
cd agent-service
UV_CACHE_DIR="$PWD/.uv-cache" uv run pytest -ra
```

## Current workflow measurements

The checked-in `CODEX TEST — AI Strategy Factory v0.1` export currently has:

| Node type | Count |
| --- | ---: |
| Code | 6 |
| Form | 7 |
| Form Trigger | 1 |
| HTTP Request | 3 |
| Switch | 2 |
| Sticky Note | 1 |
| **Total** | **20** |

The Stage 8 verification document reports 16 nodes because that record captures
an earlier dated checkpoint. Stage 9.5-lite records the later 20-node workflow.
The current export remains inactive, unpublished, credential-free, and
unavailable through MCP.

## Local-model benchmark

Stage 7.1 ran one generation and one separate critique per model against the
same checked-in synthetic brief:

| Model | Schema success | Critique success | Generation | Critique | Advisory quality | Evidence | Constraints | Unsupported claims | Issues |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gemma4:12b` | 100% | 100% | 78.44s | 33.02s | 100 | 10/10 | 10/10 | 0 | 0 |
| `gemma4:26b` | 100% | 100% | 46.99s | 11.97s | 100 | 10/10 | 10/10 | 0 | 0 |
| `gemma4:31b` | 100% | 100% | 156.84s | 79.79s | 94 | 10/10 | 10/10 | 0 | 2 |

Sources: `artifacts/evaluations/stage-7.1/report.md` and
`docs/STAGE-7.1-VERIFICATION.md`.

These results are deliberately narrow. Wall time includes possible local model
loading, each model has only one trial, the brief is synthetic, and blinded
human preference is still pending. The advisory score cannot approve a run or
select a model automatically.

## PostgreSQL cutover evidence

The P1.5 verification recorded a stopped-service migration of a **31-run**
synthetic SQLite baseline. Six application tables matched by count and
deterministic fingerprint, and all **29 physical artifact checksums** verified.
The post-cutover PostgreSQL snapshot contained:

| Record type | Count |
| --- | ---: |
| Strategy runs | 36 |
| Idempotency records | 73 |
| Reviews | 21 |
| Strategy artifacts | 18 |
| Quality reports | 16 |
| Quality artifacts | 14 |

Both service restart and PostgreSQL-container restart persistence were verified,
and the post-cutover dump passed an isolated restore test. These counts are a
dated verification snapshot, not telemetry from the currently running system.
Source: `docs/POSTGRESQL-P1.5-VERIFICATION.md`.

## Product safeguards expressed as measurable contracts

- **7** permitted run-state transitions are explicitly defined.
- Each advisory report contains **7 checks**, scored from **0–10**, plus an
  overall **0–100** advisory score.
- **0** quality scores or model outputs are allowed to approve a strategy.
- **1 explicit human decision** is required before an approved strategy
  artifact can be created.
- Strategy and quality artifacts use recorded **SHA-256** checksums for
  integrity verification.

These are system invariants rather than outcome metrics. Their implementation
is covered by the service tests and the workflow verification scripts.

## Metrics not yet established

The repository does **not** yet provide credible measurements for:

- time saved per real strategy engagement;
- improvement in strategy quality versus an unaided consultant;
- reviewer acceptance, rejection, or revision rates in real use;
- active users, retention, adoption, or willingness to pay;
- production reliability, concurrency, or service-level objectives; or
- blinded human preference among the three local models.

These gaps should be measured in a controlled synthetic pilot first and, only
after the deferred privacy and operational controls are complete, in authorized
real-world use. Until then, the project claims a working and verifiable process,
not proven market impact.
