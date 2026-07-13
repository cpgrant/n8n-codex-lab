
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
