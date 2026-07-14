# ARCHITECTURE

This document describes the implemented Strategy Factory reference
architecture. The broader multi-factory objective and the boundary between
shared platform and factory-specific capabilities are in
`docs/AI-FACTORY-PLATFORM.md`. Shared abstractions have not yet been extracted
from a second factory.

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

Stage 7 adds a quality report without changing the run-state machine:

```text
stored brief + immutable draft
              |
              +-> deterministic checks ------------------+
              |                                           |
              `-> optional Ollama critic (`pro` mode) -----+-> quality report
                                                               |
                                                               v
                                                        human review
```

The service binds the report to the draft checksum and stores it in SQLite.
The quality critic receives no review decision and cannot mutate the draft.
Stage 7.0.1 also renders that stored report under
`artifacts/quality-reports/quality-report-<run_id>.md`. Its metadata is stored
separately from the human-approved strategy artifact and retrieval verifies
the recorded checksum.

Stage 9.1 adds independent human and service authentication:

```text
signed-in n8n user -> n8n User Auth protected form pages
                              |
               service token | normal run/report/artifact operations
                review token | review + opaque authenticated actor ID
                              v
                           FastAPI
```

Tokens are injected into process environments and are absent from the workflow
export. FastAPI fails closed when a required token is missing. The distinct
review scope preserves approval/rejection as a separate authorized action.
Stage 9.1 does not yet bind runs to owners or tenants.
