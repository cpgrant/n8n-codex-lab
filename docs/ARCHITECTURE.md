# ARCHITECTURE

```text
Codex -> MCP -> n8n -> Workflows
```

AI Strategy Factory v0.1 adds a separate local service without replacing the
existing path:

```text
Codex -> MCP -> n8n (Docker)
                   |
                   v
         FastAPI service (macOS) -> SQLite
```

Stage 2 exposes health and synchronous strategy-run create/read endpoints. It
uses `FakeStrategyProvider` and SQLite. Review, artifact creation, real model
calls, and the n8n factory workflow are later stages.
