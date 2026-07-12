"""Strategy provider boundary and deterministic test provider."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Protocol
from uuid import UUID

from .schemas import StrategyBrief


class StrategyProvider(Protocol):
    name: str

    def generate_strategy(
        self, brief: StrategyBrief, run_id: UUID
    ) -> dict[str, object]: ...


class FakeStrategyProvider:
    """Return a deterministic synthetic strategy without network access."""

    name = "fake"

    def __init__(self, fixture: dict[str, object]) -> None:
        self._fixture = deepcopy(fixture)

    def generate_strategy(
        self, brief: StrategyBrief, run_id: UUID
    ) -> dict[str, object]:
        del brief
        result = deepcopy(self._fixture)
        result["run_id"] = str(run_id)
        result["provider"] = self.name
        return result

    @classmethod
    def from_fixture(cls, fixture_path: Path) -> "FakeStrategyProvider":
        return cls(json.loads(fixture_path.read_text(encoding="utf-8")))


class OpenAIStrategyProvider:
    """Reserved provider name; implementation belongs to a later stage."""

    name = "openai"

    def generate_strategy(
        self, brief: StrategyBrief, run_id: UUID
    ) -> dict[str, object]:
        raise NotImplementedError("OpenAIStrategyProvider is not implemented in Stage 1")
