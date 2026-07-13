"""Create immutable advisory quality reports for stored strategy drafts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import ValidationError

from .artifacts import draft_checksum
from .errors import FactoryError
from .providers import ProviderOutputError
from .quality import DeterministicQualityReviewer
from .repository import RunNotFound, RunRecord, RunRepository
from .schemas import (
    QualityAssessment,
    QualityIssue,
    QualityReport,
    QualityScorecard,
    StrategyBrief,
    StrategyResponse,
)
from .statuses import RunStatus


class QualityCritic(Protocol):
    name: str
    model: str

    def review_strategy(
        self,
        brief: StrategyBrief,
        strategy: StrategyResponse,
        deterministic: QualityAssessment,
    ) -> dict[str, object]: ...


def _unique_strings(*groups: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in (item for group in groups for item in group):
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
        if len(result) == limit:
            break
    return result


def _unique_issues(*groups: list[QualityIssue]) -> list[QualityIssue]:
    result: list[QualityIssue] = []
    seen: set[tuple[str, str, str]] = set()
    for issue in (item for group in groups for item in group):
        key = (issue.severity, issue.section.casefold(), issue.message.casefold())
        if key not in seen:
            seen.add(key)
            result.append(issue)
        if len(result) == 20:
            break
    return result


def _merge_assessments(
    deterministic: QualityAssessment, critique: QualityAssessment
) -> QualityAssessment:
    deterministic_scores = deterministic.checks.model_dump()
    critique_scores = critique.checks.model_dump()
    conservative_scores = {
        name: min(score, critique_scores[name])
        for name, score in deterministic_scores.items()
    }
    return QualityAssessment(
        checks=QualityScorecard(**conservative_scores),
        strengths=_unique_strings(
            deterministic.strengths, critique.strengths, limit=10
        ),
        issues=_unique_issues(deterministic.issues, critique.issues),
        unsupported_claims=_unique_strings(
            deterministic.unsupported_claims,
            critique.unsupported_claims,
            limit=20,
        ),
        missing_considerations=_unique_strings(
            deterministic.missing_considerations,
            critique.missing_considerations,
            limit=20,
        ),
        review_questions=_unique_strings(
            deterministic.review_questions, critique.review_questions, limit=20
        ),
    )


class QualityReportService:
    def __init__(
        self,
        repository: RunRepository,
        mode: str = "basic",
        critic: QualityCritic | None = None,
    ) -> None:
        self.repository = repository
        self.mode = mode
        self.critic = critic
        self.deterministic = DeterministicQualityReviewer()

    def create_report(self, run_id: UUID) -> RunRecord:
        try:
            run = self.repository.get(run_id)
        except RunNotFound as exc:
            raise FactoryError(
                404, "RUN_NOT_FOUND", "The requested strategy run does not exist."
            ) from exc
        if run.quality_report is not None:
            return run
        if run.status is not RunStatus.AWAITING_REVIEW or run.strategy is None:
            raise FactoryError(
                409,
                "INVALID_STATE_TRANSITION",
                f"A run in status '{run.status.value}' cannot create a quality report.",
                run_id=run_id,
            )

        brief = StrategyBrief.model_validate(run.brief)
        strategy = StrategyResponse.model_validate(run.strategy)
        assessment = self.deterministic.assess(brief, strategy)
        critic_provider = "deterministic"
        critic_model = None

        if self.mode == "pro":
            if self.critic is None:
                raise FactoryError(
                    503,
                    "SERVICE_UNAVAILABLE",
                    "The configured quality critic is unavailable.",
                    run_id=run_id,
                    retryable=True,
                )
            try:
                raw_critique = self.critic.review_strategy(
                    brief, strategy, assessment
                )
                critique = QualityAssessment.model_validate(raw_critique)
            except ProviderOutputError as exc:
                raise FactoryError(
                    422,
                    "QUALITY_REVIEW_OUTPUT_INVALID",
                    "The quality critic output did not satisfy the report contract.",
                    run_id=run_id,
                ) from exc
            except ValidationError as exc:
                raise FactoryError(
                    422,
                    "QUALITY_REVIEW_OUTPUT_INVALID",
                    "The quality critic output did not satisfy the report contract.",
                    details=[
                        {
                            "field": ".".join(str(part) for part in error["loc"]),
                            "reason": error["msg"],
                        }
                        for error in exc.errors()
                    ],
                    run_id=run_id,
                ) from exc
            except Exception as exc:
                raise FactoryError(
                    502,
                    "QUALITY_REVIEW_PROVIDER_ERROR",
                    "The quality critic failed.",
                    run_id=run_id,
                    retryable=True,
                ) from exc
            assessment = _merge_assessments(assessment, critique)
            critic_provider = self.critic.name
            critic_model = self.critic.model

        scores = assessment.checks.model_dump().values()
        overall_score = round(sum(scores) * 10 / 7)
        recommendation = (
            "ready_for_review"
            if overall_score >= 75
            and not any(issue.severity == "high" for issue in assessment.issues)
            else "review_with_caution"
        )
        report = QualityReport(
            **assessment.model_dump(),
            run_id=run_id,
            mode=self.mode,
            overall_score=overall_score,
            recommendation=recommendation,
            draft_checksum=draft_checksum(strategy),
            generated_at=datetime.now(UTC),
            critic_provider=critic_provider,
            critic_model=critic_model,
        )
        return self.repository.record_quality_report(run_id, report)
