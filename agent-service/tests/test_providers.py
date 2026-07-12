from uuid import uuid4

import pytest

from ai_factory.providers import FakeStrategyProvider, OpenAIStrategyProvider


def test_fake_provider_is_deterministic(brief, response_fixture):
    provider = FakeStrategyProvider(response_fixture)
    run_id = uuid4()

    first = provider.generate_strategy(brief, run_id)
    second = provider.generate_strategy(brief, run_id)

    assert first == second
    assert first["run_id"] == str(run_id)
    assert first["provider"] == "fake"


def test_openai_provider_is_explicitly_deferred(brief):
    with pytest.raises(NotImplementedError, match="not implemented in Stage 1"):
        OpenAIStrategyProvider().generate_strategy(brief, uuid4())
