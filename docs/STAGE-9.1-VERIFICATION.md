# Stage 9.1 authentication verification

Date: 2026-07-13 (`Europe/Copenhagen`)

Status: **Complete for the synthetic lab**

## Outcome

Stage 9.1 adds two independent authentication boundaries:

- n8n User Auth protects intake and every later form page;
- an environment-backed service bearer token protects normal FastAPI
  operations;
- a distinct environment-backed review bearer token protects approval and
  rejection;
- review calls require the authenticated n8n user's opaque actor ID, and the
  stored reviewer must match it.

FastAPI fails closed when required authentication is absent or not configured.
Stage 9.1 does not implement run ownership or tenant isolation and does not
authorize a real-data pilot.

## Automated verification

The following passed:

```bash
agent-service/.venv/bin/pytest agent-service/tests -q
node scripts/verify-stage8-intake.js
bash -n scripts/*.sh
```

Results:

- 83 Python tests passed;
- existing Stage 8 intake paths and validation remained valid;
- missing, malformed, unknown, expired, and wrong-scope tokens failed safely;
- missing, malformed, and mismatched review actors failed safely;
- denied review attempts did not change run status or create review records;
- configuration rejects short or identical service/review tokens;
- the public health endpoint returned no protected content;
- no authentication response exposed token values.

## Live synthetic API verification

FastAPI was started with ephemeral synthetic service and review tokens. The
repeatable verifier ran:

```bash
scripts/verify-stage9-1-auth.sh
```

It confirmed:

- missing and invalid credentials returned `401`;
- a valid token used for the wrong scope returned `403`;
- service credentials could create and read a synthetic run;
- service credentials could not make a review decision;
- review credentials without a human actor were denied;
- a body/header actor mismatch was denied;
- a valid review-scoped rejection was stored for opaque synthetic actor
  `synthetic-stage9-reviewer`;
- the rejected run created no approved artifact.

Synthetic verification run:
`1105b48a-a21f-4176-a04b-80175b011d23`.

The ephemeral server was stopped after verification so the known synthetic
test tokens were not left active. No token was written to the repository,
workflow export, SQLite, or an artifact.

## Installed n8n workflow verification

Before import, the existing workflow was exported and confirmed to:

- have a name beginning with `CODEX TEST`;
- be inactive;
- be unavailable through MCP;
- contain zero credential-bearing nodes.

The repository export was then imported over workflow ID
`CodexStrategyV01` and re-exported. The original 2026-07-13 installed result
confirmed:

| Check | Result |
| --- | --- |
| Form Trigger version | `2.6` |
| Form authentication | `n8nUserAuth` |
| Include authenticated user in output | `true` |
| Active | `false` |
| Available through MCP | `false` |
| Save successful executions | `none` |
| Save failed executions | `none` |
| Save manual executions | `false` |
| Credential-bearing nodes | 0 |

The installed n8n Form implementation was inspected read-only and confirmed
that later Form nodes inherit n8n User Auth from the trigger and propagate the
authenticated user. The editable reviewer field is absent; the review request
uses only the opaque authenticated user ID.

The in-app browser surface was unavailable during verification, so no visual
editor test form was opened. The production form URL returned HTTP 404, as
required for the inactive/unpublished workflow. Human-auth configuration was
verified through automated export tests, installed-node behavior, and n8n
import/re-export rather than by activating or publishing the form.

## Secret and export boundary

- Workflow HTTP nodes reference `$env.AI_FACTORY_SERVICE_TOKEN` and
  `$env.AI_FACTORY_REVIEW_TOKEN`; values are not embedded.
- Service and review tokens must be distinct and at least 32 characters.
- Optional timezone-aware expiry values fail closed.
- The reviewer body value and actor header both derive from `$json.user.id`.
- No existing n8n credential was created or modified.
- No workflow was activated, published, or made available through MCP.

## Completion decision

Stage 9.1 is complete for the local synthetic lab. Stage 9.2 run ownership and
isolation remains the next operationalization checkpoint, but it is deferred
until multiple users, publication, a controlled client demonstration, or pilot
preparation becomes a concrete requirement. Authentication must not be
represented as client/tenant isolation, and real data remains prohibited.

## Startup integration follow-up

On 2026-07-14, repository startup was tightened so `scripts/start.sh` and
`scripts/agent-start.sh` automatically load the ignored `.env` and reject
missing, short, or identical tokens. The n8n startup uses the repository-owned
`compose.n8n-auth.yml` override to pass both tokens into the container without
embedding values in workflow JSON or tracked files. `scripts/status.sh` checks
only whether the container configuration is valid and never prints a token.

The same override explicitly sets `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` for the
checked-in workflow's `$env` token expressions. This is a local synthetic-lab
compatibility exception: any workflow expression can read environment values
exposed to the n8n container. It does not satisfy pilot-grade secret isolation,
does not relax the no-pilot decision, and must be replaced or re-evaluated
before real data is considered.

## Live authenticated form verification

Date: 2026-07-14 (`Europe/Copenhagen`)

The inactive, unpublished `CODEX TEST — AI Strategy Factory v0.1` workflow was
run manually with the built-in synthetic community-garden example. No
credential was created or modified, and no real, personal, confidential, or
client data was submitted.

Live result:

| Check | Result |
| --- | --- |
| n8n execution | `81` — `success` |
| API run ID | `09c130e4-190d-452c-aa76-2a3c8b85dcee` |
| Human authentication | Signed-in n8n user required across form pages |
| Service authentication | Environment-backed service token accepted |
| Review authentication | Distinct review token and opaque actor binding accepted |
| Quality report | Created locally; one medium objective-quality issue recorded |
| Human decision | Explicit approval with a synthetic-test-only caveat |
| Approved artifact | `artifacts/strategy-09c130e4-190d-452c-aa76-2a3c8b85dcee.md` |
| Production form | Unpublished/inactive |

The approval comment requires a specific conversion target, deadline, owner,
and capacity rationale before operational use. The generated quality report and
approved artifact are ignored by Git and remain local synthetic evidence.

During the live test, n8n 2.29 returned no execution status when manual
execution persistence was disabled. Enabling **Save manual executions** allowed
the stored execution to move through the later form page and complete. The
tracked workflow now records `saveManualExecutions: true`; production success
and error persistence remain `none`.

This compatibility setting means synthetic form and uploaded JSON content can
remain in the local n8n database until the local lab operator deletes the
manual execution. It does not relax the synthetic-only/no-pilot decision and
must be replaced by governed retention and secret isolation before a pilot.
