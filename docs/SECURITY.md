
# Security

- Treat the n8n MCP token as a secret.

- Never commit the real token.

- Keep `.env` out of Git.

- Regenerate the token if it is exposed.

- Enable MCP only for approved workflows.

- Keep production credentials unavailable to test workflows.

- Use `AGENTS.md` rules to constrain Codex.

- Review changes before publishing workflows.

