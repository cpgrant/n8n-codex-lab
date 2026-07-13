# Stage 9.0 data policy and trust boundaries

Status: **Approved for the synthetic lab**

Policy version: `0.1`

Governance decision recorded 2026-07-13: the repository owner accepted the
allowed/restricted/prohibited classifications, synthetic-only boundary, and
the consent, privacy, AI-disclosure, retention, and pilot gates. This approval
does not authorize real data.

Ownership decision recorded 2026-07-13: the repository owner accepted the
local lab operator as interim owner for synthetic-only service,
security-containment, operations, backup, deletion, and incident duties. The
repository owner formally retained the no-pilot decision: no real-data pilot is
permitted until named service/business, security/privacy, operations,
incident-response, and pilot owners are assigned.

This document defines the data boundary for the AI Strategy Factory before
authentication, tenant isolation, retention, deletion, and abuse controls are
implemented. It is a control specification for later Stage 9 work, not evidence
that those controls already exist.

## Current operating rule

The lab accepts synthetic and fictional test data only. Do not enter, upload,
paste, generate, or derive real personal, client, company-confidential,
regulated, or credential data.

The `CODEX TEST — AI Strategy Factory v0.1` workflow must remain inactive,
unpublished, credential-free, and unavailable through MCP unless each change
receives separate explicit approval. Completing Stage 9.0 does not authorize
real-data use, workflow activation, publication, or an external pilot.

## Scope

This policy applies to:

- browser form input and review decisions;
- the n8n workflow and transient execution state;
- FastAPI requests, responses, and process configuration;
- SQLite run, idempotency, quality-report, review, and artifact metadata;
- local Ollama generation and critique requests and responses;
- approved-strategy and advisory quality-report Markdown artifacts;
- application, shell, Docker, n8n, and model-service logs;
- repository files, exported workflows, local backups, and restored copies;
- MCP access and human administrator access.

It covers both content supplied by a user and content derived from it. A draft,
quality report, review comment, generated artifact, log excerpt, or backup
inherits the highest classification of its source data.

## Data classification

| Class | Examples | Current handling rule |
| --- | --- | --- |
| **Allowed** | Checked-in fictional briefs, invented organization and role names, synthetic metrics, synthetic reviewer labels, generated content derived only from those inputs | Permitted for local development and tests. Keep generated databases and artifacts ignored by Git. |
| **Restricted** | Real business plans, internal metrics, non-public company facts, client briefs, identifiable employee or customer information, real reviewer identity, contract or commercial information | Not permitted in the current lab. A future controlled pilot may accept a specifically approved subset only after all Stage 9 gates are met. |
| **Prohibited** | Passwords, API keys, access tokens, private keys, authentication cookies, payment-card data, government identifiers, health data, highly sensitive personal data, unlawful content, or data the submitter is not authorized to provide | Never enter into the workflow. Stop processing, do not copy the content into an issue or log, and follow the incident procedure below if exposure occurs. |

Public availability does not automatically make real data allowed. Real public
company or personal information remains outside the present synthetic-only
boundary because the lab lacks an approved purpose, ownership controls,
retention rules, and deletion procedures.

### Data minimization

- Use the smallest synthetic brief that exercises the required behavior.
- Use role labels such as `synthetic-reviewer`, never real names or email
  addresses.
- Do not place secrets or sensitive content in filenames, identifiers,
  idempotency keys, request IDs, comments, prompts, or test output.
- Do not add arbitrary brief fields to the API or workflow export.
- Do not retain uploaded source files after normalization.
- Do not commit SQLite databases, generated artifacts, evaluation output,
  runtime caches, logs, `.env` files, or credentials.

## Acceptable use, consent, and disclosure

### Current lab use

Use is limited to local development, internal demonstrations, workshops, and
testing with synthetic data. The output is an AI-generated draft and advisory
quality report. Neither is authoritative professional advice, and neither may
bypass explicit human review.

### Requirements before a controlled real-data pilot

The intake surface must give the user clear information before submission and
record the applicable policy version and consent event. The notice must state:

- who operates the service and the approved purpose of processing;
- what information is collected and which classifications are forbidden;
- that an AI model generates the draft and may generate a separate critique;
- which model provider is used and whether data stays local or leaves the Mac;
- where briefs, drafts, reviews, metadata, artifacts, logs, and backups are
  stored;
- who can access the run and who may approve or reject it;
- the applicable retention and deletion behavior, including backup limits;
- that AI output may be incomplete or incorrect and requires human review;
- how to request access, correction, deletion, or incident support.

A checkbox alone is not sufficient. The operator must have an approved purpose
and authority to process the selected data category. Consent and disclosure
language requires review by the accountable business/privacy owner before a
pilot; this repository document is not legal advice or a substitute for that
review.

Users must not use the system to make fully automated high-impact decisions,
impersonate another person, upload data without authority, evade access
controls, probe another owner's runs, or submit credentials and prohibited
data.

## Current data lifecycle

```text
Browser test form
  -> n8n validation and normalization
  -> FastAPI validation
  -> SQLite brief and run state
  -> local Ollama generation and optional critique
  -> SQLite draft, quality report, review, and metadata
  -> local advisory and approved Markdown artifacts
```

Current implementation facts:

- n8n success, error, and manual execution persistence is disabled for this
  workflow, but transient execution memory still handles submitted content.
- FastAPI stores the complete normalized brief and generated draft in SQLite.
- SQLite also stores idempotency records, quality reports, review identity and
  comments, checksums, errors, and artifact metadata.
- Ollama receives the brief for generation and receives stored brief/draft
  content for model-assisted critique. It does not approve runs or write the
  database and artifacts.
- A quality-report Markdown artifact is created before review. An approved
  strategy Markdown artifact is created only after explicit approval.
- Generated SQLite and artifact directories are local and ignored by Git, but
  they have no implemented retention or deletion policy.
- Existing backup guidance covers the n8n volume. Governed backup, restore,
  retention, and deletion behavior for factory SQLite data and artifacts is
  not yet implemented.

## Trust boundaries and required controls

| Boundary | Data crossing it | Current protection | Gap and required later control |
| --- | --- | --- | --- |
| User/browser -> n8n | Brief, upload, synthetic confirmation, review decision and comment | Local test URL, strict JSON shape and 64 KiB limit; production form unpublished | No user authentication or durable consent record. Add authenticated sessions, policy notice/version, CSRF/session protection, and authorization in Stage 9.1. |
| n8n -> FastAPI | Normalized brief, run IDs, review decisions, idempotency and request IDs | Mac-local routing and schema validation | Calls are unauthenticated. Add independently managed service authentication, request limits, and secret rotation in Stages 9.1 and 9.4. |
| FastAPI -> SQLite | Full brief, generated content, report, review, errors, and metadata | Repository-local ignored file and schema constraints | No owner/tenant scope, encryption decision, retention schedule, or deletion workflow. Add trusted ownership and isolation in Stage 9.2 and lifecycle controls in Stage 9.3. |
| FastAPI -> Ollama | Brief, generation instructions, draft and critique instructions | Local loopback service; no API key; structured-output validation | Content enters a separate process with no approved real-data policy or capacity controls. Document model handling and add concurrency, timeout, and safe-error controls in Stages 9.4-9.5. |
| FastAPI -> artifact filesystem | Strategy and quality-report content with run metadata | Service-owned filenames, atomic writes, checksum verification, Git ignore | Files are not owner-scoped and have no retention/deletion schedule. Add access authorization and coordinated deletion in Stages 9.2-9.3. |
| Services -> logs/terminal | Request metadata, errors, and operational output | Raw prompts and provider envelopes are intentionally not returned or stored as evaluation artifacts | No verified redaction standard across all services. Permit identifiers and metrics only; redact content, tokens, credentials, and personal data in Stage 9.4. |
| Active storage -> backups/restores | n8n configuration and potentially workflow/execution data; future factory data backups | Manual n8n-volume backup procedure | No inventory, retention, access control, restore audit, or deletion semantics for factory data. Implement and test these in Stage 9.3. |
| Codex/MCP -> n8n | Workflow metadata and permitted workflow actions | MCP token; test workflow unavailable through MCP; repository safety rules | Token compromise or future over-broad exposure could cross the boundary. Keep secrets outside Git, apply least privilege, and require separate approval before MCP availability changes. |
| Administrator -> all local components | Configuration, databases, artifacts, logs, backups, and workflow controls | Local machine access and documented operating rules | Administrators are effectively privileged and not audited. Assign named operational ownership, least privilege, access review, and incident duties before a pilot. |

Network locality reduces exposure but is not authentication, authorization,
tenant isolation, encryption, consent, or deletion.

## Logging and observability policy

Allowed operational fields are request ID, opaque run ID, operation name,
status, duration, provider identifier, model identifier, response class, and
coarse resource metrics.

Logs must not contain:

- brief, draft, quality-report, review-comment, or artifact content;
- prompts, complete model requests, or complete model responses;
- uploaded file contents or filenames supplied by users;
- credentials, tokens, cookies, authorization headers, or environment values;
- personal identifiers or client/tenant names.

Client-visible errors must be stable and safe. Detailed errors may be available
to an authorized operator only when they follow the same redaction rules.

## Retention, deletion, and backup policy baseline

Stage 9.3 must define explicit periods for each data category before a pilot.
Until then, only synthetic data is permitted and generated lab data should be
kept only as long as needed for the active test or documented verification.

Deletion must eventually cover, as one authorized operation:

- the brief, draft, report, review, error, and idempotency records in SQLite;
- approved-strategy and advisory quality-report Markdown files;
- owner-scoped indexes or derived metadata introduced later;
- content-bearing logs, if any are found despite the logging policy;
- backup expiry, with clear disclosure that deletion from immutable or offline
  backups may occur through scheduled expiration rather than immediately.

A minimal audit tombstone may retain an opaque run ID, owner/tenant reference,
deletion timestamp, actor, policy basis, and outcome. It must not retain the
brief, generated strategy, report, review comment, or artifact content.

Backup procedures must inventory what is copied, encrypt and restrict backup
access where appropriate, define expiry, verify integrity, test restoration,
and prevent a restored copy from silently reviving data that should remain
deleted.

## Incident handling baseline

If restricted or prohibited data is submitted before the required controls
exist:

1. Stop the affected test and prevent further processing or sharing.
2. Do not reproduce the content in chat, Git, tickets, screenshots, or logs.
3. Record only safe identifiers, time, affected components, and data class.
4. Notify the designated lab operator and security/privacy owner.
5. Identify all copies in n8n memory or storage, SQLite, artifacts, logs,
   model-service state, exports, and backups.
6. Remove accessible copies using an approved, documented procedure and record
   the outcome without retaining the exposed content.
7. Rotate any exposed credential immediately and review access records.
8. Do not resume real-data processing until the cause and required controls
   have been reviewed.

The operator must not improvise destructive database, volume, or backup actions
that could damage unrelated workflows or evidence.

## Minimum gate for a controlled pilot

All of the following are required before a real-data pilot can be proposed:

- an accountable service owner, security/privacy owner, and operations owner;
- approved allowed-data categories, purpose, acceptable-use terms, consent,
  privacy notice, and AI disclosure;
- authenticated human access and separate n8n-to-FastAPI service identity;
- authorization enforced on every run, report, review, and artifact operation;
- ownership derived from trusted identity and tested cross-owner isolation;
- approved retention periods and a tested authorized deletion workflow;
- inventoried, access-controlled, expiring, and restore-tested backups;
- verified content-redacted logging and client-safe error handling;
- upload, request, rate, concurrency, and expensive-model-call limits;
- resilient status, retry, idempotency, timeout, cancellation, and recovery
  behavior for long-running calls;
- automated negative tests using multiple synthetic identities;
- a documented synthetic end-to-end verification and go/no-go decision;
- clean workflow exports containing no credentials or client content;
- separate explicit approval for pilot scope, real-data use, workflow
  activation/publication, and any MCP availability.

Meeting the technical gate does not itself approve a pilot.

## Ownership and decisions still required

Interim ownership is role-based while the repository remains a local,
synthetic-only lab. The **local lab operator** means the person who starts and
administers this repository, n8n, FastAPI, SQLite, Ollama, and local artifacts.
This role may maintain synthetic test operations, but it may not authorize a
real-data pilot by itself.

| Decision or duty | Interim synthetic-lab owner | Pilot requirement |
| --- | --- | --- |
| Maintain the service purpose and synthetic-only boundary | Local lab operator | A named service/business owner must approve purpose and allowed data |
| Maintain repository security rules and stop unsafe tests | Local lab operator | Named security and privacy owners must approve architecture, notice, and incident handling |
| Operate local access, monitoring, backup, restore, deletion, and incident response | Local lab operator | A named operations owner and tested runbooks are required |
| Approve model/provider handling, including any external transfer | No interim authority for real data | Named service and privacy owners must approve; external transfer remains prohibited |
| Make the pilot go/no-go decision | No interim authority | A named pilot sponsor must decide jointly with the owners above |

No real-data pilot may be proposed or started while any required pilot owner or
incident contact is unnamed. Until named contacts are recorded in an approved
operational record, the incident contact is the local lab operator for
containment of synthetic-lab events only. If the operator cannot safely contain
an event, processing must remain stopped and no pilot may proceed.

## Stage 9.0 review checklist

- [x] Data classes and examples have been reviewed and approved.
- [x] Every current storage location and trust boundary has an accountable
  owner.
- [x] Consent, acceptable-use, privacy, and AI-disclosure requirements have
  been reviewed by the appropriate owner.
- [x] Stage 9.1-9.6 requirements trace back to an identified policy gap.
- [x] The incident baseline and escalation contacts are documented.
- [x] Documentation cross-links and operational verification are complete.
- [x] The workflow remains inactive, unpublished, credential-free, and
  unavailable through MCP.
- [x] Verification used synthetic data only.
- [x] The roadmap records evidence and the Git checkpoint is clean.

Stage 9.0 is complete as a synthetic-lab policy checkpoint. This completion
does not approve a real-data pilot or assert that the controls planned for
Stages 9.1-9.6 are implemented.
