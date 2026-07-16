# Track B-Q1 verification

Date: 2026-07-16

Status: **Complete for the local, inactive, unpublished, synthetic-only
Strategy Factory workflow.**

## Scope

Track B-Q1 improves strategy quality and the approved final artifact without
introducing real data, workflow publication, automatic approval, or a new
operational boundary.

The checkpoint adds:

- exact objective-to-success-measure target alignment instructions for
  generation;
- deterministic detection of vague, missing, and conflicting target language;
- separate handling for baseline and scope numbers;
- actionable objective-specific findings and review questions;
- equivalent alignment guidance for the advisory Ollama critic;
- a decision summary and advisory quality context in approved Markdown.

The quality report remains advisory. It cannot approve, reject, or rewrite the
stored strategy. Artifact creation still requires an authenticated, explicit
review decision.

## Regression cases

The checked-in synthetic fixture
`examples/quality-objective-measure-cases.synthetic.json` covers:

| Case | Expected result |
| --- | --- |
| Exact objective and measure target | No alignment finding |
| Vague objective with an exact measure target | Medium actionable finding |
| Objective missing the measure target | Medium actionable finding |
| Scope number present but target missing | Medium missing-target finding |
| Different explicit end-state targets | High conflict finding |

## Automated verification

The following checks passed:

```text
87 FastAPI/service tests
Stage 8 intake verification
Stage 9.5-lite workflow verification
git diff --check
```

The focused tests assert that findings include the exact measure target in the
message, suggested correction, and human review question. API tests also verify
that an approved artifact contains its decision summary and matching quality
report metadata.

The existing Starlette `httpx` deprecation warning remains unchanged and does
not affect the result.

## Live synthetic verification

An updated FastAPI process was started temporarily on isolated localhost port
`16333`, leaving the normal n8n-facing service untouched. The standard Stage
7/7.0.1 live smoke flow ran with local Ollama generation and the pro Ollama
quality critic.

Final synthetic run:

```text
ef812274-2027-49b1-94a8-6d0c0885f364
```

Observed result:

- strategy generation completed;
- pro advisory quality generation completed;
- quality-report idempotency and durable retrieval passed;
- the 35%-to-60% objective repeated the linked 60% measure target;
- the five-garden scope number was not treated as a conflicting target;
- the missing 100% adoption target produced a medium, objective-specific
  correction;
- overall score: `94/100`;
- recommendation: `ready_for_review`;
- internal consistency: `10/10`.

A review by the explicit synthetic actor `codex-synthetic-verifier` was used
only to exercise artifact rendering. It produced:

```text
artifacts/strategy-ef812274-2027-49b1-94a8-6d0c0885f364.md
artifacts/quality-reports/quality-report-ef812274-2027-49b1-94a8-6d0c0885f364.md
```

The approved Markdown includes:

- a decision-summary table for objectives and strategic choices;
- the strategy provider;
- advisory score and recommendation;
- quality mode and critic identity;
- the matching quality-report artifact path;
- the existing detailed strategy, measures, next steps, and review record.

## Safety and operational state

- Only checked-in synthetic data was used.
- No credentials were changed or printed.
- No workflow was activated, published, deleted, or made available through
  MCP.
- The isolated verification service was stopped after the test.
- The standard local services were not restarted or modified.

## Next Track B checkpoint

Proceed to **Stage 9.3-lite**:

- define local synthetic retention periods;
- document and verify safe n8n execution cleanup;
- verify SQLite and Markdown artifact backup creation and integrity;
- document a basic restore check without claiming full pilot-grade recovery or
  deletion controls.
