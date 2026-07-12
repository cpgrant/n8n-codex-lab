from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_factory.schemas import StrategyBrief


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def brief() -> StrategyBrief:
    payload = json.loads(
        (REPOSITORY_ROOT / "examples/strategy-brief.synthetic.json").read_text()
    )
    return StrategyBrief.model_validate(payload)


@pytest.fixture
def brief_payload(brief: StrategyBrief) -> dict[str, object]:
    return brief.model_dump(mode="json")


@pytest.fixture
def response_fixture() -> dict[str, object]:
    return json.loads(
        (REPOSITORY_ROOT / "examples/strategy-response.synthetic.json").read_text()
    )
