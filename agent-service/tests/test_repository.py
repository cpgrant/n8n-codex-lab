from uuid import uuid4

import pytest

from ai_factory.database import initialize_database
from ai_factory.repository import RunNotFound, RunRepository
from ai_factory.statuses import InvalidStatusTransition, RunStatus


def test_run_persists_across_repository_instances(tmp_path, brief):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    first_repository = RunRepository(database_path)

    created = first_repository.create(brief)

    reopened_repository = RunRepository(database_path)
    loaded = reopened_repository.get(created.run_id)
    assert loaded.status is RunStatus.RECEIVED
    assert loaded.brief["title"] == brief.title


def test_repository_enforces_transition_contract(tmp_path, brief):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = repository.create(brief)

    generating = repository.transition(run.run_id, RunStatus.GENERATING)
    assert generating.status is RunStatus.GENERATING

    with pytest.raises(InvalidStatusTransition):
        repository.transition(run.run_id, RunStatus.APPROVED)


def test_unknown_run_is_reported(tmp_path):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)

    with pytest.raises(RunNotFound):
        RunRepository(database_path).get(uuid4())


def test_completed_strategy_is_durable(tmp_path, brief, response_fixture):
    from ai_factory.schemas import StrategyResponse

    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = repository.create(brief)
    repository.transition(run.run_id, RunStatus.GENERATING)
    response_fixture["run_id"] = str(run.run_id)

    completed = repository.complete_generation(
        run.run_id, StrategyResponse.model_validate(response_fixture)
    )

    reopened = RunRepository(database_path).get(run.run_id)
    assert completed.status is RunStatus.AWAITING_REVIEW
    assert reopened.strategy["executive_summary"] == response_fixture["executive_summary"]
