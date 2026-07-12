import json

import pytest
from pydantic import ValidationError

from ai_factory.schemas import StrategyBrief, StrategyResponse


def test_checked_in_examples_match_contract(brief, response_fixture):
    assert brief.schema_version == "0.1"
    response = StrategyResponse.model_validate(response_fixture)
    assert response.provider == "fake"


def test_unknown_brief_fields_are_rejected(brief):
    payload = brief.model_dump(mode="json")
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        StrategyBrief.model_validate(payload)


def test_brief_requires_an_outcome(brief):
    payload = brief.model_dump(mode="json")
    payload["desired_outcomes"] = []

    with pytest.raises(ValidationError):
        StrategyBrief.model_validate(payload)
