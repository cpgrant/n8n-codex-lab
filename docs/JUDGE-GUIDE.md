# AI Strategy Factory — Judge Guide

AI Strategy Factory is a local-first, human-in-the-loop system that turns a
structured strategy brief into a reviewed, traceable Markdown strategy
artifact. Codex was used to develop and verify the product; n8n coordinates the
experience, FastAPI implements the agent service, PostgreSQL stores workflow
state, and Ollama provides local model inference.

## Start here

- **90-second product demonstration:** [AI Strategy Factory demonstration][demo-video]
- **Public repository:** [cpgrant/n8n-codex-lab](https://github.com/cpgrant/n8n-codex-lab)
- **Existing results:** [technical, benchmark, and migration metrics](METRICS-SUMMARY.md)
- **Eligibility:** [prior work and submission-period evidence](SUBMISSION-PERIOD-EVIDENCE.md)
- **Clean-machine installation:** [SETUP.md](SETUP.md)
- **Architecture and implementation detail:** [README.md](../README.md)

[demo-video]: https://www.youtube.com/watch?v=QKJJM996nmI

The short verification path below assumes the repository has already been set
up. A first installation takes longer because Docker images, Python packages,
and the local Ollama model must be downloaded.

## Submission-period scope

This is a pre-existing project. The eligible work begins at the official
submission-period cutoff, **2026-07-13 09:00 PDT (16:00 UTC / 18:00 CEST)**.
The [submission-period evidence record](SUBMISSION-PERIOD-EVIDENCE.md)
separates the prior baseline from the 38 subsequent commits through public
audit head `87ace2b` and maps the major Codex/GPT-5.6-assisted extensions to
dated commits, files, and verification commands. Timestamped Codex session
records are retained privately, and the official `/feedback` Session ID was
submitted through Devpost.

## The problem and audience

Independent strategy consultants and small internal strategy teams often have
to choose between an unstructured AI chat and a heavyweight enterprise system.
The first is fast but difficult to review or reproduce; the second is expensive
and slow to adopt.

AI Strategy Factory demonstrates a third path: a repeatable strategy workflow
that can run locally, validates its inputs, separates generation from quality
advice, requires an explicit human decision, and creates the final artifact only
after approval. The current repository is a demonstration environment and uses
synthetic data; it is not presented as a production system for real client data.

## What makes the implementation distinctive

The product is not simply a prompt wrapped in a form:

1. A structured brief is validated before generation.
2. The model proposes content but cannot approve its own output.
3. Quality checks provide advice without changing workflow state.
4. An authenticated human review is required to approve or reject the draft.
5. Only an approved draft becomes a checksummed Markdown artifact.
6. Workflow state and review history are persisted in PostgreSQL.

```text
Strategy brief
      │
      ▼
n8n intake and orchestration
      │
      ▼
FastAPI agent service ──► Ollama local inference
      │
      ▼
PostgreSQL state and audit trail
      │
      ▼
Human review ──► approved, immutable Markdown artifact
```

## Fast evaluation path

### Option A — 90 seconds

Watch the [product demonstration][demo-video].
It shows the workflow and product experience with narration.

### Option B — about five minutes on a configured machine

From the repository root, start the local stack:

```bash
scripts/system-start.sh
```

Then check the three principal services:

```bash
scripts/postgres-status.sh
scripts/status.sh
scripts/agent-check.sh
```

The checks should report PostgreSQL, n8n, and the AI Factory agent service as
available. The stack uses local addresses; n8n is normally available at
<http://127.0.0.1:5678>.

Run the lightweight milestone verification:

```bash
node scripts/verify-stage8-intake.js
node scripts/verify-stage9-5-lite.js
scripts/verify-stage9-3-lite.sh
```

Run the agent-service tests:

```bash
cd agent-service
uv run pytest -q
```

These checks cover the intake contract, approval and artifact invariants, and
the supporting agent-service behavior. Environment-dependent tests may be
skipped when optional live services are unavailable.

## Walk through the product with synthetic data

1. Open <http://127.0.0.1:5678> and sign in to the local n8n instance.
2. Open the inactive workflow named **CODEX TEST — AI Strategy Factory v0.1**.
   If this is a new n8n installation, import
   [`workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json`](../workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json)
   once.
3. Select **Execute workflow**. Use the temporary `/form-test/...` URL shown by
   n8n; do not publish or activate the workflow.
4. Load the synthetic example from
   [`examples/strategy-brief.synthetic.json`](../examples/strategy-brief.synthetic.json),
   or enter equivalent fictional information.
5. Follow the workflow through validation, strategy generation, quality advice,
   and the human review step.
6. Approve or reject the draft using a synthetic reviewer identity. On approval,
   inspect the resulting Markdown artifact and its checksum.

For the quickest deterministic evaluation, keep the documented default
fake/basic provider configuration. A live local Ollama run demonstrates actual
local inference but can take several minutes depending on the machine and model.
Detailed operating instructions are in
[`DAILY-OPERATIONS.md`](DAILY-OPERATIONS.md).

## Evidence mapped to the judging criteria

| Criterion | What to assess | Repository evidence |
| --- | --- | --- |
| **Technological Implementation** | A non-trivial, integrated implementation with durable state, tests, local inference, and explicit workflow invariants | [`agent-service/`](../agent-service/), [`workflows/`](../workflows/), [`scripts/`](../scripts/), [`compose.n8n.yml`](../compose.n8n.yml), [`compose.postgres.yml`](../compose.postgres.yml), and [`README.md`](../README.md) |
| **Design** | A coherent journey from intake through readiness, generation, quality advice, review, and artifact delivery | The importable n8n workflow, the [90-second demonstration][demo-video], and [`docs/DAILY-OPERATIONS.md`](DAILY-OPERATIONS.md) |
| **Potential Impact** | A credible workflow for consultants and small teams that need repeatability, reviewability, and a local-processing option | The human approval boundary, PostgreSQL audit trail, artifact checksum, and problem framing in [`README.md`](../README.md) |
| **Quality of the Idea** | A strategy factory in which AI drafts and advises, while humans retain decision authority and approved outputs become durable artifacts | The separation of generation, advisory quality checks, review state, and artifact creation in the workflow and service code |

## How Codex is used

Codex served as the development and verification agent across the repository:
it helped evolve the architecture, implement service and workflow changes,
create tests and verification scripts, diagnose integration issues, and improve
the documentation and demonstration assets. The repository instructions in
[`AGENTS.md`](../AGENTS.md) constrain that work to synthetic test data and
inactive `CODEX TEST` workflows.

The roles are intentionally separate:

- **Codex** develops, inspects, tests, and documents the system.
- **Ollama** is the optional local runtime inference provider.
- **n8n and FastAPI** enforce the workflow and application behavior.
- **The human reviewer** alone authorizes approval or rejection.

This separation is central to the product: model output is treated as a draft,
not as a decision.

## Safety boundary

- Use synthetic data only.
- Work only with workflows whose names begin with `CODEX TEST`.
- Keep imported workflows inactive and unpublished.
- Do not modify credentials during evaluation.
- Do not treat the demonstration environment as approved for real client data.

## Stop the system

When evaluation is complete:

```bash
make down
```

For troubleshooting, recovery, and component-by-component commands, see
[`DAILY-OPERATIONS.md`](DAILY-OPERATIONS.md). The latest documentation
freshness review is recorded in
[`DOCUMENTATION-AUDIT.md`](DOCUMENTATION-AUDIT.md).
