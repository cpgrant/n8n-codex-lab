"""Synthetic-only local model evaluation for Stage 7.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path
import random
from time import perf_counter
from typing import Callable
from uuid import uuid4

from pydantic import ValidationError

from .providers import (
    OllamaQualityCritic,
    OllamaStrategyProvider,
    OllamaTransport,
)
from .quality import DeterministicQualityReviewer
from .quality_service import _merge_assessments
from .schemas import QualityAssessment, StrategyBrief, StrategyResponse

EVALUATION_VERSION = "7.1"


@dataclass
class TransportMetrics:
    wall_seconds: float | None = None
    total_seconds: float | None = None
    load_seconds: float | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "wall_seconds": self.wall_seconds,
            "total_seconds": self.total_seconds,
            "load_seconds": self.load_seconds,
            "prompt_tokens": self.prompt_tokens,
            "output_tokens": self.output_tokens,
        }


class ObservedTransport:
    """Capture Ollama timing metadata without storing prompts or raw responses."""

    def __init__(self, delegate: OllamaTransport) -> None:
        self.delegate = delegate
        self.metrics = TransportMetrics()

    def __call__(
        self, url: str, payload: dict[str, object], timeout: float
    ) -> dict[str, object]:
        started = perf_counter()
        try:
            envelope = self.delegate(url, payload, timeout)
        except Exception:
            self.metrics.wall_seconds = round(perf_counter() - started, 3)
            raise
        self.metrics = TransportMetrics(
            wall_seconds=round(perf_counter() - started, 3),
            total_seconds=_nanoseconds_to_seconds(envelope.get("total_duration")),
            load_seconds=_nanoseconds_to_seconds(envelope.get("load_duration")),
            prompt_tokens=_optional_int(envelope.get("prompt_eval_count")),
            output_tokens=_optional_int(envelope.get("eval_count")),
        )
        return envelope


def _nanoseconds_to_seconds(value: object) -> float | None:
    return round(value / 1_000_000_000, 3) if isinstance(value, int) else None


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


@dataclass
class EvaluationResult:
    model: str
    brief: str
    run_id: str
    schema_success: bool = False
    critique_success: bool = False
    generation: TransportMetrics = field(default_factory=TransportMetrics)
    critique: TransportMetrics = field(default_factory=TransportMetrics)
    overall_score: int | None = None
    recommendation: str | None = None
    checks: dict[str, int] | None = None
    unsupported_claims: int | None = None
    issues: int | None = None
    error_code: str | None = None
    strategy: dict[str, object] | None = None
    review_questions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "model": self.model,
            "brief": self.brief,
            "run_id": self.run_id,
            "schema_success": self.schema_success,
            "critique_success": self.critique_success,
            "generation": self.generation.as_dict(),
            "critique": self.critique.as_dict(),
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "checks": self.checks,
            "unsupported_claims": self.unsupported_claims,
            "issues": self.issues,
            "error_code": self.error_code,
            "strategy": self.strategy,
            "review_questions": self.review_questions,
        }


def evaluate_models(
    *,
    models: list[str],
    brief_paths: list[Path],
    base_url: str,
    timeout_seconds: float,
    transport: OllamaTransport | None = None,
    progress: Callable[[str], None] | None = None,
) -> dict[str, object]:
    """Run one generation and separate critique per model/brief pair."""
    if not models:
        raise ValueError("at least one model is required")
    if not brief_paths:
        raise ValueError("at least one synthetic brief is required")
    delegate = transport or OllamaStrategyProvider._post_json
    results: list[EvaluationResult] = []
    for brief_path in brief_paths:
        brief = StrategyBrief.model_validate_json(
            brief_path.read_text(encoding="utf-8")
        )
        for model in models:
            run_id = uuid4()
            result = EvaluationResult(
                model=model, brief=brief_path.name, run_id=str(run_id)
            )
            generation_transport = ObservedTransport(delegate)
            try:
                if progress:
                    progress(f"Generating {brief_path.name} with {model} ...")
                strategy_payload = OllamaStrategyProvider(
                    base_url=base_url,
                    model=model,
                    timeout_seconds=timeout_seconds,
                    transport=generation_transport,
                ).generate_strategy(brief, run_id)
                strategy = StrategyResponse.model_validate(strategy_payload)
                result.schema_success = True
                result.strategy = strategy.model_dump(mode="json")
                result.generation = generation_transport.metrics

                deterministic = DeterministicQualityReviewer().assess(
                    brief, strategy
                )
                critique_transport = ObservedTransport(delegate)
                if progress:
                    progress(f"Critiquing {brief_path.name} with {model} ...")
                critique_payload = OllamaQualityCritic(
                    base_url=base_url,
                    model=model,
                    timeout_seconds=timeout_seconds,
                    transport=critique_transport,
                ).review_strategy(brief, strategy, deterministic)
                critique = QualityAssessment.model_validate(critique_payload)
                merged = _merge_assessments(deterministic, critique)
                scores = merged.checks.model_dump()
                overall = round(sum(scores.values()) * 10 / 7)
                result.critique_success = True
                result.critique = critique_transport.metrics
                result.overall_score = overall
                result.recommendation = (
                    "ready_for_review"
                    if overall >= 75
                    and not any(issue.severity == "high" for issue in merged.issues)
                    else "review_with_caution"
                )
                result.checks = scores
                result.unsupported_claims = len(merged.unsupported_claims)
                result.issues = len(merged.issues)
                result.review_questions = merged.review_questions
            except (OSError, ValueError, ValidationError) as exc:
                result.error_code = type(exc).__name__
                result.generation = generation_transport.metrics
            except Exception as exc:
                # Reports contain only the exception type, never provider details.
                result.error_code = type(exc).__name__
                result.generation = generation_transport.metrics
            results.append(result)

    payload: dict[str, object] = {
        "evaluation_version": EVALUATION_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "synthetic_only": True,
        "base_url": base_url,
        "models": models,
        "briefs": [path.name for path in brief_paths],
        "results": [result.as_dict() for result in results],
    }
    payload["summary"] = summarize(payload)
    return payload


def summarize(payload: dict[str, object]) -> list[dict[str, object]]:
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("evaluation results must be a list")
    models = payload.get("models")
    if not isinstance(models, list):
        raise ValueError("evaluation models must be a list")
    summary: list[dict[str, object]] = []
    for model in models:
        rows = [row for row in results if row.get("model") == model]
        valid = [row for row in rows if row.get("schema_success")]
        critiqued = [row for row in rows if row.get("critique_success")]
        summary.append(
            {
                "model": model,
                "runs": len(rows),
                "schema_success_rate": _rate(len(valid), len(rows)),
                "critique_success_rate": _rate(len(critiqued), len(rows)),
                "average_generation_seconds": _average_metric(
                    rows, "generation", "wall_seconds"
                ),
                "average_critique_seconds": _average_metric(
                    rows, "critique", "wall_seconds"
                ),
                "average_quality_score": _average_values(
                    [row.get("overall_score") for row in critiqued]
                ),
                "average_evidence_grounding": _average_checks(
                    critiqued, "evidence_grounding"
                ),
                "average_constraint_adherence": _average_checks(
                    critiqued, "constraint_adherence"
                ),
                "unsupported_claims": sum(
                    int(row.get("unsupported_claims") or 0) for row in critiqued
                ),
                "issues": sum(int(row.get("issues") or 0) for row in critiqued),
            }
        )
    return summary


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator * 100 / denominator, 1) if denominator else 0.0


def _average_values(values: list[object]) -> float | None:
    numeric = [float(value) for value in values if isinstance(value, (int, float))]
    return round(sum(numeric) / len(numeric), 2) if numeric else None


def _average_metric(
    rows: list[dict[str, object]], section: str, name: str
) -> float | None:
    values = []
    for row in rows:
        metrics = row.get(section)
        if isinstance(metrics, dict):
            values.append(metrics.get(name))
    return _average_values(values)


def _average_checks(rows: list[dict[str, object]], name: str) -> float | None:
    values = []
    for row in rows:
        checks = row.get("checks")
        if isinstance(checks, dict):
            values.append(checks.get(name))
    return _average_values(values)


def write_evaluation_artifacts(
    payload: dict[str, object], output_dir: Path, seed: int = 7101
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.json"
    report_path = output_dir / "report.md"
    packet_path = output_dir / "blind-review.md"
    key_path = output_dir / "blind-review-key.json"
    preference_path = output_dir / "review-preferences.json"

    results_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_report(payload), encoding="utf-8")
    packet, key, template = render_blind_review(payload, seed=seed)
    packet_path.write_text(packet, encoding="utf-8")
    key_path.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    preference_path.write_text(
        json.dumps(template, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "results": results_path,
        "report": report_path,
        "review_packet": packet_path,
        "review_key": key_path,
        "preferences": preference_path,
    }


def render_report(
    payload: dict[str, object],
    preferences: dict[str, object] | None = None,
    review_key: dict[str, object] | None = None,
) -> str:
    lines = [
        "# Stage 7.1 local model evaluation",
        "",
        "> Synthetic-only benchmark; not an approval or production evaluation.",
        "",
        f"Generated: {payload.get('generated_at')}",
        "",
        "| Model | Schema | Critique | Generation | Critique | Quality | Evidence | Constraints | Unsupported | Issues |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    summary = payload.get("summary", [])
    for row in summary if isinstance(summary, list) else []:
        lines.append(
            "| {model} | {schema_success_rate}% | {critique_success_rate}% | "
            "{generation}s | {critique}s | {quality} | {evidence} | {constraints} | "
            "{unsupported} | {issues} |".format(
                model=row.get("model"),
                schema_success_rate=row.get("schema_success_rate"),
                critique_success_rate=row.get("critique_success_rate"),
                generation=row.get("average_generation_seconds"),
                critique=row.get("average_critique_seconds"),
                quality=row.get("average_quality_score"),
                evidence=row.get("average_evidence_grounding"),
                constraints=row.get("average_constraint_adherence"),
                unsupported=row.get("unsupported_claims"),
                issues=row.get("issues"),
            )
        )
    lines.extend(
        [
            "",
            "## Human reviewer preference",
            "",
        ]
    )
    if preferences:
        lines.append(_preference_summary(preferences, review_key))
    else:
        lines.append(
            "Not yet recorded. Complete `review-preferences.json` after reading "
            "`blind-review.md`; do not open the model key first."
        )
    lines.extend(["", "## Model decision", ""])
    lines.append(_model_decision(payload, preferences, review_key))
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- One run per model/brief is directional, not statistically conclusive.",
            "- Wall latency includes any local model-loading overhead.",
            "- Quality scores are advisory and cannot replace human preference.",
            "- Prompts and raw provider envelopes are not stored.",
            "",
        ]
    )
    return "\n".join(lines)


def render_blind_review(
    payload: dict[str, object], seed: int
) -> tuple[str, dict[str, object], dict[str, object]]:
    results = payload.get("results", [])
    briefs = payload.get("briefs", [])
    models = payload.get("models", [])
    rng = random.Random(seed)
    lines = [
        "# Stage 7.1 blind human review",
        "",
        "Review strategy usefulness without opening `blind-review-key.json`.",
        "Rank every brief's candidates from best to worst in "
        "`review-preferences.json`.",
        "",
    ]
    key: dict[str, object] = {"seed": seed, "briefs": {}}
    preference_rows = []
    for brief in briefs if isinstance(briefs, list) else []:
        shuffled = list(models) if isinstance(models, list) else []
        rng.shuffle(shuffled)
        aliases = {f"Candidate {chr(65 + index)}": model for index, model in enumerate(shuffled)}
        key["briefs"][brief] = aliases
        preference_rows.append(
            {"brief": brief, "ranking": list(aliases), "reviewer": ""}
        )
        lines.extend([f"## Brief: {brief}", ""])
        for alias, model in aliases.items():
            row = next(
                (
                    item
                    for item in results
                    if item.get("brief") == brief and item.get("model") == model
                ),
                None,
            )
            lines.extend([f"### {alias}", ""])
            if not row or not row.get("strategy"):
                lines.extend(["No schema-valid strategy was produced.", ""])
                continue
            strategy_text = json.dumps(
                row["strategy"], ensure_ascii=False, indent=2
            ).replace("```", "` ` `")
            lines.extend(["```json", strategy_text, "```", ""])
    template = {
        "instructions": "Rank candidate labels best to worst for each brief.",
        "preferences": preference_rows,
    }
    return "\n".join(lines), key, template


def apply_preferences(
    results_path: Path, preferences_path: Path, report_path: Path
) -> dict[str, object]:
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
    key_path = results_path.parent / "blind-review-key.json"
    review_key = json.loads(key_path.read_text(encoding="utf-8"))
    validate_preferences(payload, preferences)
    report_path.write_text(
        render_report(
            payload, preferences=preferences, review_key=review_key
        ),
        encoding="utf-8",
    )
    return preferences


def validate_preferences(
    payload: dict[str, object], preferences: dict[str, object]
) -> None:
    rows = preferences.get("preferences")
    briefs = payload.get("briefs")
    models = payload.get("models")
    if not isinstance(rows, list) or not isinstance(briefs, list):
        raise ValueError("preferences must contain one row per brief")
    if len(rows) != len(briefs):
        raise ValueError("preferences must contain one row per brief")
    for row in rows:
        if not isinstance(row, dict) or row.get("brief") not in briefs:
            raise ValueError("preference brief is invalid")
        ranking = row.get("ranking")
        reviewer = row.get("reviewer")
        expected_count = len(models) if isinstance(models, list) else 0
        if (
            not isinstance(ranking, list)
            or len(ranking) != expected_count
            or len(set(ranking)) != expected_count
            or set(ranking)
            != {f"Candidate {chr(65 + index)}" for index in range(expected_count)}
        ):
            raise ValueError("each ranking must contain every candidate once")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("reviewer is required")


def _preference_summary(
    preferences: dict[str, object], review_key: dict[str, object] | None
) -> str:
    rows = preferences.get("preferences", [])
    descriptions = []
    for row in rows if isinstance(rows, list) else []:
        ranking = row.get("ranking", [])
        mapped = _map_ranking(row.get("brief"), ranking, review_key)
        descriptions.append(
            f"{row.get('brief')}: {' > '.join(mapped)} ({row.get('reviewer')})"
        )
    return "Recorded: " + "; ".join(descriptions) + "."


def _map_ranking(
    brief: object, ranking: object, review_key: dict[str, object] | None
) -> list[str]:
    if not isinstance(ranking, list) or not review_key:
        return [str(item) for item in ranking] if isinstance(ranking, list) else []
    brief_keys = review_key.get("briefs")
    if not isinstance(brief_keys, dict):
        return [str(item) for item in ranking]
    aliases = brief_keys.get(brief)
    if not isinstance(aliases, dict):
        return [str(item) for item in ranking]
    return [str(aliases.get(item, item)) for item in ranking]


def _model_decision(
    payload: dict[str, object],
    preferences: dict[str, object] | None,
    review_key: dict[str, object] | None,
) -> str:
    if not preferences or not review_key:
        return (
            "Pending blind human preference. Retain the current `gemma4:31b` "
            "baseline until the reviewer ranking is recorded."
        )
    rows = preferences.get("preferences")
    if not isinstance(rows, list) or not rows:
        return "No valid human preference was recorded."
    votes: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        mapped = _map_ranking(row.get("brief"), row.get("ranking"), review_key)
        if mapped:
            votes[mapped[0]] = votes.get(mapped[0], 0) + 1
    if not votes:
        return "No valid first-choice vote was recorded."
    summary = payload.get("summary")
    summary_rows = summary if isinstance(summary, list) else []

    def rank(model: str) -> tuple[float, float, float]:
        row = next(
            (item for item in summary_rows if item.get("model") == model), {}
        )
        return (
            float(votes[model]),
            float(row.get("average_quality_score") or 0),
            -float(row.get("average_generation_seconds") or 10**9),
        )

    selected = max(votes, key=rank)
    return (
        f"Select `{selected}` as the internal Stage 7.1 default. Human "
        "first-choice votes are primary; advisory quality and generation latency "
        "break ties. This one-brief result remains directional."
    )
