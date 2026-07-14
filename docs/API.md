# AI Strategy Factory v0.1 API Contract

## Status

The v0.1 service implements `GET /health`, `POST /v1/strategy-runs`,
`GET /v1/strategy-runs/{run_id}`,
`POST /v1/strategy-runs/{run_id}/quality-report`,
`GET /v1/strategy-runs/{run_id}/quality-report`,
`GET /v1/strategy-runs/{run_id}/quality-report/artifact`,
`POST /v1/strategy-runs/{run_id}/review`, and
`GET /v1/strategy-runs/{run_id}/artifact`.

Base URLs:

```text
Host-side tools:  http://127.0.0.1:8000
n8n in Docker:    http://host.docker.internal:8000
```

All application endpoints are under `/v1`. Request and response bodies use
`application/json`. Times are ISO 8601 UTC strings. IDs are opaque UUIDs.

Stage 9.1 requires authentication for every `/v1` request. `GET /health`
remains an unauthenticated, content-free local health check.

## Common headers

| Header | Applies to | Rule |
| --- | --- | --- |
| `Content-Type: application/json` | Requests with bodies | Required |
| `Authorization: Bearer <token>` | All `/v1` requests | Service token normally; distinct review token for review decisions |
| `X-AI-Factory-Actor-ID` | Review requests | Required opaque authenticated n8n user ID |
| `Idempotency-Key` | `POST` requests | Required; 8-255 printable characters |
| `X-Request-ID` | All requests | Optional caller correlation ID; service returns one if absent |

## Health

### `GET /health`

Does not contact a strategy provider.

It does not report token values or strategy content. A successful health
response does not mean `/v1` authentication is configured.

## Authentication and authorization

Normal run, quality-report, and artifact operations require
`AI_FACTORY_SERVICE_TOKEN`. `POST /review` requires the distinct
`AI_FACTORY_REVIEW_TOKEN` and `X-AI-Factory-Actor-ID`. The `reviewer` field in
the body must equal that actor ID.

Tokens contain at least 32 characters, are supplied through the process
environment, and may have optional timezone-aware expiry timestamps. Missing
server configuration returns a fail-closed `503`; it never enables anonymous
access. See `docs/STAGE-9.1-AUTH-DESIGN.md` for the authorization matrix and
rotation contract.

Response `200`:

```json
{
  "status": "ok",
  "service": "ai-strategy-factory",
  "version": "0.1"
}
```

## Create a strategy run

### `POST /v1/strategy-runs`

Accepts the brief contract in `examples/strategy-brief.synthetic.json`.

Stage 8 does not add a second creation API. The n8n example, blank-manual, and
JSON-upload paths all normalize to this same endpoint and strict schema. The
workflow limits uploads to one `.json` object and 64 KiB, removes binary data,
and never forwards the uploaded filename. Direct API callers remain responsible
for sending `application/json` that satisfies the documented contract.

The initial synchronous v0.1 contract records the run, invokes the selected
provider, validates the result, and returns the reviewable draft. It is expected
to return `201` with status `awaiting_review`. A provider or validation failure
returns an error while preserving a durable `failed` run when a run ID was
created.

Provider selection is process configuration, never request input. `fake` is the
default. Stage 6 permits `ollama`; its local structured generation can take
substantially longer while a large model is loaded.

Response `201`:

```json
{
  "data": {
    "run_id": "4a3fd768-726a-4d7c-a722-5215d87511e4",
    "status": "awaiting_review",
    "strategy": {},
    "quality_report": null,
    "created_at": "2026-07-12T10:00:00Z",
    "updated_at": "2026-07-12T10:00:01Z"
  },
  "meta": {
    "request_id": "req_01",
    "idempotent_replay": false
  }
}
```

## Create an advisory quality report

### `POST /v1/strategy-runs/{run_id}/quality-report`

Requires an `Idempotency-Key` header and no request body. The service applies
the configured `AI_FACTORY_QUALITY_MODE`:

- `basic` runs deterministic checks without contacting a model;
- `pro` runs the same checks and a separate Ollama critic call, then merges the
  results conservatively so model feedback cannot erase deterministic warnings.

The operation is valid for a stored `awaiting_review` draft. It does not change
the run status, rewrite the strategy, or make an approval decision.

Response `200` includes the run ID, unchanged status, a `quality_report`, and
`quality_artifact` metadata for its advisory Markdown rendering. Reports are
immutable; repeating the exact operation returns the stored report and
artifact metadata.

### `GET /v1/strategy-runs/{run_id}/quality-report`

Returns the stored report, or `409 QUALITY_REPORT_NOT_READY` when a valid run
does not yet have one. `GET /v1/strategy-runs/{run_id}` also includes the report
as `quality_report`, or `null` before report generation.

### `GET /v1/strategy-runs/{run_id}/quality-report/artifact`

Returns the checksum-verified advisory Markdown report as `200 text/markdown`.
Its service-owned filename is `quality-report-<run_id>.md`; the file is stored
under `artifacts/quality-reports/`, separate from approved strategy artifacts.
Returns `409 QUALITY_ARTIFACT_NOT_READY` if it has not been rendered.

The `strategy` member follows the structured strategy response contract. The
full example is in `examples/strategy-response.synthetic.json`.

## Read a strategy run

### `GET /v1/strategy-runs/{run_id}`

Response `200` includes:

```json
{
  "data": {
    "run_id": "4a3fd768-726a-4d7c-a722-5215d87511e4",
    "status": "awaiting_review",
    "brief": {},
    "strategy": {},
    "review": null,
    "artifact": null,
    "created_at": "2026-07-12T10:00:00Z",
    "updated_at": "2026-07-12T10:00:01Z"
  },
  "meta": {
    "request_id": "req_02"
  }
}
```

## Review a strategy run

### `POST /v1/strategy-runs/{run_id}/review`

Approval request:

```json
{
  "decision": "approved",
  "reviewer": "synthetic-reviewer",
  "comment": "Approved for the fictional planning exercise."
}
```

Rejection request:

```json
{
  "decision": "rejected",
  "reviewer": "synthetic-reviewer",
  "comment": "Revise the initiative sequencing before resubmission."
}
```

Rules are defined in `docs/AI-STRATEGY-FACTORY.md`. In particular, rejection
comments are required, decisions are final for a run, and revisions create a
new linked run.

Approval response `200` after successful rendering:

```json
{
  "data": {
    "run_id": "4a3fd768-726a-4d7c-a722-5215d87511e4",
    "status": "artifact_created",
    "review": {
      "decision": "approved",
      "reviewer": "synthetic-reviewer",
      "comment": "Approved for the fictional planning exercise.",
      "decided_at": "2026-07-12T10:05:00Z",
      "draft_checksum": "sha256:example-only"
    },
    "artifact": {
      "filename": "strategy-4a3fd768-726a-4d7c-a722-5215d87511e4.md",
      "media_type": "text/markdown",
      "checksum": "sha256:example-only",
      "created_at": "2026-07-12T10:05:00Z"
    }
  },
  "meta": {
    "request_id": "req_03",
    "idempotent_replay": false
  }
}
```

Rejection response `200` has status `rejected`, its recorded review, and
`artifact: null`.

If approval is recorded but rendering fails, the API returns an error containing
the run ID and the run remains `approved`. The approved decision and exact draft
remain durable and immutable; a retry with the same idempotency key resumes safe
artifact rendering rather than creating another decision or regenerating
strategy content.

## Read an approved artifact

### `GET /v1/strategy-runs/{run_id}/artifact`

Returns `200 text/markdown` only for `artifact_created`. Returns `409
ARTIFACT_NOT_READY` for a valid run without an approved artifact and `404
RUN_NOT_FOUND` for an unknown run.

The service verifies the stored SHA-256 checksum before returning the artifact
and supplies a service-owned `Content-Disposition` filename.

## Success envelope

JSON success responses use:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_01",
    "idempotent_replay": false
  }
}
```

`idempotent_replay` is included for mutating operations.

## Error response format

All JSON errors use:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request did not satisfy the strategy brief contract.",
    "details": [
      {
        "field": "desired_outcomes",
        "reason": "must contain at least one item"
      }
    ],
    "run_id": null,
    "retryable": false
  },
  "meta": {
    "request_id": "req_04"
  }
}
```

Rules:

- `code` is stable and machine-readable.
- `message` is safe for a human and contains no secret or stack trace.
- `details` is an array and may be empty.
- `run_id` is present when a run was durably created; otherwise it is null.
- `retryable` describes whether retrying the same operation can be useful.

## Error codes and HTTP status

| HTTP | Code | Meaning |
| --- | --- | --- |
| `400` | `INVALID_JSON` | Body is not valid JSON |
| `400` | `VALIDATION_ERROR` | Request fails the documented schema |
| `400` | `IDEMPOTENCY_KEY_REQUIRED` | Mutation lacks a valid key |
| `401` | `AUTHENTICATION_REQUIRED` | Bearer token is missing |
| `401` | `AUTHENTICATION_INVALID` | Bearer token is malformed or unknown |
| `401` | `AUTHENTICATION_EXPIRED` | Valid bearer token has expired |
| `403` | `AUTHORIZATION_DENIED` | Identity lacks the required scope or review actor |
| `404` | `RUN_NOT_FOUND` | Run ID does not exist |
| `409` | `INVALID_STATE_TRANSITION` | Operation is not valid for current status |
| `409` | `IDEMPOTENCY_CONFLICT` | Key was reused with different input |
| `409` | `IDEMPOTENCY_IN_PROGRESS` | Matching operation is still running |
| `409` | `ARTIFACT_NOT_READY` | Run has no approved artifact |
| `409` | `QUALITY_REPORT_NOT_READY` | Run has no quality report |
| `409` | `QUALITY_ARTIFACT_NOT_READY` | Run has no quality-report Markdown artifact |
| `422` | `PROVIDER_OUTPUT_INVALID` | Provider output fails the strategy schema |
| `422` | `QUALITY_REVIEW_OUTPUT_INVALID` | Critic output fails the quality schema |
| `500` | `ARTIFACT_RENDER_FAILED` | Approved draft could not be rendered |
| `500` | `QUALITY_ARTIFACT_RENDER_FAILED` | Quality report could not be rendered |
| `500` | `INTERNAL_ERROR` | Unexpected safe-to-hide failure |
| `502` | `PROVIDER_ERROR` | Strategy provider failed |
| `502` | `QUALITY_REVIEW_PROVIDER_ERROR` | Quality critic failed |
| `503` | `SERVICE_UNAVAILABLE` | Required local component is unavailable |
| `503` | `AUTHENTICATION_NOT_CONFIGURED` | Required server credential is absent |

The service must not expose prompts, API keys, database paths, stack traces, or
raw provider errors to n8n clients.

## Idempotency behavior

Create and review operations follow the rules in
`docs/AI-STRATEGY-FACTORY.md`.

- Exact replay: return the original response and set
  `meta.idempotent_replay` to `true`.
- Same key, different normalized request: return `409
  IDEMPOTENCY_CONFLICT`.
- A review replay must not duplicate the decision or artifact.
- A transient artifact-render failure may be resumed with the original key and
  exact approval payload.

## API non-goals for v0.1

- Token issuance, refresh, or identity-management endpoints
- Run listing, search, deletion, or bulk operations
- Draft editing or partial approvals
- Streaming, webhooks, queues, or asynchronous job polling
- Provider selection supplied by API clients
- Direct filesystem paths in client requests or responses
