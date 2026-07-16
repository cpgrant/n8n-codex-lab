
# Security

- Treat the n8n MCP token as a secret.

- Never commit the real token.

- Keep `.env` out of Git.

- Regenerate the token if it is exposed.

- Enable MCP only for approved workflows.

- Keep production credentials unavailable to test workflows.

- Use `AGENTS.md` rules to constrain Codex.

- Review changes before publishing workflows.

- Keep `CODEX TEST — AI Strategy Factory v0.1` inactive, unpublished, and
  unavailable through MCP unless separately approved.

- Use synthetic data only. Stage 8 is not authorization to accept real,
  personal, confidential, or client data.

- Stage 8 JSON intake accepts one `.json` object up to 64 KiB, rejects unknown
  fields, discards binary input before the API call, and never uses an uploaded
  filename as an artifact path.

- Production success and error execution persistence is disabled. Manual
  execution persistence is enabled for the local synthetic lab because n8n
  2.29 multi-page test forms require a stored waiting execution. Saved manual
  runs can retain synthetic form and uploaded JSON data in the local n8n
  database until the local operator deletes them. This exception is not
  authorization for real data or a substitute for pilot retention controls.
- Stage 9.3-lite makes n8n's 14-day rolling execution pruning explicit and caps
  saved executions at 500. A read-only audit lists only `CODEX TEST` execution
  metadata; deletion remains a confirmed operator action in the n8n UI.
- Local factory backups are ignored by Git, use owner-only permissions, and
  contain complete synthetic briefs, drafts, reviews, reports, and artifacts.
  Treat them as content-bearing data. The 30-day backup audit does not delete
  files automatically.

- The Stage 9.0 data classification, trust boundaries, interim ownership, and
  pilot gates are defined in `docs/STAGE-9.0-DATA-POLICY.md`. They are policy
  requirements, not implemented authentication or authorization controls.

- No real-data pilot may proceed until named service/business, security,
  privacy, operations, incident-response, and pilot-sponsor ownership is
  recorded and the later Stage 9 controls are verified.

- Stage 9.1 requires n8n User Auth on every strategy form page and distinct,
  environment-backed FastAPI service and review bearer tokens. Tokens must be
  at least 32 characters, differ from one another, and remain outside Git and
  workflow exports.

- Missing API authentication configuration fails closed. Review calls also
  require the opaque authenticated n8n user ID, and the stored reviewer must
  match it. This is authentication, not run ownership or tenant isolation.

- The local Compose override sets `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` because
  the checked-in workflow reads its two FastAPI tokens through `$env`. This
  permits workflow expressions to read every environment variable exposed to
  the n8n container, so it is a synthetic-lab exception rather than a pilot
  secret-management design. Only approved `CODEX TEST` workflows may use it.
