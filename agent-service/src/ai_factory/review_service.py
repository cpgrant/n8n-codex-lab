"""Human review decisions and approved artifact creation."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from .artifacts import MarkdownArtifactStore, draft_checksum
from .errors import FactoryError
from .repository import RunNotFound, RunRecord, RunRepository
from .schemas import (
    QualityArtifactMetadata,
    QualityReport,
    ReviewRecord,
    ReviewRequest,
    StrategyBrief,
    StrategyResponse,
)
from .statuses import RunStatus


class ReviewService:
    def __init__(
        self, repository: RunRepository, artifact_store: MarkdownArtifactStore
    ) -> None:
        self.repository = repository
        self.artifact_store = artifact_store

    def review_run(self, run_id: UUID, request: ReviewRequest) -> RunRecord:
        try:
            run = self.repository.get(run_id)
        except RunNotFound as exc:
            raise FactoryError(
                404, "RUN_NOT_FOUND", "The requested strategy run does not exist."
            ) from exc
        if run.strategy is None:
            raise self._invalid_state(run_id, run.status)

        strategy = StrategyResponse.model_validate(run.strategy)
        checksum = draft_checksum(strategy)

        if run.status is RunStatus.AWAITING_REVIEW:
            review = ReviewRecord(
                decision=request.decision,
                reviewer=request.reviewer,
                comment=request.comment,
                decided_at=datetime.now(UTC),
                draft_checksum=checksum,
            )
            run = self.repository.record_review(run_id, review)
        elif run.status is RunStatus.APPROVED and self._matches_existing(
            run, request, checksum
        ):
            review = ReviewRecord.model_validate(run.review)
        else:
            raise self._invalid_state(run_id, run.status)

        if request.decision == "rejected":
            return run

        brief = StrategyBrief.model_validate(run.brief)
        quality_report = (
            QualityReport.model_validate(run.quality_report)
            if run.quality_report is not None
            else None
        )
        quality_artifact = (
            QualityArtifactMetadata.model_validate(run.quality_artifact)
            if run.quality_artifact is not None
            else None
        )
        try:
            artifact = self.artifact_store.create(
                run_id,
                brief,
                strategy,
                review,
                quality_report=quality_report,
                quality_artifact=quality_artifact,
            )
            return self.repository.record_artifact(run_id, artifact)
        except Exception as exc:
            raise FactoryError(
                500,
                "ARTIFACT_RENDER_FAILED",
                "The approved strategy artifact could not be rendered.",
                run_id=run_id,
                retryable=True,
            ) from exc

    @staticmethod
    def _matches_existing(
        run: RunRecord, request: ReviewRequest, checksum: str
    ) -> bool:
        if run.review is None:
            return False
        review = ReviewRecord.model_validate(run.review)
        return (
            review.decision == "approved"
            and request.decision == "approved"
            and review.reviewer == request.reviewer
            and review.comment == request.comment
            and review.draft_checksum == checksum
        )

    @staticmethod
    def _invalid_state(run_id: UUID, status: RunStatus) -> FactoryError:
        return FactoryError(
            409,
            "INVALID_STATE_TRANSITION",
            f"A run in status '{status.value}' cannot receive this review decision.",
            run_id=run_id,
        )
