import pytest

from ai_factory.config import Settings
from ai_factory.main import default_provider, default_quality_critic
from ai_factory.providers import OllamaQualityCritic, OllamaStrategyProvider


def test_config_defaults(monkeypatch):
    for name in (
        "AI_FACTORY_HOST",
        "AI_FACTORY_PORT",
        "AI_FACTORY_HOST_URL",
        "AI_FACTORY_N8N_URL",
        "AI_FACTORY_PROVIDER",
        "AI_FACTORY_DATA_DIR",
        "AI_FACTORY_ARTIFACT_DIR",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "AI_FACTORY_QUALITY_MODE",
        "OLLAMA_QUALITY_MODEL",
        "OLLAMA_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_env()

    assert settings.host_url == "http://127.0.0.1:8000"
    assert settings.n8n_url == "http://host.docker.internal:8000"
    assert settings.provider == "fake"
    assert settings.ollama_base_url == "http://127.0.0.1:11888"
    assert settings.ollama_model == "gemma4:31b"
    assert settings.quality_mode == "basic"
    assert settings.ollama_quality_model == "gemma4:31b"
    assert default_quality_critic(settings) is None
    assert settings.ollama_timeout_seconds == 300
    assert settings.data_dir.name == "data"
    assert settings.data_dir.parent.name == "n8n-codex-lab"


def test_invalid_port_is_rejected(monkeypatch):
    monkeypatch.setenv("AI_FACTORY_PORT", "not-a-port")

    with pytest.raises(ValueError, match="must be an integer"):
        Settings.from_env()


def test_ollama_config_and_provider_selection(monkeypatch):
    monkeypatch.setenv("AI_FACTORY_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11888/")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:12b")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "45.5")

    settings = Settings.from_env()

    assert settings.provider == "ollama"
    assert settings.ollama_base_url == "http://127.0.0.1:11888"
    assert settings.ollama_model == "gemma4:12b"
    assert settings.ollama_timeout_seconds == 45.5
    assert isinstance(default_provider(settings), OllamaStrategyProvider)


def test_pro_quality_mode_selects_separate_ollama_critic(monkeypatch):
    monkeypatch.setenv("AI_FACTORY_QUALITY_MODE", "pro")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:31b")
    monkeypatch.setenv("OLLAMA_QUALITY_MODEL", "gemma4:26b")

    settings = Settings.from_env()
    critic = default_quality_critic(settings)

    assert settings.quality_mode == "pro"
    assert settings.ollama_quality_model == "gemma4:26b"
    assert isinstance(critic, OllamaQualityCritic)
    assert critic.model == "gemma4:26b"


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("OLLAMA_BASE_URL", "localhost:11888", "absolute HTTP"),
        ("OLLAMA_MODEL", " ", "must not be empty"),
        ("OLLAMA_TIMEOUT_SECONDS", "slow", "must be a number"),
        ("OLLAMA_TIMEOUT_SECONDS", "0", "between 1 and 1800"),
        ("AI_FACTORY_QUALITY_MODE", "premium", "basic.*pro"),
        ("OLLAMA_QUALITY_MODEL", " ", "must not be empty"),
    ],
)
def test_invalid_ollama_config_is_rejected(monkeypatch, name, value, message):
    monkeypatch.setenv(name, value)

    with pytest.raises(ValueError, match=message):
        Settings.from_env()
