# Stage 9.1 authentication and authorization design

Status: **Implementation contract**

## Objective

Stage 9.1 adds two independent authentication boundaries while preserving the
synthetic-only policy and explicit human review:

```text
Authenticated n8n user -> protected multi-page form
                                  |
                                  v
                         n8n service identity -> FastAPI
                                  |
                   separate review identity + human actor assertion
                                  v
                         approve or reject exact draft
```

Authentication does not establish run ownership or tenant isolation. Those are
Stage 9.2 controls. No real-data pilot is authorized.

## Identities

| Identity | Authentication | Permitted use |
| --- | --- | --- |
| Human reviewer | n8n User Auth on Form Trigger v2.6; inherited by later form pages | Open intake, submit synthetic input, view the generated review page, and make an explicit review decision |
| n8n service | `AI_FACTORY_SERVICE_TOKEN` bearer token | Create/read runs, create/read quality reports, and retrieve artifacts |
| n8n review service | distinct `AI_FACTORY_REVIEW_TOKEN` bearer token plus `X-AI-Factory-Actor-ID` | Submit an approval or rejection asserted on behalf of the authenticated n8n user |
| Local operator | Local process and secret-store administration | Configure, rotate, expire, and revoke service tokens; cannot bypass human review through the workflow |

The workflow sends the opaque n8n user ID as the review actor. It does not send
the user's email or name to FastAPI or store them in strategy artifacts.

## Endpoint authorization matrix

| Endpoint | Required scope |
| --- | --- |
| `GET /health` | Public local health check; returns no protected data |
| `POST /v1/strategy-runs` | Service |
| `GET /v1/strategy-runs/{run_id}` | Service |
| `POST/GET /v1/strategy-runs/{run_id}/quality-report` | Service |
| `GET /v1/strategy-runs/{run_id}/quality-report/artifact` | Service |
| `POST /v1/strategy-runs/{run_id}/review` | Review plus actor ID |
| `GET /v1/strategy-runs/{run_id}/artifact` | Service |

The review request body must use the same opaque reviewer ID as the trusted
actor header. A mismatch is denied before the decision is stored.

## Secret configuration

FastAPI reads secrets only from its process environment:

- `AI_FACTORY_SERVICE_TOKEN`
- `AI_FACTORY_REVIEW_TOKEN`
- optional `AI_FACTORY_SERVICE_TOKEN_EXPIRES_AT`
- optional `AI_FACTORY_REVIEW_TOKEN_EXPIRES_AT`

Tokens must be distinct and contain at least 32 characters. Expiry values are
timezone-aware ISO 8601 timestamps. Missing required configuration leaves
`/v1` closed with a client-safe `503`; it never falls back to anonymous access.

n8n reads the same tokens from its process environment in workflow
expressions. Secrets must be injected through untracked local runtime
configuration. They must not be placed in workflow JSON, Git, form fields,
request bodies, URLs, logs, or n8n variables intended for non-secret data.

Rotation requires configuring new distinct tokens in both processes and
restarting them. Revocation removes or replaces the token and restarts the
process. Expiry provides a fail-closed deadline; Stage 9.1 does not implement a
token refresh endpoint.

## Denial behavior

| Condition | HTTP | Code |
| --- | ---: | --- |
| Missing bearer token | 401 | `AUTHENTICATION_REQUIRED` |
| Malformed or unknown bearer token | 401 | `AUTHENTICATION_INVALID` |
| Valid but expired token | 401 | `AUTHENTICATION_EXPIRED` |
| Valid token used for the wrong scope | 403 | `AUTHORIZATION_DENIED` |
| Missing, malformed, or mismatched review actor | 403 | `AUTHORIZATION_DENIED` |
| Required server token is not configured | 503 | `AUTHENTICATION_NOT_CONFIGURED` |

Authentication is evaluated before request-body validation and run lookup.
Denials use the normal safe error envelope and request ID, never reveal token
values, and do not distinguish unknown run IDs.

## Human form protection

The exported `CODEX TEST` workflow uses Form Trigger v2.6 with
`authentication: n8nUserAuth` and authenticated-user propagation enabled.
Multi-page Form nodes inherit that authentication in the installed n8n
version. The editable reviewer field is removed; the final review request uses
the authenticated user's opaque ID.

The workflow remains inactive, unpublished, credential-free, and unavailable
through MCP. Production form URLs therefore remain unavailable. Authentication
does not constitute approval to activate or publish it.

## Trust and limitations

- FastAPI trusts n8n to assert the human actor only when the distinct
  review-scoped token is valid.
- Tokens authenticate the calling service, not a run owner or tenant.
- Any holder of the review token could assert an actor ID; restricting and
  rotating that secret is essential. Stronger end-user claims and ownership
  binding belong to Stage 9.2.
- Static bearer tokens do not provide per-request replay prevention;
  idempotency continues to prevent duplicated mutations.
- TLS termination is not introduced for the Mac-local Docker boundary in this
  checkpoint. Publication or remote access remains prohibited.

## Completion criteria

- every `/v1` endpoint fails closed without its required token;
- service and review scopes cannot substitute for one another;
- expired tokens and invalid actor assertions fail safely;
- health remains content-free and available for local operations;
- n8n form pages require a signed-in n8n user;
- no secret or credential reference is embedded in the workflow export;
- approval/rejection remains explicit, immutable, idempotent, and attributable
  to an opaque authenticated actor;
- automated tests and synthetic operational verification pass;
- the workflow remains inactive, unpublished, and unavailable through MCP.
