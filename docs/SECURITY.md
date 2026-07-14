
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

- Success, error, and manual execution persistence is disabled on the Stage 8
  workflow to reduce upload retention. Stage 9 must define authentication,
  ownership, retention, deletion, privacy, and abuse controls before any pilot.

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
