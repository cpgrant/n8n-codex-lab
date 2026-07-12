import pytest

from ai_factory.database import initialize_database
from ai_factory.errors import FactoryError
from ai_factory.repository import RunRepository
from ai_factory.service import StrategyService
from ai_factory.statuses import RunStatus


class BrokenProvider:
    name = "broken"

    def generate_strategy(self, brief, run_id):
        raise RuntimeError("secret provider detail")


class InvalidProvider:
    name = "invalid"

    def generate_strategy(self, brief, run_id):
        return {"run_id": str(run_id)}


@pytest.mark.parametrize(
    ("provider", "code", "status_code"),
    [
        (BrokenProvider(), "PROVIDER_ERROR", 502),
        (InvalidProvider(), "PROVIDER_OUTPUT_INVALID", 422),
    ],
)
def test_generation_failure_is_durable(
    tmp_path, brief, provider, code, status_code
):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)

    with pytest.raises(FactoryError) as caught:
        StrategyService(repository, provider).create_run(brief)

    error = caught.value
    persisted = repository.get(error.run_id)
    assert error.code == code
    assert error.status_code == status_code
    assert persisted.status is RunStatus.FAILED
    assert persisted.error_code == code
    assert "secret provider detail" not in persisted.error_message
