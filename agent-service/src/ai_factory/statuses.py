"""Run statuses and their permitted transitions."""

from enum import StrEnum


class RunStatus(StrEnum):
    RECEIVED = "received"
    GENERATING = "generating"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    ARTIFACT_CREATED = "artifact_created"
    REJECTED = "rejected"
    FAILED = "failed"


PERMITTED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.RECEIVED: frozenset({RunStatus.GENERATING}),
    RunStatus.GENERATING: frozenset(
        {RunStatus.AWAITING_REVIEW, RunStatus.FAILED}
    ),
    RunStatus.AWAITING_REVIEW: frozenset(
        {RunStatus.APPROVED, RunStatus.REJECTED}
    ),
    RunStatus.APPROVED: frozenset({RunStatus.ARTIFACT_CREATED}),
    RunStatus.ARTIFACT_CREATED: frozenset(),
    RunStatus.REJECTED: frozenset(),
    RunStatus.FAILED: frozenset({RunStatus.GENERATING}),
}


class InvalidStatusTransition(ValueError):
    """Raised when a run attempts a transition outside the contract."""


def validate_transition(current: RunStatus, target: RunStatus) -> None:
    if target not in PERMITTED_TRANSITIONS[current]:
        raise InvalidStatusTransition(
            f"transition from {current.value} to {target.value} is not permitted"
        )
