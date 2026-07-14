# Authentication tokens

Stage 9.1 uses two private shared secrets between n8n and FastAPI. These are
local application tokens, not credentials obtained from OpenAI, n8n, Ollama,
or another provider.

## What each token does

- `AI_FACTORY_SERVICE_TOKEN` authorizes normal n8n-to-FastAPI operations such
  as creating and reading synthetic strategy runs.
- `AI_FACTORY_REVIEW_TOKEN` separately authorizes approval and rejection
  operations. Keeping it distinct limits the authority of the normal service
  token.

Both are required, must be different, and must contain at least 32 characters.

## Generate and configure them

Run this command twice in a terminal:

```bash
openssl rand -hex 32
openssl rand -hex 32
```

Each command prints a different 64-character random value. Paste the first
value after `AI_FACTORY_SERVICE_TOKEN=` and the second after
`AI_FACTORY_REVIEW_TOKEN=` in the repository's ignored `.env`:

```dotenv
AI_FACTORY_SERVICE_TOKEN=<first generated value>
AI_FACTORY_REVIEW_TOKEN=<second generated value>
```

Replace the angle-bracket examples completely; do not include `<` or `>`.
Never place the real values in `.env.example`, workflow JSON, documentation,
Git, screenshots, or chat.

## Optional expiration

For this local synthetic lab, leave the expiration fields present and empty:

```dotenv
AI_FACTORY_SERVICE_TOKEN_EXPIRES_AT=
AI_FACTORY_REVIEW_TOKEN_EXPIRES_AT=
```

Empty means the tokens do not expire automatically. To enforce expiration,
enter a future timezone-aware ISO 8601 timestamp, for example:

```dotenv
AI_FACTORY_SERVICE_TOKEN_EXPIRES_AT=2026-08-01T00:00:00Z
AI_FACTORY_REVIEW_TOKEN_EXPIRES_AT=2026-08-01T00:00:00Z
```

Expired tokens are rejected. Generate new values, update `.env`, and restart
both processes when rotating tokens.

## Start and verify

Run n8n and FastAPI in separate terminals:

```bash
# Terminal 1
scripts/start.sh

# Terminal 2
scripts/agent-start.sh
```

Both scripts load the same `.env` automatically. `scripts/start.sh` passes the
tokens to n8n, while `scripts/agent-start.sh` supplies them to FastAPI. Startup
stops safely if either token is missing, too short, or identical.

Check the running services without displaying token values:

```bash
scripts/status.sh
scripts/agent-check.sh
```
