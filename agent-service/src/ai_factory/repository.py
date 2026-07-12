"""Durable strategy-run storage."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from .database import connect
from .schemas import ArtifactMetadata, ReviewRecord, StrategyBrief, StrategyResponse
from .statuses import RunStatus, validate_transition


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RunRecord:
    run_id: UUID
    status: RunStatus
    brief: dict[str, object]
    strategy: dict[str, object] | None
    review: dict[str, object] | None
    artifact: dict[str, object] | None
    error_code: str | None
    error_message: str | None
    created_at: str
    updated_at: str


class RunNotFound(LookupError):
    """Raised when a run ID is unknown."""


class RunRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def create(self, brief: StrategyBrief, run_id: UUID | None = None) -> RunRecord:
        assigned_id = run_id or uuid4()
        timestamp = utc_now()
        brief_json = json.dumps(
            brief.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        with connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO strategy_runs (
                    run_id, status, brief_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(assigned_id),
                    RunStatus.RECEIVED.value,
                    brief_json,
                    timestamp,
                    timestamp,
                ),
            )
        return self.get(assigned_id)

    def get(self, run_id: UUID) -> RunRecord:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM strategy_runs WHERE run_id = ?", (str(run_id),)
            ).fetchone()
            review_row = connection.execute(
                "SELECT * FROM run_reviews WHERE run_id = ?", (str(run_id),)
            ).fetchone()
            artifact_row = connection.execute(
                "SELECT * FROM run_artifacts WHERE run_id = ?", (str(run_id),)
            ).fetchone()
        if row is None:
            raise RunNotFound(str(run_id))
        return RunRecord(
            run_id=UUID(row["run_id"]),
            status=RunStatus(row["status"]),
            brief=json.loads(row["brief_json"]),
            strategy=(
                json.loads(row["strategy_json"])
                if row["strategy_json"] is not None
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

    def transition(self, run_id: UUID, target: RunStatus) -> RunRecord:
        current = self.get(run_id)
        validate_transition(current.status, target)
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            result = connection.execute(
                """
                UPDATE strategy_runs
                SET status = ?, updated_at = ?
                WHERE run_id = ? AND status = ?
                """,
                (target.value, timestamp, str(run_id), current.status.value),
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
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT status FROM strategy_runs WHERE run_id = ?", (str(run_id),)
            ).fetchone()
            if row is None:
                raise RunNotFound(str(run_id))
            current = RunStatus(row["status"])
            validate_transition(current, target)
            connection.execute(
                """
                INSERT INTO run_reviews (
                    run_id, decision, reviewer, comment, decided_at, draft_checksum
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(run_id),
                    review.decision,
                    review.reviewer,
                    review.comment,
                    review.decided_at.isoformat().replace("+00:00", "Z"),
                    review.draft_checksum,
                ),
            )
            result = connection.execute(
                """
                UPDATE strategy_runs SET status = ?, updated_at = ?
                WHERE run_id = ? AND status = ?
                """,
                (target.value, timestamp, str(run_id), current.value),
            )
            if result.rowcount != 1:
                raise RuntimeError("run status changed concurrently")
        return self.get(run_id)

    def record_artifact(
        self, run_id: UUID, artifact: ArtifactMetadata
    ) -> RunRecord:
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT status FROM strategy_runs WHERE run_id = ?", (str(run_id),)
            ).fetchone()
            if row is None:
                raise RunNotFound(str(run_id))
            current = RunStatus(row["status"])
            validate_transition(current, RunStatus.ARTIFACT_CREATED)
            connection.execute(
                """
                INSERT INTO run_artifacts (
                    run_id, filename, media_type, checksum, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(run_id),
                    artifact.filename,
                    artifact.media_type,
                    artifact.checksum,
                    artifact.created_at.isoformat().replace("+00:00", "Z"),
                ),
            )
            result = connection.execute(
                """
                UPDATE strategy_runs SET status = ?, updated_at = ?
                WHERE run_id = ? AND status = ?
                """,
                (
                    RunStatus.ARTIFACT_CREATED.value,
                    timestamp,
                    str(run_id),
                    RunStatus.APPROVED.value,
                ),
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
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            result = connection.execute(
                """
                UPDATE strategy_runs
                SET status = ?, strategy_json = ?, error_code = NULL,
                    error_message = NULL, updated_at = ?
                WHERE run_id = ? AND status = ?
                """,
                (
                    RunStatus.AWAITING_REVIEW.value,
                    strategy_json,
                    timestamp,
                    str(run_id),
                    RunStatus.GENERATING.value,
                ),
            )
            if result.rowcount != 1:
                raise RuntimeError("run is not in generating status")
        return self.get(run_id)

    def fail_generation(
        self, run_id: UUID, error_code: str, error_message: str
    ) -> RunRecord:
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            result = connection.execute(
                """
                UPDATE strategy_runs
                SET status = ?, error_code = ?, error_message = ?, updated_at = ?
                WHERE run_id = ? AND status = ?
                """,
                (
                    RunStatus.FAILED.value,
                    error_code,
                    error_message,
                    timestamp,
                    str(run_id),
                    RunStatus.GENERATING.value,
                ),
            )
            if result.rowcount != 1:
                raise RuntimeError("run is not in generating status")
        return self.get(run_id)
