"""Deterministic advisory checks for reviewable strategy drafts."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .schemas import (
    QualityAssessment,
    QualityIssue,
    QualityScorecard,
    StrategyBrief,
    StrategyResponse,
    SuccessMeasure,
)

CHECK_LABELS = {
    "brief_alignment": "Brief alignment",
    "evidence_grounding": "Evidence grounding",
    "constraint_adherence": "Constraint adherence",
    "objective_quality": "Objective quality",
    "measurement_quality": "Measurement quality",
    "initiative_feasibility": "Initiative feasibility",
    "internal_consistency": "Internal consistency",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
}

VAGUE_OBJECTIVE_PATTERNS = (
    r"\bhigher specific target\b",
    r"\blower specific target\b",
    r"\bto (?:a |an )?(?:higher|lower|better) target\b",
)

NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


@dataclass(frozen=True)
class ObjectiveMeasureGap:
    kind: str
    objective_id: str
    objective_statement: str
    measure_id: str | None
    measure_name: str | None
    measure_target: str | None
    objective_numbers: frozenset[str]
    explicit_target_numbers: frozenset[str]
    target_numbers: frozenset[str]


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) > 2 and token not in STOP_WORDS
    }


def _number_tokens(value: str) -> frozenset[str]:
    numeric = {
        token.lstrip("0") or "0"
        for token in re.findall(r"(?<![a-z])\d+(?:\.\d+)?", value.casefold())
    }
    words = {
        number
        for word, number in NUMBER_WORDS.items()
        if re.search(rf"\b{word}\b", value, flags=re.IGNORECASE)
    }
    return frozenset(numeric | words)


def _explicit_target_numbers(value: str) -> frozenset[str]:
    target_phrases = re.findall(
        r"\b(?:to|reach|achieve|target(?:\s+of)?|at\s+least|at\s+most)\s+"
        r"(?:[a-z-]+\s+){0,3}(\d+(?:\.\d+)?)",
        value.casefold(),
    )
    return frozenset(token.lstrip("0") or "0" for token in target_phrases)


def _joined_strategy(strategy: StrategyResponse) -> str:
    values = [
        strategy.executive_summary,
        strategy.current_situation.summary,
        *strategy.current_situation.evidence,
        *(item.statement for item in strategy.objectives),
        *(item.choice for item in strategy.strategic_choices),
        *(item.rationale for item in strategy.strategic_choices),
        *(item.trade_offs for item in strategy.strategic_choices),
        *(item.name for item in strategy.recommended_initiatives),
        *(item.description for item in strategy.recommended_initiatives),
        *(item.owner_role for item in strategy.recommended_initiatives),
        *(item.timeframe for item in strategy.recommended_initiatives),
        *strategy.risks_and_assumptions.risks,
        *strategy.risks_and_assumptions.assumptions,
        *(item.measure for item in strategy.success_measures),
        *(item.target for item in strategy.success_measures),
        *(item.action for item in strategy.next_steps),
        *(item.owner_role for item in strategy.next_steps),
    ]
    return " ".join(values)


def _coverage(items: list[str], strategy_text: str) -> tuple[int, list[str]]:
    if not items:
        return 10, []
    haystack = _tokens(strategy_text)
    covered = []
    missing = []
    for item in items:
        keywords = _tokens(item)
        overlap = keywords & haystack
        threshold = 1 if len(keywords) < 4 else 2
        (covered if len(overlap) >= threshold else missing).append(item)
    return round(10 * len(covered) / len(items)), missing


def _evidence_score(
    brief: StrategyBrief, strategy: StrategyResponse
) -> tuple[int, list[str]]:
    claims = strategy.current_situation.evidence
    if not claims:
        return (10 if not brief.available_evidence else 4), []
    source_tokens = [
        _tokens(item)
        for item in [brief.organization.context, *brief.available_evidence]
    ]
    unsupported = []
    for claim in claims:
        claim_tokens = _tokens(claim)
        best_overlap = max(
            (
                len(claim_tokens & source) / max(1, min(len(claim_tokens), len(source)))
                for source in source_tokens
            ),
            default=0,
        )
        if best_overlap < 0.25:
            unsupported.append(claim)
    return round(10 * (len(claims) - len(unsupported)) / len(claims)), unsupported


def _measurement_score(brief: StrategyBrief, strategy: StrategyResponse) -> int:
    numeric_evidence = any(re.search(r"\d", item) for item in brief.available_evidence)
    if not numeric_evidence:
        return 10
    numeric_targets = sum(
        bool(re.search(r"\d", item.target)) for item in strategy.success_measures
    )
    return round(10 * numeric_targets / len(strategy.success_measures))


def _initiative_score(brief: StrategyBrief, strategy: StrategyResponse) -> int:
    stakeholders = {item.casefold() for item in brief.stakeholders}
    if not strategy.recommended_initiatives:
        return 0
    points = 0
    for initiative in strategy.recommended_initiatives:
        owner_known = (
            not stakeholders or initiative.owner_role.casefold() in stakeholders
        )
        points += int(owner_known) + int(bool(initiative.timeframe.strip()))
    return round(10 * points / (2 * len(strategy.recommended_initiatives)))


def _best_measure_for_objective(
    strategy: StrategyResponse, statement: str
) -> SuccessMeasure | None:
    objective_tokens = _tokens(statement)
    ranked = sorted(
        (
            (
                len(objective_tokens & _tokens(measure.measure)),
                measure.id,
                measure,
            )
            for measure in strategy.success_measures
        ),
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    if not ranked or ranked[0][0] < 2:
        return None
    return ranked[0][2]


def _objective_measure_gaps(
    strategy: StrategyResponse,
) -> list[ObjectiveMeasureGap]:
    gaps: list[ObjectiveMeasureGap] = []
    for objective in strategy.objectives:
        measure = _best_measure_for_objective(strategy, objective.statement)
        objective_numbers = _number_tokens(objective.statement)
        explicit_target_numbers = _explicit_target_numbers(
            objective.statement
        )
        target_numbers = (
            _number_tokens(measure.target) if measure is not None else frozenset()
        )
        vague = any(
            re.search(pattern, objective.statement, flags=re.IGNORECASE)
            for pattern in VAGUE_OBJECTIVE_PATTERNS
        )
        kind: str | None = None
        if vague:
            kind = "vague"
        elif (
            measure is not None
            and target_numbers
            and target_numbers.isdisjoint(objective_numbers)
            and not explicit_target_numbers
        ):
            kind = "missing"
        elif (
            measure is not None
            and target_numbers
            and target_numbers.isdisjoint(objective_numbers)
            and explicit_target_numbers
        ):
            kind = "conflicting"
        if kind is not None:
            gaps.append(
                ObjectiveMeasureGap(
                    kind=kind,
                    objective_id=objective.id,
                    objective_statement=objective.statement,
                    measure_id=measure.id if measure is not None else None,
                    measure_name=measure.measure if measure is not None else None,
                    measure_target=measure.target if measure is not None else None,
                    objective_numbers=objective_numbers,
                    explicit_target_numbers=explicit_target_numbers,
                    target_numbers=target_numbers,
                )
            )
    return gaps


def _objective_score(
    strategy: StrategyResponse,
) -> tuple[int, int, list[ObjectiveMeasureGap]]:
    objective_tokens = [_tokens(item.statement) for item in strategy.objectives]
    distinct_objectives = len({frozenset(tokens) for tokens in objective_tokens})
    score = round(10 * distinct_objectives / len(strategy.objectives))
    gaps = _objective_measure_gaps(strategy)
    objective_penalty = sum(
        3 if gap.kind == "conflicting" else 4 for gap in gaps
    )
    consistency_penalty = 4 * sum(
        gap.kind == "conflicting" for gap in gaps
    )
    return (
        max(0, score - objective_penalty),
        max(0, 10 - consistency_penalty),
        gaps,
    )


def _gap_finding(gap: ObjectiveMeasureGap) -> tuple[QualityIssue, str, str]:
    section = f"objectives.{gap.objective_id}"
    if gap.kind == "conflicting":
        message = (
            f"{gap.objective_id} uses numeric value(s) "
            f"{', '.join(sorted(gap.objective_numbers))}, but "
            f"{gap.measure_id} defines target '{gap.measure_target}'."
        )
        suggestion = (
            f"Choose one approved target and use it consistently in "
            f"{gap.objective_id} and {gap.measure_id}. If the measure governs, "
            f"rewrite the objective to use the exact target "
            f"'{gap.measure_target}'; do not approve while the values conflict."
        )
        missing = (
            f"{gap.objective_id} and {gap.measure_id} use conflicting target "
            f"values: '{gap.objective_statement}' versus '{gap.measure_target}'."
        )
        question = (
            f"Which target should govern {gap.objective_id}: the objective's "
            f"value(s) or {gap.measure_id}'s target '{gap.measure_target}'?"
        )
        severity = "high"
    elif gap.measure_id is not None:
        description = "uses vague target language" if gap.kind == "vague" else (
            "does not state a numeric end-state target"
        )
        message = (
            f"{gap.objective_id} {description}, while {gap.measure_id} defines "
            f"target '{gap.measure_target}'."
        )
        suggestion = (
            f"Rewrite {gap.objective_id} to state the exact end-state target "
            f"'{gap.measure_target}' from {gap.measure_id}, retaining any "
            "supported baseline and keeping the timeframe separate."
        )
        missing = (
            f"{gap.objective_id} does not explicitly align to "
            f"{gap.measure_id}'s target '{gap.measure_target}'."
        )
        question = (
            f"Should {gap.objective_id} explicitly adopt {gap.measure_id}'s "
            f"target '{gap.measure_target}' before approval?"
        )
        severity = "medium"
    else:
        message = f"{gap.objective_id} uses vague target language."
        suggestion = (
            f"Replace the vague target in {gap.objective_id} with a measurable "
            "end-state or explicitly record why a numeric target is unsupported."
        )
        missing = (
            f"{gap.objective_id} has a vague target and no clearly linked "
            "success measure."
        )
        question = (
            f"What measurable end-state should replace the vague target in "
            f"{gap.objective_id}?"
        )
        severity = "medium"
    return (
        QualityIssue(
            severity=severity,
            section=section,
            message=message,
            suggestion=suggestion,
        ),
        missing,
        question,
    )


class DeterministicQualityReviewer:
    """Produce conservative, reproducible checks without contacting a model."""

    name = "deterministic"

    def assess(
        self, brief: StrategyBrief, strategy: StrategyResponse
    ) -> QualityAssessment:
        strategy_text = _joined_strategy(strategy)
        brief_score, missing_outcomes = _coverage(
            [brief.challenge, *brief.desired_outcomes], strategy_text
        )
        constraint_score, missing_constraints = _coverage(
            brief.constraints, strategy_text
        )
        evidence_score, unsupported = _evidence_score(brief, strategy)
        measurement_score = _measurement_score(brief, strategy)
        initiative_score = _initiative_score(brief, strategy)

        objective_score, consistency_score, objective_gaps = _objective_score(
            strategy
        )

        checks = QualityScorecard(
            brief_alignment=brief_score,
            evidence_grounding=evidence_score,
            constraint_adherence=constraint_score,
            objective_quality=objective_score,
            measurement_quality=measurement_score,
            initiative_feasibility=initiative_score,
            internal_consistency=consistency_score,
        )
        issues: list[QualityIssue] = []
        for name, score in checks.model_dump().items():
            if score >= 7:
                continue
            if name == "objective_quality" and objective_gaps:
                continue
            if name == "internal_consistency" and any(
                gap.kind == "conflicting" for gap in objective_gaps
            ):
                continue
            issues.append(
                QualityIssue(
                    severity="high" if score < 5 else "medium",
                    section=name,
                    message=f"{CHECK_LABELS[name]} scored {score} of 10.",
                    suggestion=(
                        "Confirm the draft explicitly addresses this area before "
                        "approval."
                    ),
                )
            )
        gap_findings = [_gap_finding(gap) for gap in objective_gaps]
        issues.extend(item[0] for item in gap_findings)

        strengths = [
            f"{CHECK_LABELS[name]} passed the deterministic check ({score}/10)."
            for name, score in checks.model_dump().items()
            if score >= 8
        ]
        missing_considerations = [
            *(f"Outcome or challenge coverage: {item}" for item in missing_outcomes),
            *(f"Constraint coverage: {item}" for item in missing_constraints),
            *(item[1] for item in gap_findings),
        ]
        review_questions = [
            f"What evidence supports this statement: {claim}" for claim in unsupported
        ]
        review_questions.extend(
            f"Where does the draft address: {item}" for item in missing_considerations
        )
        review_questions = [*(item[2] for item in gap_findings), *review_questions]
        return QualityAssessment(
            checks=checks,
            strengths=strengths[:10],
            issues=issues,
            unsupported_claims=unsupported[:20],
            missing_considerations=missing_considerations[:20],
            review_questions=review_questions[:20],
        )
