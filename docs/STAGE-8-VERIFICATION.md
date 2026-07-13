# Stage 8 flexible-intake verification

## Outcome

The inactive `CODEX TEST — AI Strategy Factory v0.1` workflow supports three
synthetic-only intake paths:

```text
checked-in example --+
blank manual form ---+-> normalized StrategyBrief -> existing Stage 7 flow
JSON upload ---------+
```

No path changes generation, quality-report, human-review, or approved-artifact
semantics.

## Automated verification

Run:

```bash
agent-service/.venv/bin/pytest agent-service/tests -q
node scripts/verify-stage8-intake.js
```

The Python suite verifies workflow topology and safety flags, blank manual
fields, upload controls, strict API errors, and unchanged Stage 7 behavior. The
Node verifier executes the exported normalization and upload Code nodes against
the checked-in fixture, then checks unknown-field, oversize, and wrong-extension
failures.

## Upload boundary

- exactly one `.json` file;
- maximum 65,536 bytes;
- one JSON object, not an array;
- unknown top-level and organization fields rejected;
- explicit synthetic-data confirmation required;
- filename used only for extension checking, never as a path;
- binary input omitted from the normalized output;
- saved success, error, and manual workflow executions disabled.

## Create a customized synthetic brief

Do not modify the deterministic response fixture. Copy the input brief into the
Git-ignored `tmp/` directory and edit that working copy:

```bash
cd ~/Development/codex/n8n-codex-lab
cp examples/strategy-brief.synthetic.json tmp/company-brief.synthetic.json
code tmp/company-brief.synthetic.json
```

Preserve the JSON structure and use fictionalized or synthetic information
only. In n8n, choose **Upload structured JSON** and upload
`tmp/company-brief.synthetic.json`. Editing the repository example does not
change **Load synthetic example**, because that fast-path payload is embedded
in the workflow export.

Do not include real company, client, personal, confidential, or commercially
sensitive information. Even public company facts are outside the current test
boundary. Stage 9 must add authentication, ownership, privacy, retention,
deletion, and abuse controls before any real-data pilot.

The FastAPI `StrategyBrief` schema remains the final validation boundary and
returns the existing safe `400 VALIDATION_ERROR` contract.

## Installed workflow verification — 2026-07-13

The repository export was imported over the existing workflow ID
`CodexStrategyV01` and re-exported successfully. Verification confirmed:

- name starts with `CODEX TEST`;
- 16 nodes and all three Stage 8 paths present;
- zero credential-bearing nodes;
- `active: false`;
- `availableInMCP: false`;
- execution-data persistence settings remain disabled;
- production form URL returns HTTP 404.

All input and operational tests use fictional synthetic data. The workflow must
remain inactive and unpublished until explicit approval, and Stage 9 is required
before any real client intake.
