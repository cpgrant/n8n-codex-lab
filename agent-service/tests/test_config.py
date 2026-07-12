import pytest

from ai_factory.config import Settings


def test_config_defaults(monkeypatch):
    for name in (
        "AI_FACTORY_HOST",
        "AI_FACTORY_PORT",
        "AI_FACTORY_HOST_URL",
        "AI_FACTORY_N8N_URL",
        "AI_FACTORY_PROVIDER",
        "AI_FACTORY_DATA_DIR",
        "AI_FACTORY_ARTIFACT_DIR",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_env()

    assert settings.host_url == "http://127.0.0.1:8000"
    assert settings.n8n_url == "http://host.docker.internal:8000"
    assert settings.provider == "fake"
    assert settings.data_dir.name == "data"
    assert settings.data_dir.parent.name == "n8n-codex-lab"


def test_invalid_port_is_rejected(monkeypatch):
    monkeypatch.setenv("AI_FACTORY_PORT", "not-a-port")

    with pytest.raises(ValueError, match="must be an integer"):
        Settings.from_env()
