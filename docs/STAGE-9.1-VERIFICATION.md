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
`CodexStrategyV01` and re-exported. The installed result confirmed:

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
isolation is next. Until that checkpoint is complete, authentication must not
be represented as client/tenant isolation, and real data remains prohibited.
