# Professional n8n Codex Lab Manual

This is the navigation page for the maintained lab documentation. The project
currently provides a complete local synthetic Strategy Factory vertical slice,
not a production-ready multi-factory service.

## Start here

- Platform objective and factory catalog: `docs/AI-FACTORY-PLATFORM.md`
- Canonical roadmap and current decision gate: `docs/ROADMAP.md`
- Installation and local setup: `docs/SETUP.md`
- Daily startup and shutdown: `docs/DAILY-OPERATIONS.md`
- Implemented system architecture: `docs/ARCHITECTURE.md`
- Strategy Factory specification: `docs/AI-STRATEGY-FACTORY.md`
- FastAPI interface: `docs/API.md`
- Authentication token operation: `docs/AUTHENTICATION-TOKENS.md`
- Data policy and pilot gates: `docs/STAGE-9.0-DATA-POLICY.md`
- Security model: `docs/SECURITY.md`
- Known problems and recovery: `docs/TROUBLESHOOTING.md`

## Current operating boundary

- Use synthetic data only.
- Work only with workflows whose names begin with `CODEX TEST`.
- Keep workflows inactive and unpublished without explicit approval.
- Do not modify existing credentials or commit secrets.
- Keep generation, quality advice, human approval, and external delivery as
  separate decisions.

The Strategy Factory is the reference implementation. Podcast and Job
Application factories are confirmed future directions; Research and Briefing
and Content Repurposing are candidate ideas. Their scope and additional safety
gates are recorded in `docs/AI-FACTORY-PLATFORM.md` and `docs/ROADMAP.md`.
