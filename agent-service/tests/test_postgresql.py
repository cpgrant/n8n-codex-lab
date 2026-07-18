from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier, Lock

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError

from ai_factory.config import Settings
from ai_factory.errors import FactoryError
from ai_factory.idempotency import IdempotencyRepository
from ai_factory.main import create_app
from ai_factory.repository import RunRepository
from ai_factory.statuses import RunStatus

POSTGRES_URL = os.getenv("AI_FACTORY_TEST_POSTGRES_URL")
SERVICE_TOKEN = "postgres-service-" + "s" * 32
REVIEW_TOKEN = "postgres-review-" + "r" * 32
REVIEW_ACTOR = "synthetic-postgres-reviewer"

pytestmark = pytest.mark.skipif(
    not POSTGRES_URL,
    reason="AI_FACTORY_TEST_POSTGRES_URL is required for PostgreSQL integration",
)


def test_postgresql_api_lifecycle_and_idempotency(tmp_path, brief_payload):
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        database_url=POSTGRES_URL,
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
    )
    service_headers = {"Authorization": f"Bearer {SERVICE_TOKEN}"}
    review_headers = {
        "Authorization": f"Bearer {REVIEW_TOKEN}",
        "X-AI-Factory-Actor-ID": REVIEW_ACTOR,
        "Idempotency-Key": "postgres-review-001",
    }

    with TestClient(create_app(settings), headers=service_headers) as client:
        created = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "postgres-create-001"},
        )
        replay = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "postgres-create-001"},
        )
        run_id = created.json()["data"]["run_id"]
        quality = client.post(
            f"/v1/strategy-runs/{run_id}/quality-report",
            headers={"Idempotency-Key": "postgres-quality-001"},
        )
        reviewed = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json={"decision": "approved", "reviewer": REVIEW_ACTOR},
            headers=review_headers,
        )
        fetched = client.get(f"/v1/strategy-runs/{run_id}")
        strategy_artifact = client.get(f"/v1/strategy-runs/{run_id}/artifact")
        quality_artifact = client.get(
            f"/v1/strategy-runs/{run_id}/quality-report/artifact"
        )

    assert created.status_code == 201
    assert replay.status_code == 201
    assert replay.json()["meta"]["idempotent_replay"] is True
    assert quality.status_code == 200
    assert reviewed.status_code == 200
    assert reviewed.json()["data"]["status"] == "artifact_created"
    assert fetched.json()["data"]["review"]["reviewer"] == REVIEW_ACTOR
    assert strategy_artifact.status_code == 200
    assert quality_artifact.status_code == 200


def test_postgresql_concurrent_idempotency_reservation():
    repository = IdempotencyRepository(POSTGRES_URL)

    def reserve() -> str:
        try:
            result = repository.reserve(
                "postgres_concurrency", "postgres-concurrent-key", "same-hash"
            )
            return "reserved" if result is None else "replayed"
        except FactoryError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: reserve(), range(2)))

    assert sorted(outcomes) == ["IDEMPOTENCY_IN_PROGRESS", "reserved"]


def test_postgresql_competing_state_transitions_are_atomic(brief):
    repository = RunRepository(POSTGRES_URL)
    run = repository.create(brief)
    barrier = Barrier(2)
    counter_lock = Lock()
    initial_reads = 0
    original_get = repository.get

    def synchronized_get(run_id):
        nonlocal initial_reads
        record = original_get(run_id)
        with counter_lock:
            initial_reads += 1
            should_wait = initial_reads <= 2
        if should_wait:
            barrier.wait()
        return record

    repository.get = synchronized_get

    def transition() -> str:
        try:
            result = repository.transition(run.run_id, RunStatus.GENERATING)
            return result.status.value
        except RuntimeError as exc:
            assert str(exc) == "run status changed concurrently"
            return "concurrent_change_rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: transition(), range(2)))

    assert sorted(outcomes) == ["concurrent_change_rejected", "generating"]


def test_postgresql_unavailable_database_fails_startup_closed(tmp_path):
    unavailable_url = (
        "postgresql+psycopg://synthetic:synthetic@127.0.0.1:1/"
        "unavailable?connect_timeout=1"
    )
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        database_url=unavailable_url,
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
    )

    with pytest.raises(OperationalError):
        with TestClient(create_app(settings)):
            pytest.fail("application started with an unavailable database")
