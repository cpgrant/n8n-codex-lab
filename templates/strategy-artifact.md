# {{ strategy_title }}

> Approved AI Strategy Factory v0.1 artifact

| Metadata | Value |
| --- | --- |
| Organization | {{ organization_name }} |
| Decision horizon | {{ decision_horizon }} |
| Run ID | `{{ run_id }}` |
| Generated at | {{ generated_at }} |
| Approved by | {{ reviewer }} |
| Approved at | {{ decided_at }} |
| Draft checksum | `{{ draft_checksum }}` |

## Executive summary

{{ executive_summary }}

## Current situation

{{ current_situation.summary }}

### Evidence

{{#each current_situation.evidence}}
- {{ this }}
{{/each}}

## Objectives

{{#each objectives}}
### {{ id }} — {{ statement }}

- Time horizon: {{ time_horizon }}
{{/each}}

## Strategic choices

{{#each strategic_choices}}
### {{ id }} — {{ choice }}

{{ rationale }}

- Trade-off: {{ trade_offs }}
{{/each}}

## Recommended initiatives

{{#each recommended_initiatives}}
### {{ id }} — {{ name }}

{{ description }}

- Owner role: {{ owner_role }}
- Timeframe: {{ timeframe }}
- Supports objectives: {{ supports_objectives_csv }}
{{/each}}

## Risks and assumptions

### Risks

{{#each risks_and_assumptions.risks}}
- {{ this }}
{{/each}}

### Assumptions

{{#each risks_and_assumptions.assumptions}}
- {{ this }}
{{/each}}

## Success measures

| ID | Measure | Target | Review frequency |
| --- | --- | --- | --- |
{{#each success_measures}}
| {{ id }} | {{ measure }} | {{ target }} | {{ review_frequency }} |
{{/each}}

## Next steps

{{#each next_steps}}
{{ order }}. {{ action }} — **{{ owner_role }}**
{{/each}}

## Review note

{{ review_comment }}

---

This artifact was generated from synthetic test data and explicitly approved by
the reviewer recorded above.
