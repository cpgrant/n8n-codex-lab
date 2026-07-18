from datetime import UTC, datetime
import os

import pytest
from sqlalchemy.exc import IntegrityError

from ai_factory.database import create_database_engine
from ai_factory.errors import FactoryError
from ai_factory.idempotency import IdempotencyRepository
from ai_factory.migrations import upgrade_database
from ai_factory.repository import RunRepository
from ai_factory.schemas import ArtifactMetadata, ReviewRecord, StrategyResponse
from ai_factory.service import StrategyService
from ai_factory.statuses import RunStatus


class BrokenProvider:
    name = "broken"

    def generate_strategy(self, brief, run_id):
        del brief, run_id
        raise RuntimeError("private synthetic provider detail")


@pytest.fixture(params=("sqlite", "postgresql"))
def database_url(request, tmp_path):
    if request.param == "sqlite":
        url = f"sqlite:///{tmp_path / 'portability.db'}"
        upgrade_database(url)
        return url

    url = os.getenv("AI_FACTORY_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("AI_FACTORY_TEST_POSTGRES_URL is required")
    return url


def _generated_run(database_url, brief, response_fixture):
    repository = RunRepository(database_url)
    run = repository.create(brief)
    repository.transition(run.run_id, RunStatus.GENERATING)
    response_fixture["run_id"] = str(run.run_id)
    run = repository.complete_generation(
        run.run_id, StrategyResponse.model_validate(response_fixture)
    )
    return repository, run


def _approved_run(database_url, brief, response_fixture, reviewer):
    repository, run = _generated_run(database_url, brief, response_fixture)
    run = repository.record_review(
        run.run_id,
        ReviewRecord(
            decision="approved",
            reviewer=reviewer,
            comment=None,
            decided_at=datetime.now(UTC),
            draft_checksum="sha256:" + "b" * 64,
        ),
    )
    return repository, run


def test_repository_and_idempotency_survive_engine_restart(
    database_url, brief
):
    first_engine = create_database_engine(database_url)
    first_runs = RunRepository(first_engine)
    first_idempotency = IdempotencyRepository(first_engine)
    run = first_runs.create(brief)
    operation = f"restart-{run.run_id}"
    key = f"restart-key-{run.run_id}"
    first_idempotency.reserve(operation, key, "same-hash")
    first_idempotency.complete(
        operation,
        key,
        "same-hash",
        201,
        {"data": {"run_id": str(run.run_id)}},
        run.run_id,
    )
    first_engine.dispose()

    second_engine = create_database_engine(database_url)
    try:
        reopened = RunRepository(second_engine).get(run.run_id)
        replay = IdempotencyRepository(second_engine).reserve(
            operation, key, "same-hash"
        )
    finally:
        second_engine.dispose()

    assert reopened.brief["title"] == brief.title
    assert replay.status_code == 201
    assert replay.payload["data"]["run_id"] == str(run.run_id)


def test_generation_failure_is_durable_on_each_backend(database_url, brief):
    repository = RunRepository(database_url)

    with pytest.raises(FactoryError) as caught:
        StrategyService(repository, BrokenProvider()).create_run(brief)

    persisted = repository.get(caught.value.run_id)
    assert caught.value.code == "PROVIDER_ERROR"
    assert persisted.status is RunStatus.FAILED
    assert persisted.error_code == "PROVIDER_ERROR"
    assert "private synthetic provider detail" not in persisted.error_message


def test_artifact_constraint_failure_rolls_back_status_and_metadata(
    database_url, brief, response_fixture
):
    first_repository, first = _approved_run(
        database_url, brief, response_fixture.copy(), "synthetic-reviewer-one"
    )
    second_repository, second = _approved_run(
        database_url, brief, response_fixture.copy(), "synthetic-reviewer-two"
    )
    artifact = ArtifactMetadata(
        filename=f"strategy-{first.run_id}.md",
        media_type="text/markdown",
        checksum="sha256:" + "a" * 64,
        created_at=datetime.now(UTC),
    )
    first_repository.record_artifact(first.run_id, artifact)

    with pytest.raises(IntegrityError):
        second_repository.record_artifact(second.run_id, artifact)

    unchanged = second_repository.get(second.run_id)
    assert unchanged.status is RunStatus.APPROVED
    assert unchanged.artifact is None


def test_pending_idempotency_release_allows_retry_on_each_backend(database_url):
    repository = IdempotencyRepository(database_url)
    operation = f"release-{datetime.now(UTC).timestamp()}"
    key = f"release-key-{datetime.now(UTC).timestamp()}"
    repository.reserve(operation, key, "same-hash")
    repository.release(operation, key, "same-hash")

    assert repository.reserve(operation, key, "same-hash") is None
