from uuid import uuid4

from fastapi.testclient import TestClient

from ai_factory.config import Settings
from ai_factory.main import create_app


class BrokenProvider:
    name = "broken"

    def generate_strategy(self, brief, run_id):
        raise RuntimeError("private failure detail")


def client_for(tmp_path):
    settings = Settings(
        data_dir=tmp_path / "data", artifact_dir=tmp_path / "artifacts"
    )
    return TestClient(create_app(settings)), settings


def test_create_read_and_replay_strategy_run(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)
    headers = {"Idempotency-Key": "synthetic-create-001", "X-Request-ID": "req_test"}

    with client:
        created = client.post(
            "/v1/strategy-runs", json=brief_payload, headers=headers
        )
        replay = client.post(
            "/v1/strategy-runs", json=brief_payload, headers=headers
        )
        fetched = client.get(
            f"/v1/strategy-runs/{created.json()['data']['run_id']}"
        )

    assert created.status_code == 201
    assert created.json()["data"]["status"] == "awaiting_review"
    assert created.json()["data"]["strategy"]["provider"] == "fake"
    assert created.json()["meta"] == {
        "request_id": "req_test",
        "idempotent_replay": False,
    }
    assert replay.status_code == 201
    assert replay.json()["data"] == created.json()["data"]
    assert replay.json()["meta"]["idempotent_replay"] is True
    assert fetched.status_code == 200
    assert fetched.json()["data"]["brief"]["title"] == brief_payload["title"]
    assert fetched.json()["data"]["review"] is None


def test_create_requires_idempotency_key(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)

    with client:
        response = client.post("/v1/strategy-runs", json=brief_payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"


def test_reused_key_with_different_brief_conflicts(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)
    headers = {"Idempotency-Key": "synthetic-create-002"}

    with client:
        first = client.post("/v1/strategy-runs", json=brief_payload, headers=headers)
        changed = dict(brief_payload)
        changed["title"] = "A different synthetic brief"
        second = client.post("/v1/strategy-runs", json=changed, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_validation_and_not_found_use_error_contract(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)
    invalid = dict(brief_payload)
    invalid["desired_outcomes"] = []

    with client:
        validation = client.post(
            "/v1/strategy-runs",
            json=invalid,
            headers={"Idempotency-Key": "synthetic-create-003"},
        )
        missing = client.get(f"/v1/strategy-runs/{uuid4()}")

    assert validation.status_code == 400
    assert validation.json()["error"]["code"] == "VALIDATION_ERROR"
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "RUN_NOT_FOUND"


def test_request_id_is_returned_in_header_and_body(tmp_path):
    client, _ = client_for(tmp_path)

    with client:
        response = client.get("/health", headers={"X-Request-ID": "req_known"})

    assert response.headers["X-Request-ID"] == "req_known"


def test_failed_generation_is_safe_durable_and_replayable(tmp_path, brief_payload):
    settings = Settings(
        data_dir=tmp_path / "data", artifact_dir=tmp_path / "artifacts"
    )
    headers = {"Idempotency-Key": "synthetic-failure-001"}

    with TestClient(create_app(settings, provider=BrokenProvider())) as client:
        failed = client.post("/v1/strategy-runs", json=brief_payload, headers=headers)
        replay = client.post("/v1/strategy-runs", json=brief_payload, headers=headers)
        run = client.get(
            f"/v1/strategy-runs/{failed.json()['error']['run_id']}"
        )

    assert failed.status_code == 502
    assert failed.json()["error"]["code"] == "PROVIDER_ERROR"
    assert "private failure detail" not in failed.text
    assert replay.status_code == 502
    assert replay.json()["meta"]["idempotent_replay"] is True
    assert run.json()["data"]["status"] == "failed"
    assert run.json()["data"]["error_code"] == "PROVIDER_ERROR"
