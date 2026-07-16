from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from ai_factory.config import Settings
from ai_factory.main import create_app

SERVICE_TOKEN = "service-token-" + "s" * 32
REVIEW_TOKEN = "review-token-" + "r" * 32
REVIEW_ACTOR = "synthetic-user-001"


class BrokenProvider:
    name = "broken"

    def generate_strategy(self, brief, run_id):
        raise RuntimeError("private failure detail")


def client_for(tmp_path):
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
    )
    return TestClient(
        create_app(settings),
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
    ), settings


def review_headers(idempotency_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {REVIEW_TOKEN}",
        "X-AI-Factory-Actor-ID": REVIEW_ACTOR,
        "Idempotency-Key": idempotency_key,
    }


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


def test_stage8_unknown_uploaded_brief_fields_are_rejected_clearly(
    tmp_path, brief_payload
):
    client, _ = client_for(tmp_path)
    unknown_top_level = deepcopy(brief_payload)
    unknown_top_level["uploaded_filename"] = "never-use-this.json"
    unknown_organization = deepcopy(brief_payload)
    unknown_organization["organization"]["secret"] = "synthetic"

    with client:
        top_level = client.post(
            "/v1/strategy-runs",
            json=unknown_top_level,
            headers={"Idempotency-Key": "stage8-unknown-top-level"},
        )
        organization = client.post(
            "/v1/strategy-runs",
            json=unknown_organization,
            headers={"Idempotency-Key": "stage8-unknown-organization"},
        )

    assert top_level.status_code == 400
    assert top_level.json()["error"]["code"] == "VALIDATION_ERROR"
    assert any(
        detail["field"] == "uploaded_filename"
        for detail in top_level.json()["error"]["details"]
    )
    assert organization.status_code == 400
    assert organization.json()["error"]["code"] == "VALIDATION_ERROR"
    assert any(
        detail["field"] == "organization.secret"
        for detail in organization.json()["error"]["details"]
    )


def test_request_id_is_returned_in_header_and_body(tmp_path):
    client, _ = client_for(tmp_path)

    with client:
        response = client.get("/health", headers={"X-Request-ID": "req_known"})

    assert response.headers["X-Request-ID"] == "req_known"


def test_authentication_fails_closed_and_scopes_are_separate(
    tmp_path, brief_payload
):
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
    )
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        missing = client.post("/v1/strategy-runs", json=brief_payload)
        invalid = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Authorization": "Bearer invalid-token"},
        )
        wrong_scope = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Authorization": f"Bearer {REVIEW_TOKEN}"},
        )

    assert health.status_code == 200
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert missing.headers["www-authenticate"] == "Bearer"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "AUTHENTICATION_INVALID"
    assert wrong_scope.status_code == 403
    assert wrong_scope.json()["error"]["code"] == "AUTHORIZATION_DENIED"
    assert SERVICE_TOKEN not in missing.text + invalid.text + wrong_scope.text
    assert REVIEW_TOKEN not in missing.text + invalid.text + wrong_scope.text


def test_missing_configuration_and_expired_token_fail_safely(
    tmp_path, brief_payload
):
    unconfigured = Settings(
        data_dir=tmp_path / "unconfigured-data",
        artifact_dir=tmp_path / "unconfigured-artifacts",
    )
    expired = Settings(
        data_dir=tmp_path / "expired-data",
        artifact_dir=tmp_path / "expired-artifacts",
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
        service_token_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )

    with TestClient(create_app(unconfigured)) as client:
        not_configured = client.post("/v1/strategy-runs", json=brief_payload)
    with TestClient(create_app(expired)) as client:
        expired_response = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
        )

    assert not_configured.status_code == 503
    assert not_configured.json()["error"]["code"] == (
        "AUTHENTICATION_NOT_CONFIGURED"
    )
    assert expired_response.status_code == 401
    assert expired_response.json()["error"]["code"] == "AUTHENTICATION_EXPIRED"


def test_review_requires_review_scope_and_matching_authenticated_actor(
    tmp_path, brief_payload
):
    client, _ = client_for(tmp_path)
    decision = {"decision": "approved", "reviewer": REVIEW_ACTOR}

    with client:
        created = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "auth-review-create-001"},
        )
        run_id = created.json()["data"]["run_id"]
        service_scope = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json=decision,
            headers={"Idempotency-Key": "auth-review-service-001"},
        )
        missing_actor = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json=decision,
            headers={
                "Authorization": f"Bearer {REVIEW_TOKEN}",
                "Idempotency-Key": "auth-review-missing-actor-001",
            },
        )
        mismatched_actor = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json=decision,
            headers={
                **review_headers("auth-review-mismatch-001"),
                "X-AI-Factory-Actor-ID": "different-synthetic-user",
            },
        )
        fetched = client.get(f"/v1/strategy-runs/{run_id}")

    assert service_scope.status_code == 403
    assert service_scope.json()["error"]["code"] == "AUTHORIZATION_DENIED"
    assert missing_actor.status_code == 403
    assert missing_actor.json()["error"]["code"] == "AUTHORIZATION_DENIED"
    assert mismatched_actor.status_code == 403
    assert mismatched_actor.json()["error"]["code"] == "AUTHORIZATION_DENIED"
    assert fetched.json()["data"]["status"] == "awaiting_review"
    assert fetched.json()["data"]["review"] is None


def test_failed_generation_is_safe_durable_and_replayable(tmp_path, brief_payload):
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        service_token=SERVICE_TOKEN,
        review_token=REVIEW_TOKEN,
    )
    headers = {"Idempotency-Key": "synthetic-failure-001"}

    with TestClient(
        create_app(settings, provider=BrokenProvider()),
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
    ) as client:
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


def test_approval_creates_replayable_retrievable_markdown(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)
    approval = {
        "decision": "approved",
        "reviewer": REVIEW_ACTOR,
        "comment": "Approved for the fictional planning exercise.",
    }

    with client:
        created = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "synthetic-create-review-001"},
        )
        run_id = created.json()["data"]["run_id"]
        not_ready = client.get(f"/v1/strategy-runs/{run_id}/artifact")
        reviewed = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json=approval,
            headers=review_headers("synthetic-approval-001"),
        )
        replay = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json=approval,
            headers=review_headers("synthetic-approval-001"),
        )
        fetched = client.get(f"/v1/strategy-runs/{run_id}")
        artifact = client.get(f"/v1/strategy-runs/{run_id}/artifact")

    assert not_ready.status_code == 409
    assert not_ready.json()["error"]["code"] == "ARTIFACT_NOT_READY"
    assert reviewed.status_code == 200
    assert reviewed.json()["data"]["status"] == "artifact_created"
    assert reviewed.json()["data"]["review"]["decision"] == "approved"
    assert reviewed.json()["data"]["artifact"]["media_type"] == "text/markdown"
    assert replay.status_code == 200
    assert replay.json()["data"] == reviewed.json()["data"]
    assert replay.json()["meta"]["idempotent_replay"] is True
    assert fetched.json()["data"]["review"] == reviewed.json()["data"]["review"]
    assert fetched.json()["data"]["artifact"] == reviewed.json()["data"]["artifact"]
    assert artifact.status_code == 200
    assert artifact.headers["content-type"].startswith("text/markdown")
    assert "## Executive summary" in artifact.text
    assert "Approved AI Strategy Factory v0.1 artifact" in artifact.text


def test_rejection_requires_comment_and_is_final(tmp_path, brief_payload):
    client, _ = client_for(tmp_path)

    with client:
        created = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "synthetic-create-review-002"},
        )
        run_id = created.json()["data"]["run_id"]
        invalid = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json={"decision": "rejected", "reviewer": REVIEW_ACTOR},
            headers=review_headers("synthetic-rejection-invalid"),
        )
        rejected = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json={
                "decision": "rejected",
                "reviewer": REVIEW_ACTOR,
                "comment": "Revise the fictional sequencing.",
            },
            headers=review_headers("synthetic-rejection-001"),
        )
        later_approval = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json={"decision": "approved", "reviewer": REVIEW_ACTOR},
            headers=review_headers("synthetic-approval-too-late"),
        )
        artifact = client.get(f"/v1/strategy-runs/{run_id}/artifact")

    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
    assert rejected.status_code == 200
    assert rejected.json()["data"]["status"] == "rejected"
    assert rejected.json()["data"]["artifact"] is None
    assert later_approval.status_code == 409
    assert later_approval.json()["error"]["code"] == "INVALID_STATE_TRANSITION"
    assert artifact.status_code == 409


def test_quality_report_is_idempotent_retrievable_and_advisory(
    tmp_path, brief_payload
):
    client, _ = client_for(tmp_path)

    with client:
        created = client.post(
            "/v1/strategy-runs",
            json=brief_payload,
            headers={"Idempotency-Key": "synthetic-quality-create-001"},
        )
        run_id = created.json()["data"]["run_id"]
        not_ready = client.get(f"/v1/strategy-runs/{run_id}/quality-report")
        artifact_not_ready = client.get(
            f"/v1/strategy-runs/{run_id}/quality-report/artifact"
        )
        quality = client.post(
            f"/v1/strategy-runs/{run_id}/quality-report",
            headers={"Idempotency-Key": "synthetic-quality-001"},
        )
        replay = client.post(
            f"/v1/strategy-runs/{run_id}/quality-report",
            headers={"Idempotency-Key": "synthetic-quality-001"},
        )
        fetched_quality = client.get(
            f"/v1/strategy-runs/{run_id}/quality-report"
        )
        fetched_run = client.get(f"/v1/strategy-runs/{run_id}")
        quality_artifact = client.get(
            f"/v1/strategy-runs/{run_id}/quality-report/artifact"
        )
        reviewed = client.post(
            f"/v1/strategy-runs/{run_id}/review",
            json={"decision": "approved", "reviewer": REVIEW_ACTOR},
            headers=review_headers("synthetic-quality-approval-001"),
        )
        approved_artifact = client.get(
            f"/v1/strategy-runs/{run_id}/artifact"
        )
        quality_artifact_after_review = client.get(
            f"/v1/strategy-runs/{run_id}/quality-report/artifact"
        )

    report = quality.json()["data"]["quality_report"]
    assert not_ready.status_code == 409
    assert not_ready.json()["error"]["code"] == "QUALITY_REPORT_NOT_READY"
    assert artifact_not_ready.status_code == 409
    assert artifact_not_ready.json()["error"]["code"] == (
        "QUALITY_ARTIFACT_NOT_READY"
    )
    assert quality.status_code == 200
    assert report["mode"] == "basic"
    assert report["critic_provider"] == "deterministic"
    assert quality.json()["data"]["status"] == "awaiting_review"
    assert replay.json()["data"] == quality.json()["data"]
    assert replay.json()["meta"]["idempotent_replay"] is True
    assert fetched_quality.json()["data"]["quality_report"] == report
    assert fetched_run.json()["data"]["quality_report"] == report
    artifact_metadata = quality.json()["data"]["quality_artifact"]
    assert artifact_metadata["filename"] == f"quality-report-{run_id}.md"
    assert fetched_quality.json()["data"]["quality_artifact"] == artifact_metadata
    assert fetched_run.json()["data"]["quality_artifact"] == artifact_metadata
    assert quality_artifact.status_code == 200
    assert quality_artifact.headers["content-type"].startswith("text/markdown")
    assert artifact_metadata["filename"] in quality_artifact.headers[
        "content-disposition"
    ]
    assert "Advisory AI Strategy Factory quality report" in quality_artifact.text
    assert f"| Run ID | `{run_id}` |" in quality_artifact.text
    assert reviewed.status_code == 200
    assert reviewed.json()["data"]["review"]["draft_checksum"] == report[
        "draft_checksum"
    ]
    assert approved_artifact.status_code == 200
    assert "## Decision summary" in approved_artifact.text
    assert (
        f"| Advisory quality score | {report['overall_score']}/100 |"
        in approved_artifact.text
    )
    assert (
        f"`quality-reports/quality-report-{run_id}.md`"
        in approved_artifact.text
    )
    assert quality_artifact_after_review.status_code == 200
    assert quality_artifact_after_review.text == quality_artifact.text
