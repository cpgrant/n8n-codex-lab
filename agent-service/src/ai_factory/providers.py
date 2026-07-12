"""Strategy provider boundary and deterministic test provider."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
from typing import Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID

from .schemas import StrategyBrief, StrategyContent


class ProviderTransportError(Exception):
    """The provider could not be reached or returned an invalid envelope."""


class ProviderOutputError(Exception):
    """The provider response did not contain parseable structured content."""


OllamaTransport = Callable[[str, dict[str, object], float], dict[str, object]]


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


class OllamaStrategyProvider:
    """Generate structured strategy content through a local Ollama server."""

    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
        transport: OllamaTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._transport = transport or self._post_json

    def generate_strategy(
        self, brief: StrategyBrief, run_id: UUID
    ) -> dict[str, object]:
        schema = StrategyContent.model_json_schema()
        brief_json = json.dumps(
            brief.model_dump(mode="json"), ensure_ascii=False, indent=2
        )
        schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        payload: dict[str, object] = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {"temperature": 0},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are AI Strategy Factory v0.1. Create a concise but "
                        "decision-ready strategy using only the supplied synthetic "
                        "brief. Ground every factual claim in the brief. Do not invent "
                        "people, organizations, evidence, credentials, URLs, software, "
                        "budgets, or confidential facts. Use stakeholder labels from "
                        "the brief as owner roles when stakeholders are supplied. "
                        "Reflect every material constraint in the choices or "
                        "initiatives. Preserve numeric baselines and use measurable "
                        "numeric targets when the evidence supports them. A target "
                        "must state a desired end-state number; never use vague targets "
                        "such as 'higher', 'increase', or 'improve' without that number. "
                        "If no "
                        "evidence is supplied, return an empty evidence list rather "
                        "than fabricating evidence. Return only JSON that satisfies "
                        "the supplied schema."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Generate the eight-section strategy for this synthetic brief. "
                        "Make each objective distinct, each strategic choice a real "
                        "decision with an explicit trade-off, and each initiative "
                        "specific enough to execute. Use sequential IDs without gaps, "
                        "reference only objective IDs that exist, and order next steps "
                        "sequentially from 1.\n\n"
                        f"BRIEF:\n{brief_json}\n\nJSON SCHEMA:\n{schema_json}"
                    ),
                },
            ],
        }

        envelope = self._transport(
            f"{self.base_url}/api/chat", payload, self.timeout_seconds
        )
        message = envelope.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ProviderTransportError("Ollama returned an invalid response envelope")
        try:
            content = json.loads(message["content"])
        except json.JSONDecodeError as exc:
            raise ProviderOutputError("Ollama returned malformed structured JSON") from exc
        if not isinstance(content, dict):
            raise ProviderOutputError("Ollama structured output was not an object")

        result = dict(content)
        result.update(
            {
                "schema_version": "0.1",
                "run_id": str(run_id),
                "status": "awaiting_review",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "provider": self.name,
            }
        )
        return result

    @staticmethod
    def _post_json(
        url: str, payload: dict[str, object], timeout_seconds: float
    ) -> dict[str, object]:
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
        except (HTTPError, URLError, TimeoutError, socket.timeout, OSError) as exc:
            raise ProviderTransportError("Ollama request failed") from exc
        try:
            envelope = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProviderTransportError("Ollama returned an invalid JSON envelope") from exc
        if not isinstance(envelope, dict):
            raise ProviderTransportError("Ollama response envelope was not an object")
        return envelope


class OpenAIStrategyProvider:
    """Reserved provider name; implementation belongs to a later stage."""

    name = "openai"

    def generate_strategy(
        self, brief: StrategyBrief, run_id: UUID
    ) -> dict[str, object]:
        raise NotImplementedError("OpenAIStrategyProvider is not implemented in Stage 6")
