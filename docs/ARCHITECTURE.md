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

Stage 3 exposes health, synchronous strategy-run create/read, explicit human
approval/rejection, and approved Markdown retrieval. It uses
`FakeStrategyProvider`, SQLite, and repository-local ignored artifact storage.
Real model calls and the n8n factory workflow are later stages.
