# AI Factory Platform ideas and options

## Purpose

This document records promising platform directions that have not yet been
accepted as implementation commitments. It keeps exploratory architecture and
factory ideas separate from the canonical roadmap.

An idea moves into `docs/ROADMAP.md` as planned work only after its value,
scope, safety boundary, dependencies, and completion criteria are explicitly
accepted. Implemented architecture belongs in `docs/ARCHITECTURE.md` only after
it exists and has been verified.

## Decision status

| Option | Current status | Suggested next decision |
| --- | --- | --- |
| Knowledge Factory and shared evidence layer | Recommended candidate | Define a small synthetic contract |
| LangGraph or another durable agent runtime | Evaluation option | Run only when a bounded use case requires it |
| Multiple specialist agents | Evaluation option | Start with typed roles inside one controlled run |
| Additional MCP servers | Add only as needed | Establish an admission policy before installation |

## Knowledge Factory / LLM Wiki

### Opportunity

A Knowledge Factory would turn approved source material into durable,
reviewed, versioned knowledge artifacts. It could become a shared evidence
layer for Strategy, Podcast, Job Application, Research and Content
Repurposing factories.

Unlike a simple retrieval-augmented answer, the factory would preserve both
the source evidence and the reviewed output:

```text
approved sources
-> validate and register
-> extract and index passages
-> retrieve evidence
-> map claims to sources
-> check citations, conflicts, gaps, and freshness
-> human review
-> approved knowledge artifact or wiki page
```

Possible outputs:

- evidence packs and source summaries;
- topic pages, FAQs, timelines, and glossaries;
- claim-to-source matrices;
- research briefs and fact-checking reports;
- versioned wiki pages that distinguish quoted facts from AI interpretation.

### Required controls

- retain source URI, title, author, date, checksum, version, and permission;
- show citations at claim level where practical;
- distinguish source content, extracted metadata, and generated synthesis;
- preserve conflicting evidence and uncertainty rather than silently merging
  it;
- detect stale sources and broken citations;
- prohibit unsupported claims from becoming approved knowledge;
- keep ingestion synthetic or explicitly licensed under the current lab
  boundary;
- require human approval before generated material becomes approved knowledge.

### Small first experiment

Use a checked-in synthetic source pack to produce one cited topic page and one
evidence matrix. Reuse the existing immutable-run, quality-report, human-review,
artifact-checksum, and synthetic-verification patterns.

Do not start by building a general enterprise knowledge base, crawler, or
autonomous web researcher.

## Agent orchestration option

### Where an agent runtime may help

A durable graph runtime such as LangGraph may be useful when a factory needs:

- resumable execution across long-running model or tool calls;
- bounded research or revision loops;
- conditional branches based on structured state;
- parallel specialist work with a deterministic join;
- checkpoints that can pause for human approval;
- progress streaming, retry, cancellation, and recovery.

The likely first use case is a Knowledge or Research Factory:

```text
plan research
-> retrieve sources
-> assess source quality
-> identify evidence gaps
-> retrieve again if needed (bounded)
-> synthesize
-> verify citations
-> human review
```

The current Strategy Factory is mostly linear and does not yet justify another
orchestration runtime.

### Proposed responsibility boundary

If adopted later:

- n8n remains the visible business workflow, forms, and human-review layer;
- FastAPI remains the domain-policy, authorization, run, and artifact API;
- the agent runtime executes bounded reasoning graphs behind FastAPI;
- MCP remains an integration boundary for approved tools and information;
- SQLite or a later approved datastore remains the durable system of record.

### Multi-agent constraints

Prefer one orchestrator with constrained specialist roles over an unrestricted
agent conversation. Candidate roles include researcher, drafter, critic, and
citation verifier.

Every role should have:

- typed input and output contracts;
- an explicit tool allowlist;
- a maximum iteration count and wall-clock timeout;
- model-call and cost budgets where hosted providers are used;
- durable run and step identifiers;
- idempotent retry behavior;
- safe error handling and observable progress;
- human approval before consequential external actions.

Adopt an agent runtime only if a small proof of concept is materially clearer
or more reliable than implementing the same flow with the existing n8n and
FastAPI components.

## MCP integration options

MCP servers should be installed to satisfy a defined factory requirement, not
to create a broad collection of tools. Each server expands the information or
actions available to models and therefore expands the trust boundary.

### Potentially useful servers or capabilities

| Capability | Potential use | Initial posture |
| --- | --- | --- |
| Knowledge search | Retrieve approved passages with citations and source metadata | High-value candidate; read-only |
| n8n workflow access | Inspect, validate, export, and test permitted `CODEX TEST` workflows | Useful; read-only first, never activate or publish automatically |
| Browser testing | Exercise local forms and inspect synthetic user journeys | Useful for verification; local synthetic targets only |
| GitHub | Read issues, roadmap decisions, reviews, and release checkpoints | Add when remote collaboration needs it; limit repository scope |
| Approved artifact retrieval | Provide strategies, reports, scripts, and knowledge artifacts to other factories | Consider after a stable artifact catalog exists; read-only |
| Product documentation | Retrieve current framework and API documentation | Useful when maintained and source provenance is clear |
| Direct database access | Query SQLite or a later datastore | Avoid initially; prefer authorized domain APIs |
| General filesystem access | Read or write arbitrary files | Avoid; repository-scoped tools already exist |
| Email, calendar, publishing, or submission | Deliver content or applications | Defer; consequential writes require separate policy and human approval |

### MCP server admission checklist

Before installing or enabling a server, record:

1. the exact factory requirement it satisfies;
2. whether it is official, community-maintained, or locally owned;
3. its maintainer, version, update method, and removal procedure;
4. whether it runs locally or sends information to a third party;
5. every resource and tool it exposes;
6. its filesystem, network, credential, and data permissions;
7. authentication, authorization, and secret-delivery behavior;
8. whether tools can be made read-only or separately approved;
9. logging, retention, redaction, timeout, and rate-limit behavior;
10. prompt-injection and untrusted-content exposure;
11. synthetic negative tests for unauthorized and consequential actions;
12. the human-approval boundary for writes, messages, publication, or
    submission.

MCP access must not bypass FastAPI authorization, artifact integrity checks,
n8n workflow restrictions, or explicit human approval.

## Possible future roadmap proposals

These labels are placeholders for later decisions, not active roadmap stages:

- **P1 — Knowledge and evidence layer:** source registry, provenance,
  retrieval, citations, evidence quality, and reviewed knowledge artifacts.
- **P2 — Agent-runtime evaluation:** bounded proof of concept for durable
  Knowledge Factory research, compared with the existing stack.
- **P3 — MCP governance and selected integrations:** admission policy plus the
  minimum read-only servers required by accepted factory use cases.

## Recommended evaluation order

1. Define the Knowledge Factory's synthetic input, evidence, quality, review,
   and artifact contracts.
2. Test the contract with the current n8n, FastAPI, and provider pattern.
3. Continue the planned Podcast Factory using a synthetic evidence pack.
4. Identify capabilities genuinely repeated by Strategy, Knowledge, and
   Podcast flows.
5. Evaluate a durable agent runtime against one bounded research loop.
6. Add only the MCP capabilities required by an accepted experiment.
7. Move successful options into the roadmap and architecture with verification
   evidence.

This order preserves a simple working platform while allowing evidence-backed
experimentation with knowledge, agents, and integrations.
