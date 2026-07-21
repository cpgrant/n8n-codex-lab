# Prior Work and Submission-Period Development

This document separates the pre-existing AI Strategy Factory baseline from the
work eligible for evaluation in OpenAI Build Week. It is based on the public
Git history and repository artifacts; it does not publish private Codex
conversation content.

## Official cutoff

The OpenAI Build Week submission period began on **2026-07-13 at 09:00 PDT**,
equivalent to **16:00 UTC** and **18:00 CEST (Europe/Copenhagen)**. The source is
the [official Devpost rules](https://openai.devpost.com/rules).

The last pre-period commit is
[`698badc`](https://github.com/cpgrant/n8n-codex-lab/commit/698badc443889556e179fad7d7445430fd12dd77),
dated **2026-07-13 17:59:56 CEST**, four seconds before the cutoff. It is treated
as prior work. The first eligible commit is
[`e8b0cc2`](https://github.com/cpgrant/n8n-codex-lab/commit/e8b0cc2),
dated **2026-07-14 05:50:40 CEST**.

## Prior-work baseline

At the cutoff, the repository had 21 commits and already contained:

- repository safety rules and the MCP/n8n development lab;
- an early typed FastAPI strategy-generation service;
- structured synthetic brief intake and state transitions;
- an inactive `CODEX TEST` n8n workflow with human review;
- deterministic fake generation and optional local Ollama generation;
- initial strategy-quality evaluation and local-model comparison; and
- the Stage 9.0 synthetic-data policy.

These capabilities establish the baseline and are not presented as eligible
submission-period work.

## Meaningful submission-period extensions

This evidence snapshot was prepared on **2026-07-21 CEST** at public audit head
[`87ace2b`](https://github.com/cpgrant/n8n-codex-lab/commit/87ace2b4a681facf8e69a0a37310fa72484a4b9d).
At that point, the public `main` history contained 38 commits after the cutoff.
Relative to `698badc`, the eligible change set modifies 136 files with 15,907
insertions and 529 deletions. Judges can inspect the complete
[`698badc...87ace2b` comparison](https://github.com/cpgrant/n8n-codex-lab/compare/698badc443889556e179fad7d7445430fd12dd77...87ace2b4a681facf8e69a0a37310fa72484a4b9d).

The table groups representative commits rather than claiming that a single
commit contains every part of a feature. All dates and times are CEST
(`UTC+02:00`).

| Date and representative commit | Eligible extension | Documented Codex/GPT-5.6 contribution | Evidence and verification |
| --- | --- | --- | --- |
| 2026-07-14 05:50 — [`e8b0cc2`](https://github.com/cpgrant/n8n-codex-lab/commit/e8b0cc2) | Added bearer-token authentication, protected service/review boundaries, configuration, tests, and operating documentation | Codex helped implement and test the authentication boundary and align the API, workflow contract, and documentation | [`auth.py`](../agent-service/src/ai_factory/auth.py), [`test_api.py`](../agent-service/tests/test_api.py), [`STAGE-9.1-VERIFICATION.md`](STAGE-9.1-VERIFICATION.md); run `scripts/verify-stage9-1-auth.sh` |
| 2026-07-16 08:47 — [`cefec16`](https://github.com/cpgrant/n8n-codex-lab/commit/cefec16) | Added recovery of incomplete runs, run-status tooling, workflow verification, troubleshooting, and later responsive review-form fixes | Codex used repository and workflow inspection to implement recovery paths, verify the export contract, and iterate on form behavior | [`strategy-run-status.sh`](../scripts/strategy-run-status.sh), [`verify-stage9-5-lite.js`](../scripts/verify-stage9-5-lite.js), [`STAGE-9.5-LITE-VERIFICATION.md`](STAGE-9.5-LITE-VERIFICATION.md); run `node scripts/verify-stage9-5-lite.js` |
| 2026-07-16 10:27 — [`76e5291`](https://github.com/cpgrant/n8n-codex-lab/commit/76e5291) | Strengthened the strategy-quality contract, artifacts, provider behavior, review service, and tests while preserving human-only approval | Codex helped implement the advisory quality layer and tests that prevent model scores from authorizing workflow state | [`quality.py`](../agent-service/src/ai_factory/quality.py), [`test_quality.py`](../agent-service/tests/test_quality.py), [`TRACK-B-Q1-VERIFICATION.md`](TRACK-B-Q1-VERIFICATION.md); run `cd agent-service && uv run pytest -q` |
| 2026-07-16 10:57 — [`f27f3c3`](https://github.com/cpgrant/n8n-codex-lab/commit/f27f3c3) | Added backup, restore, retention audit, security guidance, and verification coverage | Codex helped design and test backup integrity and retention operations around synthetic run data | [`backup.py`](../agent-service/src/ai_factory/backup.py), [`test_backup.py`](../agent-service/tests/test_backup.py), [`STAGE-9.3-LITE-VERIFICATION.md`](STAGE-9.3-LITE-VERIFICATION.md); run `scripts/verify-stage9-3-lite.sh` |
| 2026-07-18 14:20 — [`2449736`](https://github.com/cpgrant/n8n-codex-lab/commit/2449736), [`942a4fa`](https://github.com/cpgrant/n8n-codex-lab/commit/942a4fa), [`fb06944`](https://github.com/cpgrant/n8n-codex-lab/commit/fb06944) | Added PostgreSQL/SQLite portability, Alembic schema, transactional migration, dual-backend tests, reconciliation, backup/restore, cutover, and rollback evidence | Codex helped evolve the persistence layer, implement migration and recovery tooling, run database checks, and document the cutover decision | [`migrations/`](../agent-service/migrations/), [`test_postgresql.py`](../agent-service/tests/test_postgresql.py), [`POSTGRESQL-MIGRATION-PLAN.md`](POSTGRESQL-MIGRATION-PLAN.md), [`POSTGRESQL-P1.5-VERIFICATION.md`](POSTGRESQL-P1.5-VERIFICATION.md); run `scripts/verify-postgres-migration.sh` |
| 2026-07-18 15:21 — [`14be354`](https://github.com/cpgrant/n8n-codex-lab/commit/14be354) | Added coordinated full-system start/stop commands and updated operating/setup paths | Codex helped connect Docker, PostgreSQL, n8n, Ollama, and FastAPI startup checks into repository-managed operations | [`system-start.sh`](../scripts/system-start.sh), [`system-stop.sh`](../scripts/system-stop.sh), [`DAILY-OPERATIONS.md`](DAILY-OPERATIONS.md); run `scripts/system-start.sh`, then the status commands in the judge guide |
| 2026-07-19 10:06 — [`c6be9f0`](https://github.com/cpgrant/n8n-codex-lab/commit/c6be9f0) | Made clean-machine setup reproducible with pinned n8n build inputs, Compose configuration, environment defaults, and a rewritten setup guide | Codex helped audit dependency/configuration sources and turn the working local environment into repeatable judge instructions | [`Dockerfile.n8n`](../Dockerfile.n8n), [`compose.n8n.yml`](../compose.n8n.yml), [`SETUP.md`](SETUP.md); follow the clean-machine verification checklist |
| 2026-07-19 10:24 — [`4975846`](https://github.com/cpgrant/n8n-codex-lab/commit/4975846), 2026-07-20 20:47 — [`e4e3881`](https://github.com/cpgrant/n8n-codex-lab/commit/e4e3881) | Documented Codex/GPT-5.6 usage, produced the Remotion demonstration and provenance, audited stale claims, and added judge/metrics evidence | Codex helped organize implementation evidence, write and validate judge-facing documentation, and build the checked-in Remotion presentation | [`README.md`](../README.md), [`JUDGE-GUIDE.md`](JUDGE-GUIDE.md), [`METRICS-SUMMARY.md`](METRICS-SUMMARY.md), [`ai-strategy-factory-video/`](../ai-strategy-factory-video/) |

## Codex and GPT-5.6 evidence

Codex powered by GPT-5.6 was used as the development collaborator during the
eligible work. The detailed contribution map is in
[`README.md`](../README.md#codex-contribution-evidence), and the resulting code,
tests, verification records, operations scripts, and presentation sources are
linked above.

Additional time evidence is retained as follows:

- local Codex JSONL session records contain timestamped session metadata for
  this repository during the submission period;
- the primary official `/feedback` Codex Session ID was entered in the private
  Devpost submission field; and
- the public Git history provides dated, inspectable commits throughout the
  eligible period.

Raw Codex session logs are intentionally not committed because they can contain
conversation content, local paths, environment details, or other private
context. They can be retained for organizer verification if requested.

## Reproduce the boundary audit

From the repository root:

```bash
git log --date=iso-strict --pretty=format:'%h %ad %s' --reverse
git rev-list --count --before='2026-07-13T18:00:00+02:00' 87ace2b
git rev-list --count --since='2026-07-13T18:00:00+02:00' 87ace2b
git diff --stat 698badc..87ace2b
git diff --name-status 698badc..87ace2b
```

The counts in this document include merge commits because they describe the
public `main` history a judge saw at the audit head. The linked comparison is
the authoritative file-level view of that eligible-change snapshot.
