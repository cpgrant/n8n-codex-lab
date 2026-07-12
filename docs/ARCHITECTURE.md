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
At that checkpoint, real model calls and the n8n factory workflow remained
later stages.

Stage 4 adds the inactive n8n form workflow:

```text
Human test form -> n8n (Docker) -> FastAPI (macOS) -> SQLite
       review decision |                    |
                       +--------------------+-> approved Markdown artifact
```

n8n reaches the Mac service through `host.docker.internal:8000`. The workflow
remains inactive and unpublished unless separately approved.

Stage 6 adds an optional local model path without changing the n8n workflow:

```text
n8n (Docker) -> FastAPI :8000 -> Ollama :11888 -> gemma4:31b
                              -> SQLite
                              -> approved Markdown artifact
```

`FakeStrategyProvider` remains the deterministic test default.
`OllamaStrategyProvider` is selected only through the FastAPI process
environment. Ollama never receives review decisions, writes SQLite records, or
creates artifacts.
