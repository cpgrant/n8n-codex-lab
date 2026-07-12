from pathlib import Path

import pytest

from ai_factory.artifacts import MarkdownArtifactStore
from ai_factory.database import initialize_database
from ai_factory.errors import FactoryError
from ai_factory.providers import FakeStrategyProvider
from ai_factory.repository import RunRepository
from ai_factory.review_service import ReviewService
from ai_factory.schemas import ReviewRequest
from ai_factory.service import StrategyService
from ai_factory.statuses import RunStatus


class FailOnceArtifactStore(MarkdownArtifactStore):
    def __init__(self, artifact_dir: Path) -> None:
        super().__init__(artifact_dir)
        self.failed = False

    def create(self, run_id, brief, strategy, review):
        if not self.failed:
            self.failed = True
            raise OSError("private filesystem detail")
        return super().create(run_id, brief, strategy, review)


def generated_run(tmp_path, brief, response_fixture):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = StrategyService(
        repository, FakeStrategyProvider(response_fixture)
    ).create_run(brief)
    return repository, run


def test_rejection_is_terminal_and_creates_no_artifact(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)
    request = ReviewRequest(
        decision="rejected",
        reviewer="synthetic-reviewer",
        comment="Revise this synthetic draft.",
    )

    rejected = ReviewService(
        repository, MarkdownArtifactStore(tmp_path / "artifacts")
    ).review_run(run.run_id, request)

    assert rejected.status is RunStatus.REJECTED
    assert rejected.review["decision"] == "rejected"
    assert rejected.artifact is None
    assert list((tmp_path / "artifacts").glob("*.md")) == []

    with pytest.raises(FactoryError) as second_review:
        ReviewService(
            repository, MarkdownArtifactStore(tmp_path / "artifacts")
        ).review_run(run.run_id, request)
    assert second_review.value.code == "INVALID_STATE_TRANSITION"


def test_render_failure_leaves_approval_durable_and_exact_retry_resumes(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)
    store = FailOnceArtifactStore(tmp_path / "artifacts")
    service = ReviewService(repository, store)
    request = ReviewRequest(
        decision="approved", reviewer="synthetic-reviewer", comment=None
    )

    with pytest.raises(FactoryError) as failed:
        service.review_run(run.run_id, request)

    approved = repository.get(run.run_id)
    assert failed.value.code == "ARTIFACT_RENDER_FAILED"
    assert "private filesystem detail" not in failed.value.message
    assert approved.status is RunStatus.APPROVED
    assert approved.review["decision"] == "approved"
    assert approved.artifact is None

    completed = service.review_run(run.run_id, request)
    assert completed.status is RunStatus.ARTIFACT_CREATED
    assert completed.artifact is not None


def test_changed_approval_cannot_replace_durable_review(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)
    store = FailOnceArtifactStore(tmp_path / "artifacts")
    service = ReviewService(repository, store)
    original = ReviewRequest(
        decision="approved", reviewer="synthetic-reviewer", comment=None
    )
    with pytest.raises(FactoryError):
        service.review_run(run.run_id, original)

    changed = ReviewRequest(
        decision="approved", reviewer="different-reviewer", comment=None
    )
    with pytest.raises(FactoryError) as rejected_change:
        service.review_run(run.run_id, changed)
    assert rejected_change.value.code == "INVALID_STATE_TRANSITION"
