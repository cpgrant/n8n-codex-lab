# Stage 9.5-lite verification

Status: **Complete**

Date: `2026-07-16`

## Scope

Stage 9.5-lite improves the local synthetic form experience without introducing
a job queue, background worker, polling API, WebSocket progress, durable
cancellation, workflow activation, or publication.

The workflow now separates the two slow local-model calls:

```text
validated synthetic brief
-> generation readiness and before-run recovery guidance
-> Ollama strategy generation
-> stored run ID and after-run recovery guidance
-> Ollama advisory quality critique
-> human review
-> approved or rejected completion with local artifact paths
```

## Automated verification

Run from the repository root:

```bash
node scripts/verify-stage8-intake.js
node scripts/verify-stage9-5-lite.js
cd agent-service
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Verified on 2026-07-16:

- Stage 8 intake verification passed;
- Stage 9.5-lite workflow-contract verification passed;
- 83 automated tests passed;
- the recovery helper returned `artifact_created` and the correct advisory and
  approved paths for synthetic run
  `fbf78215-a80c-41c0-8d6d-2eb8793480e6`;
- n8n imported and re-exported the updated 20-node workflow;
- the installed and tracked workflow matched semantically;
- the installed workflow remained inactive, unpublished, credential-free, and
  unavailable through MCP.

## Manual completion check

Use only the built-in synthetic example.

1. In n8n, open `CODEX TEST — AI Strategy Factory v0.1` and click **Execute
   workflow**. Do not activate or publish it.
2. Confirm the initial form warns that both local-model calls can take several
   minutes.
3. Choose **Load synthetic example** and confirm the generation-readiness page
   explains that no run ID exists yet and how to restart safely.
4. Select **Generate strategy** and wait for the stored-draft page.
5. Copy the displayed run ID and confirm the recovery command includes that
   exact ID.
6. Run `scripts/strategy-run-status.sh <run-id>` and confirm the stored draft is
   `awaiting_review` with no quality report yet.
7. Select **Generate quality report** and wait for the human-review page.
8. Confirm the review page shows the same run ID, the advisory Markdown path,
   recovery command, quality findings, and explicit human decision control.
9. Approve or reject the synthetic run.
10. Confirm the completion page shows the same run ID and the correct local
    artifact result. Approval must show both report and strategy paths;
    rejection must show the retained report and state that no approved strategy
    was created.
11. Run the status helper again and confirm the terminal state and paths match
    the completion page.

Completed on 2026-07-16 with synthetic run
`5062f0cf-eb42-4f4b-9f0f-38459e06e399`:

- the initial form set expectations for both slow local-model calls;
- the generation-readiness page explained safe recovery before a run ID;
- the stored-draft page displayed the run ID before quality review;
- the recovery helper returned `awaiting_review`, no quality report, and no
  approved strategy before the critic call;
- the human-review page displayed the same run ID, advisory Markdown path,
  recovery command, pro quality findings, strategy draft, and separate human
  decision control;
- the synthetic strategy was explicitly approved;
- the recovery helper then returned `artifact_created` and the expected quality
  and approved-strategy paths.

The first completion rendering exposed one narrow-card presentation issue: the
long recovery command extended beyond the white card. The workflow was updated
with explicit wrap opportunities and word-breaking styles for recovery commands
and artifact paths, the automated verifier was strengthened to require those
markers, and n8n accepted and re-exported the correction while remaining
inactive and unavailable through MCP.

A final no-model UI hardening pass converts the structured JSON block from
non-wrapping `pre` rendering to ordinary wrapping HTML with explicit line
breaks. This was necessary because n8n's form CSS overrode the attempted
`pre-wrap` styling during the visual regression run. The stored JSON, API
response, and Markdown artifacts remain unchanged.

## Completion gate

Stage 9.5-lite is complete for the local synthetic Track B workflow. Full
asynchronous execution, cancellation, and resumable browser polling remain
deferred to full Stage 9.5.
