"""Durable, SQLite/PostgreSQL-portable strategy-run storage."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID, uuid4

from sqlalchemy import Engine, text

from .database import engine_for_target, sqlite_path_for_target
from .schemas import (
    ArtifactMetadata,
    QualityArtifactMetadata,
    QualityReport,
    ReviewRecord,
    StrategyBrief,
    StrategyResponse,
)
from .statuses import RunStatus, validate_transition

DatabaseTarget = Path | str | Engine


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RunRecord:
    run_id: UUID
    status: RunStatus
    brief: dict[str, object]
    strategy: dict[str, object] | None
    quality_report: dict[str, object] | None
    quality_artifact: dict[str, object] | None
    review: dict[str, object] | None
    artifact: dict[str, object] | None
    error_code: str | None
    error_message: str | None
    created_at: str
    updated_at: str


class RunNotFound(LookupError):
    """Raised when a run ID is unknown."""


class RunRepository:
    def __init__(self, database: DatabaseTarget) -> None:
        self.engine = engine_for_target(database)
        self.database_path = sqlite_path_for_target(self.engine)

    def _locking_query(self, query: str) -> str:
        if self.engine.dialect.name == "postgresql":
            return f"{query} FOR UPDATE"
        return query

    def create(self, brief: StrategyBrief, run_id: UUID | None = None) -> RunRecord:
        assigned_id = run_id or uuid4()
        timestamp = utc_now()
        brief_json = json.dumps(
            brief.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO strategy_runs (
                        run_id, status, brief_json, created_at, updated_at
                    ) VALUES (
                        :run_id, :status, :brief_json, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "run_id": str(assigned_id),
                    "status": RunStatus.RECEIVED.value,
                    "brief_json": brief_json,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                },
            )
        return self.get(assigned_id)

    def get(self, run_id: UUID) -> RunRecord:
        parameters = {"run_id": str(run_id)}
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT * FROM strategy_runs WHERE run_id = :run_id"),
                parameters,
            ).mappings().first()
            review_row = connection.execute(
                text("SELECT * FROM run_reviews WHERE run_id = :run_id"),
                parameters,
            ).mappings().first()
            artifact_row = connection.execute(
                text("SELECT * FROM run_artifacts WHERE run_id = :run_id"),
                parameters,
            ).mappings().first()
            quality_row = connection.execute(
                text("SELECT * FROM run_quality_reports WHERE run_id = :run_id"),
                parameters,
            ).mappings().first()
            quality_artifact_row = connection.execute(
                text("SELECT * FROM run_quality_artifacts WHERE run_id = :run_id"),
                parameters,
            ).mappings().first()
        if row is None:
            raise RunNotFound(str(run_id))
        return self._record_from_rows(
            row, review_row, artifact_row, quality_row, quality_artifact_row
        )

    @staticmethod
    def _record_from_rows(
        row: Mapping[str, Any],
        review_row: Mapping[str, Any] | None,
        artifact_row: Mapping[str, Any] | None,
        quality_row: Mapping[str, Any] | None,
        quality_artifact_row: Mapping[str, Any] | None,
    ) -> RunRecord:
        return RunRecord(
            run_id=UUID(row["run_id"]),
            status=RunStatus(row["status"]),
            brief=json.loads(row["brief_json"]),
            strategy=(
                json.loads(row["strategy_json"])
                if row["strategy_json"] is not None
                else None
            ),
            quality_report=(
                json.loads(quality_row["report_json"])
                if quality_row is not None
                else None
            ),
            quality_artifact=(
                {
                    "filename": quality_artifact_row["filename"],
                    "media_type": quality_artifact_row["media_type"],
                    "checksum": quality_artifact_row["checksum"],
                    "created_at": quality_artifact_row["created_at"],
                }
                if quality_artifact_row is not None
                else None
            ),
            review=(
                {
                    "decision": review_row["decision"],
                    "reviewer": review_row["reviewer"],
                    "comment": review_row["comment"],
                    "decided_at": review_row["decided_at"],
                    "draft_checksum": review_row["draft_checksum"],
                }
                if review_row is not None
                else None
            ),
            artifact=(
                {
                    "filename": artifact_row["filename"],
                    "media_type": artifact_row["media_type"],
                    "checksum": artifact_row["checksum"],
                    "created_at": artifact_row["created_at"],
                }
                if artifact_row is not None
                else None
            ),
            error_code=row["error_code"],
            error_message=row["error_message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def record_quality_report(
        self, run_id: UUID, report: QualityReport
    ) -> RunRecord:
        report_json = json.dumps(
            report.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        parameters = {"run_id": str(run_id)}
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    self._locking_query(
                        "SELECT strategy_json FROM strategy_runs "
                        "WHERE run_id = :run_id"
                    )
                ),
                parameters,
            ).mappings().first()
            if row is None:
                raise RunNotFound(str(run_id))
            if row["strategy_json"] is None:
                raise RuntimeError("run has no reviewable strategy")
            existing = connection.execute(
                text(
                    "SELECT report_json FROM run_quality_reports "
                    "WHERE run_id = :run_id"
                ),
                parameters,
            ).first()
            if existing is None:
                connection.execute(
                    text(
                        """
                        INSERT INTO run_quality_reports (
                            run_id, report_json, draft_checksum, created_at
                        ) VALUES (
                            :run_id, :report_json, :draft_checksum, :created_at
                        )
                        """
                    ),
                    {
                        **parameters,
                        "report_json": report_json,
                        "draft_checksum": report.draft_checksum,
                        "created_at": utc_now(),
                    },
                )
        return self.get(run_id)

    def record_quality_artifact(
        self, run_id: UUID, artifact: QualityArtifactMetadata
    ) -> RunRecord:
        parameters = {"run_id": str(run_id)}
        with self.engine.begin() as connection:
            report = connection.execute(
                text(
                    self._locking_query(
                        "SELECT run_id FROM run_quality_reports "
                        "WHERE run_id = :run_id"
                    )
                ),
                parameters,
            ).first()
            if report is None:
                raise RuntimeError("run has no quality report")
            existing = connection.execute(
                text(
                    "SELECT run_id FROM run_quality_artifacts "
                    "WHERE run_id = :run_id"
                ),
                parameters,
            ).first()
            if existing is None:
                connection.execute(
                    text(
                        """
                        INSERT INTO run_quality_artifacts (
                            run_id, filename, media_type, checksum, created_at
                        ) VALUES (
                            :run_id, :filename, :media_type, :checksum, :created_at
                        )
                        """
                    ),
                    {
                        **parameters,
                        "filename": artifact.filename,
                        "media_type": artifact.media_type,
                        "checksum": artifact.checksum,
                        "created_at": artifact.created_at.isoformat().replace(
                            "+00:00", "Z"
                        ),
                    },
                )
        return self.get(run_id)

    def transition(self, run_id: UUID, target: RunStatus) -> RunRecord:
        current = self.get(run_id)
        validate_transition(current.status, target)
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    UPDATE strategy_runs
                    SET status = :target, updated_at = :updated_at
                    WHERE run_id = :run_id AND status = :current
                    """
                ),
                {
                    "target": target.value,
                    "updated_at": utc_now(),
                    "run_id": str(run_id),
                    "current": current.status.value,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("run status changed concurrently")
        return self.get(run_id)

    def record_review(self, run_id: UUID, review: ReviewRecord) -> RunRecord:
        target = (
            RunStatus.APPROVED
            if review.decision == "approved"
            else RunStatus.REJECTED
        )
        parameters = {"run_id": str(run_id)}
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    self._locking_query(
                        "SELECT status FROM strategy_runs WHERE run_id = :run_id"
                    )
                ),
                parameters,
            ).mappings().first()
            if row is None:
                raise RunNotFound(str(run_id))
            current = RunStatus(row["status"])
            validate_transition(current, target)
            connection.execute(
                text(
                    """
                    INSERT INTO run_reviews (
                        run_id, decision, reviewer, comment, decided_at,
                        draft_checksum
                    ) VALUES (
                        :run_id, :decision, :reviewer, :comment, :decided_at,
                        :draft_checksum
                    )
                    """
                ),
                {
                    **parameters,
                    "decision": review.decision,
                    "reviewer": review.reviewer,
                    "comment": review.comment,
                    "decided_at": review.decided_at.isoformat().replace(
                        "+00:00", "Z"
                    ),
                    "draft_checksum": review.draft_checksum,
                },
            )
            result = connection.execute(
                text(
                    """
                    UPDATE strategy_runs SET status = :target,
                        updated_at = :updated_at
                    WHERE run_id = :run_id AND status = :current
                    """
                ),
                {
                    **parameters,
                    "target": target.value,
                    "updated_at": utc_now(),
                    "current": current.value,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("run status changed concurrently")
        return self.get(run_id)

    def record_artifact(
        self, run_id: UUID, artifact: ArtifactMetadata
    ) -> RunRecord:
        parameters = {"run_id": str(run_id)}
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    self._locking_query(
                        "SELECT status FROM strategy_runs WHERE run_id = :run_id"
                    )
                ),
                parameters,
            ).mappings().first()
            if row is None:
                raise RunNotFound(str(run_id))
            current = RunStatus(row["status"])
            validate_transition(current, RunStatus.ARTIFACT_CREATED)
            connection.execute(
                text(
                    """
                    INSERT INTO run_artifacts (
                        run_id, filename, media_type, checksum, created_at
                    ) VALUES (
                        :run_id, :filename, :media_type, :checksum, :created_at
                    )
                    """
                ),
                {
                    **parameters,
                    "filename": artifact.filename,
                    "media_type": artifact.media_type,
                    "checksum": artifact.checksum,
                    "created_at": artifact.created_at.isoformat().replace(
                        "+00:00", "Z"
                    ),
                },
            )
            result = connection.execute(
                text(
                    """
                    UPDATE strategy_runs SET status = :target,
                        updated_at = :updated_at
                    WHERE run_id = :run_id AND status = :current
                    """
                ),
                {
                    **parameters,
                    "target": RunStatus.ARTIFACT_CREATED.value,
                    "updated_at": utc_now(),
                    "current": RunStatus.APPROVED.value,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("run status changed concurrently")
        return self.get(run_id)

    def complete_generation(
        self, run_id: UUID, strategy: StrategyResponse
    ) -> RunRecord:
        strategy_json = json.dumps(
            strategy.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    UPDATE strategy_runs
                    SET status = :target, strategy_json = :strategy_json,
                        error_code = NULL, error_message = NULL,
                        updated_at = :updated_at
                    WHERE run_id = :run_id AND status = :current
                    """
                ),
                {
                    "target": RunStatus.AWAITING_REVIEW.value,
                    "strategy_json": strategy_json,
                    "updated_at": utc_now(),
                    "run_id": str(run_id),
                    "current": RunStatus.GENERATING.value,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("run is not in generating status")
        return self.get(run_id)

    def fail_generation(
        self, run_id: UUID, error_code: str, error_message: str
    ) -> RunRecord:
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    UPDATE strategy_runs
                    SET status = :target, error_code = :error_code,
                        error_message = :error_message, updated_at = :updated_at
                    WHERE run_id = :run_id AND status = :current
                    """
                ),
                {
                    "target": RunStatus.FAILED.value,
                    "error_code": error_code,
                    "error_message": error_message,
                    "updated_at": utc_now(),
                    "run_id": str(run_id),
                    "current": RunStatus.GENERATING.value,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("run is not in generating status")
        return self.get(run_id)
