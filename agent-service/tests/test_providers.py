import json
from uuid import uuid4

import pytest

from ai_factory.providers import (
    FakeStrategyProvider,
    OllamaQualityCritic,
    OllamaStrategyProvider,
    OpenAIStrategyProvider,
    ProviderOutputError,
    ProviderTransportError,
)
from ai_factory.quality import DeterministicQualityReviewer
from ai_factory.schemas import StrategyResponse


def test_fake_provider_is_deterministic(brief, response_fixture):
    provider = FakeStrategyProvider(response_fixture)
    run_id = uuid4()

    first = provider.generate_strategy(brief, run_id)
    second = provider.generate_strategy(brief, run_id)

    assert first == second
    assert first["run_id"] == str(run_id)
    assert first["provider"] == "fake"


def test_openai_provider_is_explicitly_deferred(brief):
    with pytest.raises(NotImplementedError, match="not implemented in Stage 6"):
        OpenAIStrategyProvider().generate_strategy(brief, uuid4())


def test_ollama_provider_sends_schema_and_injects_service_metadata(
    brief, response_fixture
):
    captured = {}
    content = {
        key: value
        for key, value in response_fixture.items()
        if key
        not in {"schema_version", "run_id", "status", "generated_at", "provider"}
    }

    def transport(url, payload, timeout):
        captured.update(url=url, payload=payload, timeout=timeout)
        return {
            "message": {"role": "assistant", "content": json.dumps(content)}
        }

    run_id = uuid4()
    provider = OllamaStrategyProvider(
        "http://127.0.0.1:11888", "gemma4:31b", 300, transport=transport
    )

    result = provider.generate_strategy(brief, run_id)

    assert captured["url"] == "http://127.0.0.1:11888/api/chat"
    assert captured["timeout"] == 300
    assert captured["payload"]["model"] == "gemma4:31b"
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["think"] is False
    assert captured["payload"]["options"] == {"temperature": 0}
    assert captured["payload"]["format"]["type"] == "object"
    prompt = " ".join(
        message["content"] for message in captured["payload"]["messages"]
    )
    assert "measurable numeric targets" in prompt
    assert "desired end-state number" in prompt
    assert "repeat that exact end-state target" in prompt
    assert "never use different target values" in prompt
    assert "Use stakeholder labels" in prompt
    assert "sequential IDs without gaps" in prompt
    assert result["run_id"] == str(run_id)
    assert result["provider"] == "ollama"
    assert result["status"] == "awaiting_review"


@pytest.mark.parametrize(
    ("envelope", "error_type"),
    [
        ({"message": {}}, ProviderTransportError),
        ({"message": {"content": "not-json"}}, ProviderOutputError),
        ({"message": {"content": "[]"}}, ProviderOutputError),
    ],
)
def test_ollama_provider_rejects_invalid_responses(brief, envelope, error_type):
    provider = OllamaStrategyProvider(
        "http://127.0.0.1:11888",
        "gemma4:31b",
        300,
        transport=lambda *_: envelope,
    )

    with pytest.raises(error_type):
        provider.generate_strategy(brief, uuid4())


def test_ollama_quality_critic_is_advisory_and_schema_constrained(
    brief, response_fixture
):
    captured = {}
    strategy = StrategyResponse.model_validate(response_fixture)
    deterministic = DeterministicQualityReviewer().assess(brief, strategy)

    def transport(url, payload, timeout):
        captured.update(url=url, payload=payload, timeout=timeout)
        return {
            "message": {
                "role": "assistant",
                "content": deterministic.model_dump_json(),
            }
        }

    critic = OllamaQualityCritic(
        "http://127.0.0.1:11888", "gemma4:31b", 300, transport=transport
    )
    result = critic.review_strategy(brief, strategy, deterministic)

    assert captured["url"] == "http://127.0.0.1:11888/api/chat"
    assert captured["payload"]["format"]["type"] == "object"
    prompt = " ".join(
        message["content"] for message in captured["payload"]["messages"]
    )
    assert "Do not rewrite" in prompt
    assert "must not be removed" in prompt
    assert "maps clearly to an objective" in prompt
    assert "repeated exactly" in prompt
    assert "baseline or scope number" in prompt
    assert "DETERMINISTIC FINDINGS" in prompt
    assert result["checks"] == deterministic.model_dump(mode="json")["checks"]
