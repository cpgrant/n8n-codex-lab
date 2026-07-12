# AI Strategy Factory v0.1

## Purpose

AI Strategy Factory v0.1 is a thin, human-reviewed workflow for turning a
synthetic strategy brief into a structured draft and, after explicit approval,
an approved Markdown artifact.

n8n remains the orchestration and review surface. A later lightweight Python
service will own validation, generation, durable run state, review decisions,
and artifact rendering.

```text
Human -> n8n (Docker) -> agent service (macOS) -> strategy provider
                    review decision |
                                    v
                         approved Markdown artifact
```

Stage 3 implements synchronous create/read run endpoints using the deterministic
`FakeStrategyProvider`, explicit approval/rejection, immutable review records,
approved Markdown rendering and retrieval, artifact integrity checks, and
SQLite-backed idempotency. It does not perform real model calls or create an
n8n workflow.

## Example files

- Brief: `examples/strategy-brief.synthetic.json`
- Structured response: `examples/strategy-response.synthetic.json`
- Approved artifact template: `templates/strategy-artifact.md`

All examples are fictional and must remain synthetic during v0.1 development.

## Strategy brief contract

Required fields:

| Field | Type | Rules |
| --- | --- | --- |
| `schema_version` | string | Exactly `0.1` |
| `title` | string | 1-200 characters |
| `organization` | object | Synthetic `name`, `type`, and `context` strings |
| `decision_horizon` | string | Time horizon for the strategy |
| `challenge` | string | The strategic question to address |
| `desired_outcomes` | array of strings | At least one outcome |
| `constraints` | array of strings | May be empty |
| `available_evidence` | array of strings | Synthetic evidence only; may be empty |
| `stakeholders` | array of strings | Roles or groups, not real personal data |
| `requested_by` | string | Synthetic actor label |

Optional fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `supersedes_run_id` | string or null | Links a revision to an earlier immutable run |

Unknown fields should be rejected in v0.1 so integration mistakes are visible.

## Structured strategy response contract

The response is a reviewable draft, not an approved strategy. It contains:

| Field | Type | Content |
| --- | --- | --- |
| `schema_version` | string | Exactly `0.1` |
| `run_id` | string | Opaque UUID assigned by the service |
| `status` | string | Normally `awaiting_review` |
| `executive_summary` | string | Short decision-oriented summary |
| `current_situation` | object | `summary` and `evidence` string array |
| `objectives` | array | Objects with `id`, `statement`, and `time_horizon` |
| `strategic_choices` | array | Objects with `id`, `choice`, `rationale`, and `trade_offs` |
| `recommended_initiatives` | array | Objects with `id`, `name`, `description`, `owner_role`, `timeframe`, and `supports_objectives` |
| `risks_and_assumptions` | object | `risks` and `assumptions` string arrays |
| `success_measures` | array | Objects with `id`, `measure`, `target`, and `review_frequency` |
| `next_steps` | array | Ordered objects with `order`, `action`, and `owner_role` |
| `generated_at` | string | ISO 8601 UTC timestamp |
| `provider` | string | Provider identifier, initially `fake` |

IDs are stable within a run and use readable prefixes such as `OBJ-1`, `CHO-1`,
`INIT-1`, and `MET-1`. Text generated from the brief must be treated as
untrusted content and never used directly as a filename, path, command, or
credential value.

## Provider interface

The first implementation will use a deliberately small provider abstraction:

```text
generate_strategy(brief) -> structured strategy content
```

Providers:

- `FakeStrategyProvider`: first implementation; deterministic output for tests
  and synthetic demonstrations, with no network or model dependency.
- `OpenAIStrategyProvider`: later implementation behind the same interface.

Providers return strategy content only. They do not assign run IDs, change run
status, approve drafts, write artifacts, or access n8n. The service validates
provider output before persisting it.

## Run statuses

| Status | Meaning |
| --- | --- |
| `received` | Brief has been accepted and durably recorded |
| `generating` | A provider generation attempt is in progress |
| `awaiting_review` | Valid structured output is available for human review |
| `approved` | A human explicitly approved the immutable draft |
| `artifact_created` | The approved Markdown artifact was rendered and recorded |
| `rejected` | A human explicitly rejected the immutable draft |
| `failed` | Generation or provider-output validation failed |

## Permitted transitions

```text
received -> generating
generating -> awaiting_review
generating -> failed
awaiting_review -> approved
awaiting_review -> rejected
approved -> artifact_created
failed -> generating
```

Rules:

- No other transition is permitted.
- `artifact_created` and `rejected` are terminal.
- A failed generation may retry on the same run only when no reviewable draft
  exists.
- If rendering fails after approval, the run remains `approved`. Artifact
  rendering is retried as `approved -> artifact_created` without regenerating
  content. The implementation must keep the approved draft immutable during
  this recovery.
- A revised brief or changed draft creates a new run with `supersedes_run_id`;
  it never mutates an approved, rejected, or reviewable draft in place.

## Approval semantics

- Only a run in `awaiting_review` can receive a new review decision.
- Approval requires `decision: approved`, a non-empty synthetic `reviewer`, and
  an optional comment.
- Approval applies to the exact stored structured draft identified by `run_id`.
- Approval is recorded with reviewer, timestamp, comment, and draft checksum.
- Approval makes the draft immutable.
- Markdown generation is attempted only after approval.
- The artifact filename is service-owned and based on the run ID, for example
  `strategy-<run_id>.md`.
- Successful approval returns the review record and artifact metadata. It does
  not return arbitrary filesystem paths supplied by a client.

## Rejection semantics

- Rejection requires `decision: rejected`, a non-empty synthetic `reviewer`,
  and a non-empty explanatory comment.
- Rejection is recorded with timestamp and draft checksum.
- A rejected run produces no approved artifact and cannot later be approved.
- Addressing rejection feedback requires a new brief/run linked through
  `supersedes_run_id`.

## Idempotency rules

- Every mutating API request requires an `Idempotency-Key` header.
- Keys are scoped to the operation and authenticated caller when authentication
  is introduced.
- A repeated key with byte-equivalent normalized input returns the original
  status code and response without repeating generation, review, or rendering.
- Reusing a key with different normalized input returns `409
  IDEMPOTENCY_CONFLICT`.
- Concurrent requests with the same key produce one operation result.
- Keys and their request fingerprints are retained at least as long as the run.
- Provider retries caused by the service are not new client operations and do
  not require a new client key.

## Configuration contract

| Variable | Default/example | Purpose |
| --- | --- | --- |
| `AI_FACTORY_HOST` | `127.0.0.1` | Host interface for the macOS service |
| `AI_FACTORY_PORT` | `8000` | Service port |
| `AI_FACTORY_HOST_URL` | `http://127.0.0.1:8000` | URL used by host-side checks |
| `AI_FACTORY_N8N_URL` | `http://host.docker.internal:8000` | URL used by n8n inside Docker Desktop |
| `AI_FACTORY_PROVIDER` | `fake` | Provider selection; v0.1 starts with `fake` |
| `AI_FACTORY_DATA_DIR` | repository `data/` | Local SQLite directory |
| `AI_FACTORY_ARTIFACT_DIR` | repository `artifacts/` | Generated approved artifact directory |
| `OPENAI_API_KEY` | unset secret | Reserved for the later OpenAI provider |

Secrets must never be committed or embedded in workflow exports. The two URLs
are intentionally separate: `localhost` inside the n8n container refers to that
container, not to the Mac.

## Approved Markdown artifact

The checked-in template is the human-readable reference layout. The service
renderer preserves the same eight strategy sections, approval metadata, run ID,
and generation time without executing template expressions. Rendering rules:

- escape or safely render untrusted Markdown content;
- include no secrets, hidden prompts, or provider credentials;
- preserve stored item ordering and stable IDs;
- include approval metadata and draft checksum;
- never create an artifact for `awaiting_review`, `rejected`, or unapproved
  failed runs.

## v0.1 non-goals

- Production use or production data
- Live n8n workflow creation, activation, or publication during Stages 0-3
- PostgreSQL, Redis, vector databases, embeddings, or retrieval-augmented generation
- LangChain, LangGraph, or the OpenAI Agents SDK
- Multi-agent orchestration or autonomous tool use
- Fine-tuning, evaluation platforms, or prompt optimization systems
- Multiple model providers active at once
- Streaming responses, background job queues, or distributed workers
- Multi-user authentication, authorization, tenancy, or billing
- Collaborative editing, inline section approval, or partial approval
- Rich document formats such as DOCX, PDF, or slides
- Automatic publication or external distribution of artifacts
- Use of real company, customer, employee, or confidential strategy data
