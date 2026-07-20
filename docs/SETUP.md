# AI Strategy Factory setup

This is the canonical clean-machine setup for the local AI Strategy Factory on
macOS. The supported boundary is a local synthetic-data lab. Do not use real or
confidential client data, and keep the n8n workflow inactive and unpublished.

This guide covers installation, configuration, startup, verification, the first
synthetic workflow run, and safe shutdown. If the machine is already configured,
use the daily commands below.

## Daily start, status, and stop

From the repository root, start the complete system with:

```bash
scripts/system-start.sh
```

The command starts Docker Desktop when required, then PostgreSQL, n8n, Ollama,
and FastAPI in dependency order. FastAPI remains in the foreground, so keep that
terminal open.

In a second terminal, check the system with:

```bash
scripts/postgres-status.sh
scripts/status.sh
scripts/agent-check.sh
curl -fsS http://127.0.0.1:11888/api/tags | jq '.models[].name'
```

Stop FastAPI with `Ctrl-C` in its terminal, then stop the remaining services
without deleting persistent data:

```bash
scripts/system-stop.sh
```

## What runs where

| Component | Version source | Runtime | Address | Purpose |
| --- | --- | --- | --- | --- |
| Docker Desktop | Locally installed | macOS | n/a | Runs n8n and PostgreSQL containers |
| n8n 2.29.10 | Pinned in `Dockerfile.n8n` | Docker | http://127.0.0.1:5678 | Workflow orchestration and human review |
| PostgreSQL 18.4 | Pinned in `compose.postgres.yml` | Docker | `127.0.0.1:5432` | Authoritative application database |
| Ollama | Locally installed | macOS | http://127.0.0.1:11888 | Optional local generation and critique |
| FastAPI 0.139.0 / Uvicorn 0.51.0 | Locked in `agent-service/uv.lock` | macOS | http://127.0.0.1:8000 | AI Strategy Factory API |

n8n reaches FastAPI through `http://host.docker.internal:8000`. The repository
owns both Compose definitions; no external n8n directory is required.

## Version inventory

The following versions define or describe the verified development environment
as of 20 July 2026. Pinned and locked versions are reproducible project inputs.
Observed versions document the machine used for verification; they are not all
minimum requirements.

### Repository-pinned and locked versions

| Component | Version | Source |
| --- | --- | --- |
| n8n | 2.29.10 | `Dockerfile.n8n` and `compose.n8n.yml` |
| PostgreSQL | 18.4 (`bookworm`) | `compose.postgres.yml` |
| Python | Requires 3.11 or newer; project environment resolved to 3.12.11 | `agent-service/pyproject.toml` and `uv.lock` |
| FastAPI | 0.139.0 | `agent-service/uv.lock` |
| Uvicorn | 0.51.0 | `agent-service/uv.lock` |
| Ollama model | `gemma4:31b` | `.env.example` and setup commands |

### Observed local tool versions

| Tool | Verified version |
| --- | --- |
| macOS | 26.5.2 |
| Git | 2.53.0 |
| Docker CLI | 29.6.1 |
| Docker Compose | 5.3.0 |
| Ollama client | 0.32.1 |
| `uv` | 0.10.4 |
| `jq` | 1.7.1 |
| OpenSSL | 3.6.1 |
| Codex CLI (optional development tool) | 0.144.6 |

Codex was used to develop and verify the repository, but it is not a runtime
dependency of the submitted application. The default deterministic provider
also does not require the Ollama model.

## 1. Install prerequisites

Install:

- Git.
- Docker Desktop for Mac: <https://docs.docker.com/desktop/setup/install/mac-install/>.
- Ollama for macOS: <https://docs.ollama.com/macos>.
- `uv`: <https://docs.astral.sh/uv/getting-started/installation/>.
- `jq` (for health and verification scripts).

The Codex CLI is optional and is needed only for Codex-assisted development or
MCP inspection; the application runs without it.

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
# Optional development tool:
codex --version
```

Docker Desktop must be installed, but it does not need to be running before the
normal startup command; the startup wrapper opens it when necessary.

## 2. Clone the repository

```bash
git clone https://github.com/cpgrant/n8n-codex-lab.git
cd n8n-codex-lab
```

The repository is public and can be cloned without GitHub authentication:
<https://github.com/cpgrant/n8n-codex-lab>.

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
`.venv`. No global Python packages are required. Confirm the resolved runtime
and locked framework versions with:

```bash
cd agent-service
uv run python --version
uv run python -c 'import fastapi, uvicorn; print(f"FastAPI {fastapi.__version__}"); print(f"Uvicorn {uvicorn.__version__}")'
cd ..
```

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

From the repository root, use the same daily startup command described above:

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

To inspect the installed runtime versions directly:

```bash
docker exec n8n n8n --version
docker exec codex-test-ai-factory-postgres postgres --version
ollama --version
uv --version
jq --version
```

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
