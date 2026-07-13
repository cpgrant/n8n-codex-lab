# Stage 7.1 local-model evaluation

## Safety boundary

The evaluation sends only checked-in synthetic briefs to the repository-managed
local Ollama service. It does not call n8n, change workflow activation, make a
human-review decision, or use confidential data. Prompts and raw Ollama
envelopes are not written to artifacts.

## Run the benchmark

From the repository root:

```bash
agent-service/.venv/bin/python scripts/evaluate-stage7-1.py \
  --models gemma4:12b gemma4:26b gemma4:31b \
  --briefs examples/strategy-brief.synthetic.json \
  --output-dir artifacts/evaluations/stage-7.1
```

The ignored output directory contains:

- `results.json`: normalized results and schema-safe strategies;
- `report.md`: aggregate metrics and the model decision;
- `blind-review.md`: candidates without model names;
- `blind-review-key.json`: the separate candidate-to-model key;
- `review-preferences.json`: the human ranking template.

Review `blind-review.md` before opening the key. Rank every candidate exactly
once, add the reviewer name, then finalize without rerunning Ollama:

```bash
agent-service/.venv/bin/python scripts/evaluate-stage7-1.py \
  --output-dir artifacts/evaluations/stage-7.1 \
  --apply-preferences
```

## Automated verification

```bash
agent-service/.venv/bin/pytest agent-service/tests -q
```

The suite verifies metric capture, schema and critique validation, aggregate
scoring, blinded output, complete candidate rankings, reviewer attribution, and
preference application.

## Live record — 2026-07-13

One generation and one separate critique were run per candidate against
`strategy-brief.synthetic.json`:

| Model | Schema | Critique | Generation | Critique | Quality | Evidence | Constraints | Unsupported | Issues |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gemma4:12b` | 100% | 100% | 78.44s | 33.02s | 100 | 10 | 10 | 0 | 0 |
| `gemma4:26b` | 100% | 100% | 46.99s | 11.97s | 100 | 10 | 10 | 0 | 0 |
| `gemma4:31b` | 100% | 100% | 156.84s | 79.79s | 94 | 10 | 10 | 0 | 2 |

Wall latency includes model-loading overhead. The result is directional rather
than statistically conclusive because the set currently contains one synthetic
brief and one trial per model.

Human preference: **pending blinded review**.
