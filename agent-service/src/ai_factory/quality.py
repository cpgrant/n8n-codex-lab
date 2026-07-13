"""Deterministic advisory checks for reviewable strategy drafts."""

from __future__ import annotations

import re

from .schemas import (
    QualityAssessment,
    QualityIssue,
    QualityScorecard,
    StrategyBrief,
    StrategyResponse,
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


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) > 2 and token not in STOP_WORDS
    }


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


def _objective_score(strategy: StrategyResponse) -> tuple[int, list[str]]:
    objective_tokens = [_tokens(item.statement) for item in strategy.objectives]
    distinct_objectives = len({frozenset(tokens) for tokens in objective_tokens})
    score = round(10 * distinct_objectives / len(strategy.objectives))
    vague = [
        item.statement
        for item in strategy.objectives
        if any(
            re.search(pattern, item.statement, flags=re.IGNORECASE)
            for pattern in VAGUE_OBJECTIVE_PATTERNS
        )
    ]
    return max(0, score - 4 * len(vague)), vague


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

        objective_score, vague_objectives = _objective_score(strategy)

        checks = QualityScorecard(
            brief_alignment=brief_score,
            evidence_grounding=evidence_score,
            constraint_adherence=constraint_score,
            objective_quality=objective_score,
            measurement_quality=measurement_score,
            initiative_feasibility=initiative_score,
            internal_consistency=10,
        )
        issues: list[QualityIssue] = []
        for name, score in checks.model_dump().items():
            if score >= 7:
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

        strengths = [
            f"{CHECK_LABELS[name]} passed the deterministic check ({score}/10)."
            for name, score in checks.model_dump().items()
            if score >= 8
        ]
        missing_considerations = [
            *(f"Outcome or challenge coverage: {item}" for item in missing_outcomes),
            *(f"Constraint coverage: {item}" for item in missing_constraints),
            *(f"Objective target is vague: {item}" for item in vague_objectives),
        ]
        review_questions = [
            f"What evidence supports this statement: {claim}" for claim in unsupported
        ]
        review_questions.extend(
            f"Where does the draft address: {item}" for item in missing_considerations
        )
        return QualityAssessment(
            checks=checks,
            strengths=strengths[:10],
            issues=issues,
            unsupported_claims=unsupported[:20],
            missing_considerations=missing_considerations[:20],
            review_questions=review_questions[:20],
        )
