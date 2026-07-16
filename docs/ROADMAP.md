# AI Factory Platform roadmap

## Purpose

This is the canonical development roadmap for the AI Factory Platform in the
n8n Codex Lab. The detailed stages below describe the Strategy Factory, which
is the first reference implementation. The broader objective, shared lifecycle,
and factory portfolio are defined in `docs/AI-FACTORY-PLATFORM.md`.

The confirmed platform direction includes Strategy, Podcast, and Job
Application factories. Research and Briefing and Content Repurposing are
candidate ideas, not committed stages. Factory expansion and production
hardening are separate decisions: new local synthetic prototypes do not make
the platform ready for real data, multiple users, publication, or external
submissions.

Uncommitted Knowledge Factory, agent-runtime, and MCP options are recorded in
`docs/PLATFORM-IDEAS.md`. Their placeholder labels are not active stages and do
not change the status summary below.

Completion dates use the `Europe/Copenhagen` timezone and are based on Git
history unless a separate operational-verification date is stated.

## Status summary

| Stage | Milestone | Status | Completed |
| --- | --- | --- | --- |
| P0 | Platform vision and factory catalog | Complete | 2026-07-14 |
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
| 9 | Client-demo and operationalization hardening | Local baseline complete; decision gate open | — |
| 9.0 | Data policy and trust boundaries | Complete | 2026-07-13 |
| 9.1 | Authentication and authorization | Complete | 2026-07-13 |
| 10 | OpenAI provider and professional routing | Planned | — |

## Platform P0 — Vision and factory catalog

Status: **Complete** on 2026-07-14.

The platform objective and portfolio are now explicit:

- Strategy Factory is the implemented reference vertical slice;
- Podcast Factory and Job Application Factory are confirmed planned factories;
- Research and Briefing Factory and Content Repurposing Factory are candidate
  ideas requiring a later portfolio decision;
- the shared factory lifecycle preserves validation, immutable runs, quality
  checks, explicit human review, approved artifacts, and retention/deletion;
- shared platform components will be extracted from repeated needs after a
  second working factory, rather than generalized from Strategy alone.

See `docs/AI-FACTORY-PLATFORM.md` for scope, boundaries, and the recommended
expansion sequence.

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
- removal of binary data before generation and workflow settings that initially
  disabled saved success, error, and manual execution data;
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

Stage 9.1 follow-up: n8n 2.29 multi-page test forms require a saved manual
waiting execution. Manual execution persistence is now enabled for synthetic
tests; production success/error persistence remains disabled. This can retain
synthetic form/upload data locally until operator deletion.

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

That persistence statement records the Stage 9.0 checkpoint. The dated Stage
9.1 follow-up below supersedes only the manual-execution setting for functional
synthetic multi-page tests.

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
inactive, unpublished, credential-free, and unavailable through MCP. A live
synthetic multi-page run on 2026-07-14 confirmed that n8n 2.29 requires manual
execution persistence; production success/error persistence remains disabled.
The production form continued to return HTTP 404.

Stage 9.1 authenticates callers but does not assign run ownership or tenant
boundaries. That isolation remains Stage 9.2 scope.

#### Post-Stage 9.1 decision gate

Stages 9.0-9.1 form the completed **local synthetic-lab security baseline**.
The workflow is suitable for a single local operator using synthetic data while
it remains inactive and unpublished. Production hardening remains important
for operationalization, but the full Stage 9.2-9.6 sequence is not required for
continued local product development.

Choose one of these tracks deliberately:

**Track A — Operationalization and client-demo hardening**

Use this track when there is a concrete need for multiple users, a published
form, a controlled client demonstration, or pilot preparation. Continue through
Stages 9.2-9.6 in order. Completion of those stages remains mandatory before
any real-data or externally accessible pilot can be considered.

**Track B — Local synthetic product development (recommended now)**

Keep the workflow local, inactive, unpublished, and synthetic-only. Prioritize:

1. ~~a Stage 9.5-lite usability pass for clear generation progress, resilient
   form-window recovery, and obvious completion/artifact links;~~ completed
   2026-07-16;
2. ~~strategy-quality improvements, especially measurable objectives,
   actionable reviewer feedback, and stronger final artifacts;~~ completed
   2026-07-16 as Track B-Q1;
3. Stage 9.3-lite housekeeping with a documented synthetic execution-retention
   period, safe cleanup procedure, and basic SQLite/artifact backup check;

Under Track B, Stage 9.2, full Stage 9.3, Stage 9.4, and Stage 9.6 remain
pilot-gated rather than canceled. The no-pilot and synthetic-only decisions
remain in force.

#### Track B-Q1 — Strategy quality and final artifacts

Status: **Complete on 2026-07-16.**

This local synthetic product checkpoint improves the decision quality of a
draft without changing the separation between generation, advisory criticism,
and explicit review:

- generation instructions require success measures to map clearly to
  objectives and require an objective to repeat the measure's exact supported
  end-state target;
- deterministic quality checks distinguish aligned, vague, missing, and
  conflicting objective-to-measure targets;
- baseline and scope numbers are not treated as conflicting end-state targets;
- actionable findings identify the objective, measure, exact target, required
  rewrite, and reviewer question;
- the Ollama critic independently checks the same alignment while retaining all
  deterministic findings as minimum warnings;
- approved Markdown artifacts begin with a decision summary and include the
  strategy provider, advisory score, recommendation, critic, and matching
  quality-report artifact path when available.

Verification evidence: 87 automated tests, Stage 8 intake verification, Stage
9.5-lite workflow verification, and a live isolated-port Ollama/pro-critic
synthetic run. Run `ef812274-2027-49b1-94a8-6d0c0885f364` correctly aligned the
35%-to-60% objective with its 60% measure and classified a five-garden scope
statement as missing the exact 100% adoption target rather than as a false
numeric conflict. The report scored 94/100 with `ready_for_review`. A labeled
synthetic test approval produced the enhanced strategy Markdown with the
matching advisory quality-report path. See
`docs/TRACK-B-Q1-VERIFICATION.md`.

#### Stage 9.2 — Run ownership and isolation

Status: **Pilot-gated / deferred for the single-user local lab.**

Start when multiple authenticated users, client boundaries, publication, or a
controlled pilot becomes a concrete requirement.

- assign every run to an authenticated owner and client/tenant boundary;
- derive ownership from trusted authentication context, not request JSON;
- scope run, quality-report, review, and artifact retrieval by ownership;
- prevent cross-client enumeration and access, including error differences;
- migrate existing synthetic lab runs without treating them as client data.

#### Stage 9.3 — Retention, deletion, and recovery

Status: **Stage 9.3-lite complete on 2026-07-16. Full lifecycle controls remain
pilot-gated.**

The Track B subset covers synthetic execution cleanup and a basic backup check.
The complete scope below is required for operationalization.

Stage 9.3-lite implemented:

- explicit 14-day n8n execution pruning and a 500-execution cap;
- a read-only `CODEX TEST` execution-retention audit with a separate 24-hour
  stale-waiting threshold;
- a safe operator procedure that deletes confirmed execution candidates only
  through the n8n UI and never deletes workflows;
- online SQLite backup plus local Markdown artifact copy;
- a versioned SHA-256 manifest with file sizes and owner-only permissions;
- SQLite integrity and recorded-artifact checksum verification;
- a basic restore test in automatically removed temporary storage;
- a read-only 30-day expired-backup audit.

Verification evidence: 91 automated tests, shell syntax and destructive-command
checks, a live read-only n8n audit, and a live factory backup/verify/restore
test. The n8n audit identified stale waiting executions `65`, `66`, `67`, and
`75`; it did not delete them. The ignored verification backup reconciled 31
runs, 16 approved strategy artifacts, and 13 quality-report artifacts. See
`docs/STAGE-9.3-LITE-VERIFICATION.md`.

Stage 9.3-lite does not implement per-run deletion, audit tombstones,
tenant-aware authorization, backup encryption/offline custody, automated
expiry, or restoration into active storage. Those remain in the full scope:

- define retention periods for briefs, drafts, reviews, SQLite records,
  Markdown artifacts, logs, and backups;
- implement an authorized deletion workflow covering database rows and files;
- document what deletion can and cannot remove from backups immediately;
- test backup creation, restoration, integrity checks, and deletion behavior;
- maintain a minimal audit record without retaining deleted strategy content.

#### Stage 9.4 — Abuse controls and safer observability

Status: **Publication/pilot-gated.**

Defer while the service is single-user, local, inactive, and unpublished.

- enforce request, upload, and concurrency limits at trusted boundaries;
- add rate limiting and protection against repeated expensive model calls;
- use request/run identifiers while redacting briefs, prompts, model output,
  tokens, credentials, and personal data from logs;
- add client-safe validation, provider, timeout, and recovery errors;
- monitor health and capacity without exposing client content.

#### Stage 9.5 — Long-running request experience

Status: **Stage 9.5-lite complete on 2026-07-16. Full resilient execution
remains operationalization work.**

The live Stage 9.1 run exposed confusing browser-window and waiting-state
behavior, making a small local usability pass valuable before more demos.

- replace fragile browser waits with background execution or a documented,
  resilient polling/status flow;
- make retry and idempotency behavior explicit for generation and critique;
- show safe progress, timeout, cancellation, and recovery states;
- ensure a browser disconnect does not duplicate a run or approval decision.

Stage 9.5-lite implemented:

- a pre-generation readiness page with realistic local Ollama timing and safe
  before-run recovery guidance;
- a stored-draft checkpoint that displays the run ID before the separate
  quality-critic call;
- explicit 330-second n8n timeouts for generation and critique;
- `scripts/strategy-run-status.sh` for authenticated, content-free status and
  artifact-location recovery after a run ID exists;
- prominent run ID, advisory-report location, approved-artifact location, and
  retry guidance through review and completion;
- an automated workflow-contract verifier and updated regression tests.

Implementation evidence: 83 automated tests, Stage 8 regression verification,
Stage 9.5-lite static verification, successful n8n import/re-export, and an
exact semantic comparison of the tracked and installed 20-node workflow. The
installed workflow remains inactive, unpublished, credential-free, and
unavailable through MCP.

Manual completion evidence: synthetic run
`5062f0cf-eb42-4f4b-9f0f-38459e06e399` passed the generation-readiness,
stored-run recovery, pro quality-review, explicit approval, and final artifact
checks. The terminal status changed from `awaiting_review` without a quality
artifact to `artifact_created` with both expected Markdown paths. A long-command
overflow found on the first completion rendering was corrected with wrap-safe
markup, asserted by the automated verifier, and accepted by n8n on re-import.
The same contract now requires the human-review JSON to use ordinary wrapping
HTML line breaks rather than n8n's non-wrapping `pre` presentation.
The supported n8n `--container-width` form variable provides responsive
`720px` standard cards and a `1000px` human-review card while preserving
wrapping on narrower screens.
Synthetic run `d308a8b7-8ec7-40e6-a2ac-ea17c8c7db79` visually verified the
responsive pages and completed as `artifact_created`.

#### Stage 9.6 — Controlled synthetic client-demo verification

Status: **Client-demo-gated / deferred.**

Run only after the operationalization controls it verifies are implemented.

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

These gates define readiness for a controlled external demonstration or later
pilot decision. They do not block local synthetic product and quality work
under Track B.

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

## Factory expansion roadmap

The Strategy stages above are the reference implementation track. Additional
factories should be thin vertical slices first, then sources of proven shared
platform components.

### F1 — Strategy Factory reference implementation

Status: **Local synthetic vertical slice complete through Stage 9.5-lite and
Track B-Q1.** Continue with Stage 9.3-lite unless an operationalization
milestone is chosen.

### F2 — Podcast Factory

Status: **Confirmed planned; synthetic contract not yet defined.**

Recommended first slice:

- accept a checked-in synthetic source pack and episode brief;
- produce an evidence-backed outline, draft script, editorial quality report,
  and human-reviewed script/show-notes artifact;
- remain inactive and unpublished, with no distribution integration;
- define copyright, source provenance, AI disclosure, and voice/likeness gates
  before audio generation is added.

### F3 — Job Application Factory

Status: **Confirmed planned; synthetic contract not yet defined.**

Recommended first slice:

- use only a synthetic candidate profile and synthetic job posting;
- map claims to supplied evidence before drafting a CV, cover letter,
  application answers, or interview pack;
- prohibit invented qualifications and automatic application submission;
- require stricter privacy, retention, ownership, and deletion controls before
  any real candidate data is considered.

### Candidate factories

Research and Briefing Factory and Content Repurposing Factory are potentially
useful because they reuse evidence, review, and artifact capabilities while
producing distinct outputs. They remain ideas rather than scheduled work until
one is selected for a concrete use case.

Recommended sequence:

1. keep Strategy stable as the reference factory;
2. build the Podcast Factory as the second inactive synthetic vertical slice;
3. compare both implementations and extract only repeated platform primitives;
4. design the Job Application Factory with its sensitive-data boundary first;
5. schedule candidate factories only after an explicit value and safety review.

The Stage 9.2-9.6 operationalization gates apply before any factory uses real
data, multiple users, an externally accessible form, publication, or automatic
delivery/submission. They do not prevent local synthetic contract and product
work under Track B.

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
