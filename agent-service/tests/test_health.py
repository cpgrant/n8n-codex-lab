from fastapi.testclient import TestClient

from ai_factory.config import Settings
from ai_factory.main import create_app


def test_health_initializes_database_and_returns_contract(tmp_path):
    settings = Settings(
        data_dir=tmp_path / "data", artifact_dir=tmp_path / "artifacts"
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-strategy-factory",
        "version": "0.1",
    }
    assert settings.database_path.exists()
    assert settings.artifact_dir.is_dir()


def test_explicit_sqlite_url_uses_versioned_schema(tmp_path):
    database_path = tmp_path / "portable.db"
    settings = Settings(
        data_dir=tmp_path / "data",
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{database_path}",
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert database_path.exists()
