# AI Factory Platform

## Objective

Build a local-first platform for creating specialized, human-reviewed AI
factories. Each factory turns a bounded input into a checked, reviewable
artifact through a repeatable workflow. The Strategy Factory is the first
reference implementation; it is not the final extent of the platform.

The platform should make new factories easier to build without forcing every
factory into one premature generic framework.

Exploratory Knowledge Factory, agent-runtime, and MCP integration options are
kept separately in `docs/PLATFORM-IDEAS.md` until they are accepted as roadmap
commitments.

## Shared factory lifecycle

Every factory should use the same high-level control pattern:

```text
intake
-> validate
-> create immutable run
-> generate
-> quality and evidence checks
-> human review
-> approved artifact
-> retention or deletion
```

Generation and quality advice never grant approval. Publication, submission,
or delivery to a third party is a separate, explicitly authorized action.

## Factory portfolio

| Factory | Portfolio status | Intended output | Important boundary |
| --- | --- | --- | --- |
| Strategy Factory | Reference implementation | Structured strategy, quality report, and approved Markdown artifact | Local, inactive, unpublished, and synthetic-only at the current checkpoint |
| Podcast Factory | Confirmed planned factory | Evidence-backed outline, script, editorial review pack, show notes, and later audio | No automatic publication; copyright, source provenance, disclosure, and voice/likeness permission are required |
| Job Application Factory | Confirmed planned factory | Evidence-mapped CV, cover letter, application answers, and interview pack | Candidate and employment data are sensitive; use synthetic profiles and postings until operational controls and real-data use are explicitly approved |
| Research and Briefing Factory | Candidate idea | Cited evidence matrix and decision briefing | Source quality, provenance, quotations, and uncertainty must remain visible |
| Content Repurposing Factory | Candidate idea | Human-reviewed variants of an approved source for selected channels | Preserve provenance and meaning; do not publish automatically |

The first three entries were confirmed as part of the original platform
direction. Research and Briefing and Content Repurposing are new proposals,
not recovered original commitments. They become planned work only after an
explicit portfolio decision.

## Shared platform versus factory-specific work

Likely shared platform capabilities:

- run identity, immutable inputs, state transitions, and idempotency;
- human and service authentication, authorization, and audit identity;
- provider routing, safe errors, retries, and long-running job status;
- quality reports, evidence checks, and explicit human review;
- artifact metadata, checksums, retrieval, retention, deletion, and recovery;
- inactive/unpublished workflow defaults and synthetic verification fixtures.

Factory-specific capabilities:

- intake schemas and validation rules;
- generation prompts, tools, and model/provider choices;
- quality rubrics and evidence requirements;
- artifact formats and renderers;
- delivery, submission, recording, or publication integrations.

Shared components should be extracted only after at least two working
factories demonstrate the same need. This avoids designing abstractions from a
single Strategy Factory example.

## Recommended expansion sequence

1. Preserve the Strategy Factory as the tested reference implementation.
2. Define a synthetic Podcast Factory contract and build a small inactive
   vertical slice with script and editorial review outputs only.
3. Compare the first two factories and extract only proven shared platform
   primitives.
4. Design the Job Application Factory using synthetic candidate profiles and
   job postings, with stricter privacy and human-submission boundaries.
5. Select a candidate factory only when it supports a concrete use case.

Operational hardening and factory expansion are separate decisions. Local,
synthetic factory prototypes may continue under the roadmap's Track B. Any
multi-user, externally accessible, real-data, publication, or submission use
must pass the applicable Stage 9 operationalization gates first.

## Current safety boundary

- Work only with workflows whose names begin with `CODEX TEST`.
- Keep workflows inactive and unpublished unless approval is explicit.
- Use synthetic inputs only.
- Do not use real CVs, applications, client briefs, recordings, or personal
  data.
- Do not clone voices or use a person's likeness without permission.
- Do not ingest or reproduce copyrighted material without authorization.
- Do not automatically publish content or submit applications.
- Keep human review and final authorization explicit for every factory.
