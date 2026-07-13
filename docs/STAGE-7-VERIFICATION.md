# Stage 7 quality-report verification

## Outcome

Stage 7 adds an immutable advisory quality report between strategy generation
and human review. The report is bound to the exact draft checksum and cannot
change run status, rewrite content, or make a review decision.

## Automated verification

Run:

```bash
cd agent-service
UV_CACHE_DIR=.uv-cache uv run pytest
```

The suite covers deterministic reports, pro-mode critic merging, invalid critic
output, SQLite persistence, checksum binding, API idempotency, and unchanged
human-review semantics.

## Synthetic smoke test

Start FastAPI in `basic` or `pro` mode, then run from the repository root:

```bash
EXPECTED_QUALITY_MODE=basic scripts/agent-smoke-stage7.sh
```

For `pro`, Ollama must be healthy and the configured critic model installed.
The script creates one ignored synthetic run and quality report, verifies the
seven check scores and checksum, confirms the report is retrievable, and leaves
the run in `awaiting_review` for optional manual review.

## n8n verification

Import the updated exported workflow only as
`CODEX TEST — AI Strategy Factory v0.1`. Keep it inactive and unpublished.

1. Click **Execute workflow** and submit the prefilled synthetic brief.
2. Confirm the second form page displays the advisory mode, score, seven
   checks, findings, and complete strategy JSON.
3. Confirm the page states that the report cannot approve, reject, or rewrite.
4. Submit a synthetic approval or rejection.
5. Confirm approval creates an artifact and rejection does not.

## Completion criteria

- The Python test suite passes.
- Basic-mode synthetic verification passes.
- Pro-mode verification passes against local Ollama.
- The report remains unchanged across API retrieval and restart.
- Its draft checksum matches the checksum recorded by later human review.
- The n8n workflow remains inactive, unpublished, credential-free, and
  unavailable through MCP.
- One manual synthetic n8n execution displays the report before review.

## Verification record

On 2026-07-13:

- 66 automated tests passed, including the workflow-export contract and a
  regression check for vague objective targets;
- basic mode passed for synthetic run
  `6a4fe10e-eac5-4d3a-9fef-5058c1f8a343`;
- pro mode passed with the `gemma4:31b` critic for synthetic run
  `deb6144d-bb8e-45bb-b244-5278b949223b`;
- the final updated port-8000 service passed pro mode again for synthetic run
  `09a6b685-4798-4919-928a-96c45c98a5af`;
- the pro report scored 96, retained one issue and three review questions, and
  was stored with a SHA-256 draft checksum;
- the updated local n8n workflow was re-exported and confirmed inactive,
  unpublished, credential-free, MCP-disabled, and connected through the new
  `Generate Quality Report` node;
- manual synthetic n8n run `286e341c-a332-4dbc-9927-61cea879287d` displayed
  the pro report, seven checks, advisory warning, findings, reviewer question,
  and complete immutable strategy before the decision;
- that run was explicitly approved and created
  `strategy-286e341c-a332-4dbc-9927-61cea879287d.md`;
- the manual output exposed a vague “higher specific target” objective that the
  initial 100/100 report did not flag; the deterministic evaluator and tests
  were strengthened before Stage 7 closure.
