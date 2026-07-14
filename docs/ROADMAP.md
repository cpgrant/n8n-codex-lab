# AI Strategy Factory roadmap

## Purpose

This is the canonical development roadmap for the AI Strategy Factory in the
n8n Codex Lab. It records completed work, planned stages, and the safety
boundary for moving from a synthetic local lab toward a controlled
professional workflow.

Completion dates use the `Europe/Copenhagen` timezone and are based on Git
history unless a separate operational-verification date is stated.

## Status summary

| Stage | Milestone | Status | Completed |
| --- | --- | --- | --- |
| 0 | Contracts and safety boundary | Complete | 2026-07-12 |
| 1 | FastAPI and SQLite foundation | Complete | 2026-07-12 |
| 2 | Deterministic strategy generation | Complete | 2026-07-12 |
| 3 | Human review and Markdown artifacts | Complete | 2026-07-12 |
| 4 | Inactive n8n strategy workflow | Complete | 2026-07-12 |
| 5 | Operational verification | Complete | 2026-07-12 |
| 6 | Local Ollama strategy provider | Complete | 2026-07-12 |
| 6.1 | Generation quality contract | Complete | 2026-07-12; live re-verification 2026-07-13 |
| 7 | Pre-review quality report | Complete | 2026-07-13 |
| 7.0.1 | Quality report Markdown artifact | Complete | 2026-07-13 |
| 7.1 | Local model evaluation | Human review pending | — |
| 8 | Flexible intake | Complete | 2026-07-13 |
| 9 | Client-demo hardening | In progress; Stage 9.2 next | — |
| 9.0 | Data policy and trust boundaries | Complete | 2026-07-13 |
| 9.1 | Authentication and authorization | Complete | 2026-07-13 |
| 10 | OpenAI provider and professional routing | Planned | — |

## Completed foundation

### Stage 0 — Contracts and safety boundary

Status: **Complete** on 2026-07-12 as part of commit `8aeef20`.

Established:

- the synthetic-only strategy brief and structured response contracts;
- run statuses, permitted transitions, review semantics, and idempotency rules;
- the provider boundary and approved Markdown artifact rules;
- explicit v0.1 non-goals and the prohibition on production or confidential
  data;
- the rule that n8n workflows remain inactive and unpublished without explicit
  approval.

### Stage 1 — FastAPI and SQLite foundation

Status: **Complete** on 2026-07-12 in commit `8aeef20`.

Delivered:

- a Mac-local FastAPI service;
- configuration and health endpoints;
- SQLite schema and repository-local persistence;
- typed request and response schemas;
- isolated Python development and test setup.

### Stage 2 — Deterministic strategy generation

Status: **Complete** on 2026-07-12 in commit `8aeef20`.

Delivered:

- synchronous strategy-run creation and retrieval;
- the deterministic `FakeStrategyProvider` for safe repeatable tests;
- durable run state and create-request idempotency;
- checked-in synthetic brief and response examples;
- automated and synthetic smoke tests.

### Stage 3 — Human review and Markdown artifacts

Status: **Complete** on 2026-07-12 in commit `a7ff3c5`.

Delivered:

- explicit human approval and rejection;
- immutable reviewable drafts and review records;
- terminal rejection with no artifact creation;
- approved Markdown rendering and retrieval;
- review idempotency and artifact checksums.

### Stage 4 — Inactive n8n strategy workflow

Status: **Complete** on 2026-07-12 in commit `c85dbe3`.

Delivered:

- the exported `CODEX TEST — AI Strategy Factory v0.1` workflow;
- synthetic form intake and normalization;
- n8n-to-Mac FastAPI connectivity through `host.docker.internal`;
- a complete draft review page and explicit approval/rejection path;
- an inactive, unpublished, credential-free workflow that is unavailable
  through MCP.

### Stage 5 — Operational verification

Status: **Complete** on 2026-07-12 in commit `743400c`.

Verified:

- workflow safety flags and local network paths;
- create and review idempotency;
- terminal rejection without an artifact;
- durable SQLite retrieval and restart persistence;
- approved manual n8n execution and Markdown artifact creation;
- absence of tracked databases, artifacts, secrets, and runtime caches.

The repeatable procedure is in `docs/STAGE-5-VERIFICATION.md`.

### Stage 6 — Local Ollama strategy provider

Status: **Complete** on 2026-07-12 in commit `b23f38d`. Repository-managed
Ollama startup support was added earlier that day in commit `52d3147`.

Delivered:

- opt-in `OllamaStrategyProvider` support through service configuration;
- local `gemma4:31b` structured generation;
- JSON-schema-constrained output and service-side validation;
- safe provider timeout, connection, envelope, and invalid-output errors;
- a live synthetic Ollama smoke test while retaining the fake provider as the
  deterministic default.

### Stage 6.1 — Generation quality contract

Status: **Complete** on 2026-07-12 in commit `acf97ec`. The committed code was
live re-verified with `gemma4:31b` on 2026-07-13 using synthetic run
`78d28f63-fe08-46a9-b8ee-ae6cfa87aaa0`.

Delivered:

- bounded depth for objectives, choices, initiatives, risks, assumptions,
  measures, and next steps;
- unique sequential IDs and valid initiative-to-objective references;
- stronger evidence, stakeholder, constraint, and numeric-target grounding;
- rejection of shallow or internally inconsistent provider output;
- a fully prefilled n8n test form based on the checked-in synthetic brief;
- 55 passing automated tests and successful live local-model generation.

Human approval remains mandatory. Structural validity is not treated as proof
of strategic quality.

## Planned professional workflow

### Stage 7 — Pre-review quality report

Status: **Complete** on 2026-07-13.

Add an advisory quality-review step between draft generation and human review:

```text
Generate draft
-> deterministic quality checks
-> optional model critique
-> human review
-> approval or rejection
```

Planned scope:

- a structured quality-report contract;
- `basic` mode with deterministic checks;
- `pro` mode with deterministic checks plus a separate critic call;
- checks for brief alignment, evidence grounding, constraint adherence,
  measurement quality, feasibility, and internal consistency;
- strengths, issues, unsupported claims, missing considerations, and review
  questions;
- durable association between the quality report and the exact draft checksum;
- quality findings displayed in the n8n human-review form.

Guardrails:

- the report is advisory and cannot approve a run;
- no numeric score automatically changes run status;
- the critic does not silently rewrite the stored draft;
- the human reviewer retains the final decision;
- the first implementation may use `gemma4:31b` for both generation and a
  separate critic call, with the shared-model limitation made explicit.

Completion criteria:

- deterministic and model-assisted reports validate against one contract;
- reports are reproducible or safely idempotent for the same draft;
- the review form displays findings without exposing prompts or raw provider
  errors;
- approval and rejection semantics remain unchanged;
- automated tests and a synthetic end-to-end n8n test pass.

Completion evidence:

- 66 automated tests passed;
- deterministic `basic` and Ollama-backed `pro` smoke tests passed;
- the installed workflow remained inactive, unpublished, credential-free, and
  unavailable through MCP;
- manual synthetic run `286e341c-a332-4dbc-9927-61cea879287d` displayed the
  advisory report before review, was explicitly approved, and created the
  checksum-bound Markdown artifact.

### Stage 7.0.1 — Quality report Markdown artifact

Status: **Complete** on 2026-07-13.

Delivered before Stage 7.1:

- an advisory Markdown file at
  `artifacts/quality-reports/quality-report-<run_id>.md` for every generated
  quality report;
- durable filename, media type, SHA-256 checksum, and creation metadata;
- atomic rendering, safe Markdown escaping, integrity-checked API retrieval,
  and retry recovery without regenerating the stored quality report;
- explicit separation from the approved `strategy-<run_id>.md` artifact;
- retention regardless of the later human approval or rejection decision.

The quality artifact is evidence for human review, not an approved strategy.
It cannot change run status or bypass approval.

Completion evidence: 69 automated tests and a live pro-mode synthetic smoke
test passed. Run `1010080d-9b6c-455e-9bf9-fc6c396dd678` produced a retrievable,
checksum-protected Markdown quality report while remaining `awaiting_review`.

### Stage 7.1 — Local model evaluation

Status: **In progress** on 2026-07-13; live benchmark complete and blind human
preference pending.

Benchmark the same synthetic brief set with:

- `gemma4:12b` as the latency-oriented baseline;
- `gemma4:26b` as the middle option;
- `gemma4:31b` as the current quality baseline.

Measure:

- schema success rate;
- generation and critique latency;
- constraint and evidence adherence;
- unsupported claims;
- quality-report results;
- human reviewer preference.

Model selection remains internal configuration rather than a client-facing
form control. Evaluation uses synthetic data only and should produce a
reviewable, repeatable report before changing the default model.

Implemented:

- a repeatable runner at `scripts/evaluate-stage7-1.py`;
- schema, critique, latency, token, grounding, constraint, unsupported-claim,
  issue, and overall-quality measurements;
- normalized JSON results, a Markdown report, and a blinded comparison packet
  under ignored `artifacts/evaluations/stage-7.1/`;
- a separate blind key and validated reviewer-preference file so preference is
  recorded by a human rather than inferred from model scores;
- 72 passing automated tests.

Live results for the checked-in synthetic brief:

| Model | Schema | Critique | Generation | Critique | Quality |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gemma4:12b` | 100% | 100% | 78.44s | 33.02s | 100 |
| `gemma4:26b` | 100% | 100% | 46.99s | 11.97s | 100 |
| `gemma4:31b` | 100% | 100% | 156.84s | 79.79s | 94 |

All candidates scored 10/10 for evidence grounding and constraint adherence,
with zero unsupported claims. The benchmark is directional because it has one
run per model on one synthetic brief. Stage completion and any internal model
default change require the blinded human preference.

### Stage 8 — Flexible intake

Status: **Complete** on 2026-07-13.

Add three intake modes:

```text
Choose input mode
|-- Load synthetic example
|-- Enter a blank manual form
`-- Upload structured JSON
          |
          v
   Validate and normalize
          |
          v
   Generate strategy
```

Planned scope and guardrails:

- preserve the fast synthetic demonstration path;
- add a genuinely blank manual form;
- add JSON upload first, with YAML considered later;
- enforce a small file-size limit and strict schema validation;
- reject unknown fields and provide clear validation errors;
- never use uploaded filenames for artifact paths;
- do not retain arbitrary uploaded files;
- keep all tests synthetic until the Stage 9 controls exist.

Delivered:

- an initial mode chooser with a fast checked-in synthetic example;
- a genuinely blank manual brief form with explicit synthetic-data
  confirmation;
- a single-file structured JSON upload path with a 64 KiB maximum;
- strict `.json`, one-object, top-level field, nested organization field, and
  v0.1 API-schema validation;
- normalization of all three paths into the same `StrategyBrief` contract;
- removal of binary data before generation and workflow settings that disable
  saved success, error, and manual execution data;
- no use of uploaded filenames for artifact paths;
- an updated installed workflow that remains inactive, unpublished,
  credential-free, and unavailable through MCP.

Completion evidence:

- 74 automated tests passed;
- `scripts/verify-stage8-intake.js` passed the example, blank-manual, valid
  upload, unknown-field, oversize, and wrong-extension cases;
- n8n accepted and re-exported the 16-node workflow with all safety flags;
- the production form continued to return HTTP 404.

The workflow remains synthetic-only. Real or confidential client intake is
blocked until the Stage 9 controls are complete.

### Stage 9 — Client-demo hardening

Status: **In progress** before any controlled external pilot.

Stage 9 is divided into independently reviewable checkpoints. Implementation
and verification continue with synthetic data throughout the stage.

#### Stage 9.0 — Data policy and trust boundaries

Status: **Complete** on 2026-07-13.

- classify allowed, restricted, and prohibited input data;
- document consent, acceptable-use, privacy, and AI-disclosure requirements;
- identify trust boundaries across browser, n8n, FastAPI, SQLite, Ollama,
  artifacts, logs, backups, MCP, and administrators;
- define the minimum controls required before a controlled real-data pilot.

Delivered:

- an approved synthetic-lab policy at `docs/STAGE-9.0-DATA-POLICY.md`;
- data classifications, acceptable-use rules, consent/privacy/AI-disclosure
  requirements, trust boundaries, incident baseline, and minimum pilot gates;
- accepted interim local-lab ownership for synthetic-only operations;
- a formal no-pilot decision until named service/business, security/privacy,
  operations, incident-response, and pilot owners are assigned;
- synthetic verification recorded in `docs/STAGE-9.0-VERIFICATION.md`.

Completion evidence: 74 automated tests and the Stage 8 intake verifier
passed; static inspection confirmed the exported workflow remained inactive,
unpublished, credential-free, unavailable through MCP, and configured not to
save success, error, or manual execution data. Stage 9.0 completion does not
authorize real data or implement the controls planned for Stages 9.1-9.6.

#### Stage 9.1 — Authentication and authorization

Status: **Complete** on 2026-07-13.

- require an authenticated user for client-facing intake and review;
- authenticate n8n-to-FastAPI service calls separately from human sessions;
- keep credentials in approved secret storage, never workflow exports or Git;
- test missing, invalid, expired, and insufficient authorization paths;
- retain explicit human approval as a separate authorized action.

Delivered:

- n8n User Auth across the complete multi-page form flow;
- distinct environment-backed FastAPI service and review bearer tokens;
- fail-closed missing configuration and optional token expiry;
- separate service/review scopes and safe `401`, `403`, and `503` contracts;
- opaque authenticated human actor binding for approval/rejection;
- removal of the editable reviewer identity from the form;
- updated synthetic smoke scripts and a repeatable Stage 9.1 verifier;
- design and verification records in `docs/STAGE-9.1-AUTH-DESIGN.md` and
  `docs/STAGE-9.1-VERIFICATION.md`.

Completion evidence: 83 automated tests passed; live synthetic API verification
passed all required and denied paths; n8n imported and re-exported the updated
workflow with Form Trigger v2.6 and `n8nUserAuth`; the workflow remained
inactive, unpublished, credential-free, unavailable through MCP, and configured
not to persist success, error, or manual execution data. The production form
continued to return HTTP 404.

Stage 9.1 authenticates callers but does not assign run ownership or tenant
boundaries. That isolation remains Stage 9.2 scope.

#### Stage 9.2 — Run ownership and isolation

- assign every run to an authenticated owner and client/tenant boundary;
- derive ownership from trusted authentication context, not request JSON;
- scope run, quality-report, review, and artifact retrieval by ownership;
- prevent cross-client enumeration and access, including error differences;
- migrate existing synthetic lab runs without treating them as client data.

#### Stage 9.3 — Retention, deletion, and recovery

- define retention periods for briefs, drafts, reviews, SQLite records,
  Markdown artifacts, logs, and backups;
- implement an authorized deletion workflow covering database rows and files;
- document what deletion can and cannot remove from backups immediately;
- test backup creation, restoration, integrity checks, and deletion behavior;
- maintain a minimal audit record without retaining deleted strategy content.

#### Stage 9.4 — Abuse controls and safer observability

- enforce request, upload, and concurrency limits at trusted boundaries;
- add rate limiting and protection against repeated expensive model calls;
- use request/run identifiers while redacting briefs, prompts, model output,
  tokens, credentials, and personal data from logs;
- add client-safe validation, provider, timeout, and recovery errors;
- monitor health and capacity without exposing client content.

#### Stage 9.5 — Long-running request experience

- replace fragile browser waits with background execution or a documented,
  resilient polling/status flow;
- make retry and idempotency behavior explicit for generation and critique;
- show safe progress, timeout, cancellation, and recovery states;
- ensure a browser disconnect does not duplicate a run or approval decision.

#### Stage 9.6 — Controlled synthetic client-demo verification

- exercise authentication, isolation, deletion, throttling, recovery, and
  long-running behavior with multiple synthetic test identities;
- complete automated negative tests and a documented end-to-end demo run;
- verify workflow exports contain no credentials and remain unavailable via
  MCP unless separately approved;
- verify backup/restore and operational runbooks;
- produce a go/no-go record for a later, separately approved pilot.

Stage 9 completion gates:

- all 9.0-9.6 checkpoints have automated tests, operational evidence, and
  documented ownership;
- cross-client access tests fail safely for every run and artifact endpoint;
- deletion and recovery procedures are demonstrated with synthetic records;
- logs and exported workflows contain no secrets or strategy content;
- the controlled synthetic demo passes without bypassing human approval;
- the Git checkpoint is clean and the roadmap evidence is recorded.

Completing Stage 9 does not automatically authorize real data, activate the
workflow, or publish a stable form. Each remains a separate explicit decision
requiring approved data policy, operational ownership, and a documented pilot
scope. Until then, earlier stages remain suitable only for local synthetic
demonstrations, workshops, and internal experimentation.

### Stage 10 — OpenAI provider and professional routing

Status: **Planned** after the quality rubric and client-data controls exist.

Planned scope:

- implement the reserved `OpenAIStrategyProvider` behind the existing provider
  interface;
- preserve the same schemas, quality report, review semantics, idempotency, and
  artifact rules across providers;
- configure generation and review providers independently;
- support local/private, cost-balanced, premium, and independent cross-provider
  review modes;
- add provider-parity, structured-output, timeout, retry, and safe-error tests;
- keep provider and model choices in controlled server configuration rather
  than accepting arbitrary values from n8n clients.

Illustrative configuration:

```text
STRATEGY_GENERATION_PROVIDER=ollama
STRATEGY_GENERATION_MODEL=gemma4:31b

STRATEGY_REVIEW_PROVIDER=openai
STRATEGY_REVIEW_MODEL=<approved-openai-model>
```

Before any hosted-provider use with non-synthetic data, the system must have
approved API-key handling, consent and disclosure, retention rules, logging
controls, client authorization, and a clear statement that the brief leaves
the local Mac.

## Roadmap rules

- Use synthetic data until Stage 9 is complete and real-data use is explicitly
  approved.
- Work only with n8n workflows whose names begin with `CODEX TEST`.
- Never activate or publish a workflow without explicit approval.
- Never modify existing credentials or commit secrets.
- Keep generation, quality advice, and human approval as separate concerns.
- Do not mark a planned stage complete from code alone: require automated tests,
  synthetic operational verification, documentation, and a clean Git
  checkpoint.
- Record material scope changes and completion evidence in this file.
