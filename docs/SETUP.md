# AI Strategy Factory setup

This is the canonical clean-machine setup for the local AI Strategy Factory on
macOS. The supported boundary is a local synthetic-data lab. Do not use real or
confidential client data, and keep the n8n workflow inactive and unpublished.

## What runs where

| Component | Runtime | Address | Purpose |
| --- | --- | --- | --- |
| Docker Desktop | macOS | n/a | Runs n8n and PostgreSQL containers |
| n8n 2.29.10 | Docker | http://127.0.0.1:5678 | Workflow orchestration and human review |
| PostgreSQL 18.4 | Docker | `127.0.0.1:5432` | FastAPI application database |
| Ollama | macOS | http://127.0.0.1:11888 | Optional local generation and critique |
| FastAPI/Uvicorn | macOS | http://127.0.0.1:8000 | AI Strategy Factory API |

n8n reaches FastAPI through `http://host.docker.internal:8000`. The repository
owns both Compose definitions; no external n8n directory is required.

## 1. Install prerequisites

Install:

- Git.
- Docker Desktop for Mac: <https://docs.docker.com/desktop/setup/install/mac-install/>.
- Ollama for macOS: <https://docs.ollama.com/macos>.
- `uv`: <https://docs.astral.sh/uv/getting-started/installation/>.
- `jq` (for health and verification scripts).

With Homebrew already installed, the command-line prerequisites can be
installed with:

```bash
brew install git uv jq
```

Install Docker Desktop and Ollama from their official macOS installers, launch
each once, and allow their command-line tools to be added to `PATH`.

Verify the prerequisites:

```bash
git --version
docker compose version
ollama --version
uv --version
jq --version
openssl version
curl --version
```

Docker Desktop must be installed, but it does not need to be running before the
normal startup command; the startup wrapper opens it when necessary.

## 2. Clone the repository

```bash
git clone https://github.com/cpgrant/n8n-codex-lab.git
cd n8n-codex-lab
```

The repository is private, so GitHub authentication is required to clone it.

## 3. Configure the local environment

Create the ignored local environment file:

```bash
cp .env.example .env
```

Generate three different secrets. Run this command three times:

```bash
openssl rand -hex 32
```

Edit `.env` and set:

```text
AI_FACTORY_POSTGRES_PASSWORD=<first generated value>
AI_FACTORY_SERVICE_TOKEN=<second generated value>
AI_FACTORY_REVIEW_TOKEN=<third generated value>
AI_FACTORY_DEFAULT_DATABASE=postgresql
```

The service and review tokens must be different and at least 32 characters.
Never commit `.env`, paste its values into workflow JSON, or store them in n8n
fields intended for non-secret data. See `docs/AUTHENTICATION-TOKENS.md` for
rotation and optional expiration.

Leave `AI_FACTORY_PROVIDER=fake` and `AI_FACTORY_QUALITY_MODE=basic` for the
fastest deterministic first run. Ollama is enabled explicitly later.

## 4. Install the FastAPI environment

```bash
cd agent-service
uv sync --extra dev
cd ..
```

`uv` installs the project Python version when necessary and creates the local
`.venv`. No global Python packages are required.

## 5. Install the Ollama model

The repository starts its own Ollama listener on port `11888`, separate from
Ollama's conventional port. Download the configured model before the first live
generation:

```bash
OLLAMA_HOST=127.0.0.1:11888 ollama serve
```

Keep that terminal open temporarily. In a second terminal, from the repository
root, run:

```bash
OLLAMA_HOST=http://127.0.0.1:11888 ollama pull gemma4:31b
```

Stop the temporary server with `Ctrl-C`. Normal startup subsequently manages
the repository listener. The model is large; confirm that the Mac has enough
free disk space and memory. Deterministic `fake` mode does not require a model.

## 6. Start the complete system

From the repository root:

```bash
scripts/system-start.sh
```

The command:

1. opens Docker Desktop when necessary and waits for the engine;
2. starts the repository-owned PostgreSQL container;
3. builds and starts the repository-owned n8n container;
4. starts the repository-managed Ollama listener; and
5. starts FastAPI in the foreground.

The first run downloads Docker images and builds the pinned n8n image with
FFmpeg, so it takes longer than later starts. Keep the terminal open while
FastAPI is running.

The equivalent manual sequence is:

```bash
scripts/postgres-start.sh
scripts/start.sh
scripts/agent-start.sh
```

## 7. Complete the one-time n8n setup

1. Open <http://127.0.0.1:5678>.
2. Create the local n8n owner account when prompted. Use local test-account
   information; do not use client credentials.
3. Import `workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json`.
4. Confirm that its name begins with `CODEX TEST`.
5. Keep it inactive and unpublished.

Do not modify existing n8n credentials. The checked-in workflow obtains the
two local FastAPI tokens from its container environment and must be used only
with synthetic input.

## 8. Verify all components

Keep `scripts/system-start.sh` running and use a second terminal:

```bash
cd n8n-codex-lab
scripts/postgres-status.sh
scripts/status.sh
scripts/agent-check.sh
curl -fsS http://127.0.0.1:11888/api/tags | jq '.models[].name'
```

Expected results:

- PostgreSQL reports healthy on `127.0.0.1:5432`.
- n8n reports running and is reachable on port `5678`.
- FastAPI returns an `ok` health status on port `8000`.
- Ollama lists `gemma4:31b` when the live provider will be used.

Run the automated local checks:

```bash
node scripts/verify-stage8-intake.js
node scripts/verify-stage9-5-lite.js
scripts/verify-stage9-3-lite.sh
cd agent-service
uv run pytest -q
```

## 9. Run the first synthetic workflow test

In n8n, open the imported inactive workflow and select **Execute workflow**.
Use its temporary `/form-test/...` URL and choose **Load synthetic example**.
Do not activate or publish the workflow to obtain a permanent URL.

The default `fake` provider produces a deterministic strategy without calling
Ollama. For live local generation, stop FastAPI with `Ctrl-C`, set these values
in the ignored `.env`, and restart with `scripts/agent-start.sh`:

```text
AI_FACTORY_PROVIDER=ollama
AI_FACTORY_QUALITY_MODE=pro
OLLAMA_MODEL=gemma4:31b
OLLAMA_QUALITY_MODEL=gemma4:31b
```

Run `scripts/agent-smoke-stage6-ollama.sh` or the synthetic n8n form again.
The first live request may take several minutes while the model loads.

## 10. Stop safely

Stop FastAPI with `Ctrl-C`, then run:

```bash
scripts/system-stop.sh
```

This stops the repository-managed Ollama process, n8n, and PostgreSQL without
deleting their persistent volumes, the SQLite rollback file, artifacts, or
backups. Never use `docker compose down --volumes` for routine shutdown.

## Troubleshooting and next steps

- Known startup and connectivity problems: `docs/TROUBLESHOOTING.md`.
- Daily commands after installation: `docs/DAILY-OPERATIONS.md`.
- PostgreSQL migration and rollback: `docs/POSTGRESQL-MIGRATION-RUNBOOK.md`.
- Backup and recovery: `docs/BACKUP-AND-RECOVERY.md`.
- Authentication tokens: `docs/AUTHENTICATION-TOKENS.md`.
