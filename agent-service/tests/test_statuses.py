import pytest

from ai_factory.statuses import (
    InvalidStatusTransition,
    RunStatus,
    validate_transition,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (RunStatus.RECEIVED, RunStatus.GENERATING),
        (RunStatus.GENERATING, RunStatus.AWAITING_REVIEW),
        (RunStatus.GENERATING, RunStatus.FAILED),
        (RunStatus.AWAITING_REVIEW, RunStatus.APPROVED),
        (RunStatus.AWAITING_REVIEW, RunStatus.REJECTED),
        (RunStatus.APPROVED, RunStatus.ARTIFACT_CREATED),
        (RunStatus.FAILED, RunStatus.GENERATING),
    ],
)
def test_permitted_transitions(current, target):
    validate_transition(current, target)


def test_terminal_status_cannot_transition():
    with pytest.raises(InvalidStatusTransition):
        validate_transition(RunStatus.REJECTED, RunStatus.APPROVED)
