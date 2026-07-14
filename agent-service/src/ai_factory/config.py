"""Environment-backed service configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    host_url: str = "http://127.0.0.1:8000"
    n8n_url: str = "http://host.docker.internal:8000"
    provider: str = "fake"
    ollama_base_url: str = "http://127.0.0.1:11888"
    ollama_model: str = "gemma4:31b"
    quality_mode: str = "basic"
    ollama_quality_model: str = "gemma4:31b"
    ollama_timeout_seconds: float = 300.0
    data_dir: Path = REPOSITORY_ROOT / "data"
    artifact_dir: Path = REPOSITORY_ROOT / "artifacts"
    service_token: str | None = None
    review_token: str | None = None
    service_token_expires_at: datetime | None = None
    review_token_expires_at: datetime | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("AI_FACTORY_SERVICE_TOKEN", self.service_token),
            ("AI_FACTORY_REVIEW_TOKEN", self.review_token),
        ):
            if value is not None and len(value) < 32:
                raise ValueError(f"{name} must contain at least 32 characters")
        if (
            self.service_token is not None
            and self.review_token is not None
            and self.service_token == self.review_token
        ):
            raise ValueError(
                "AI_FACTORY_SERVICE_TOKEN and AI_FACTORY_REVIEW_TOKEN must differ"
            )
        for name, value in (
            ("AI_FACTORY_SERVICE_TOKEN_EXPIRES_AT", self.service_token_expires_at),
            ("AI_FACTORY_REVIEW_TOKEN_EXPIRES_AT", self.review_token_expires_at),
        ):
            if value is not None and (
                value.tzinfo is None or value.utcoffset() is None
            ):
                raise ValueError(f"{name} must include a timezone")

    @property
    def database_path(self) -> Path:
        return self.data_dir / "ai-strategy-factory.db"

    @classmethod
    def from_env(cls) -> "Settings":
        def optional_token(name: str) -> str | None:
            value = os.getenv(name, "").strip()
            if not value:
                return None
            if len(value) < 32:
                raise ValueError(f"{name} must contain at least 32 characters")
            return value

        def optional_expiry(name: str) -> datetime | None:
            value = os.getenv(name, "").strip()
            if not value:
                return None
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(
                    f"{name} must be a valid ISO 8601 timestamp"
                ) from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError(f"{name} must include a timezone")
            return parsed

        port_text = os.getenv("AI_FACTORY_PORT", "8000")
        try:
            port = int(port_text)
        except ValueError as exc:
            raise ValueError("AI_FACTORY_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("AI_FACTORY_PORT must be between 1 and 65535")

        provider = os.getenv("AI_FACTORY_PROVIDER", "fake").strip().lower()
        if provider not in {"fake", "ollama", "openai"}:
            raise ValueError(
                "AI_FACTORY_PROVIDER must be 'fake', 'ollama', or 'openai'"
            )

        ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://127.0.0.1:11888"
        ).rstrip("/")
        parsed_ollama_url = urlparse(ollama_base_url)
        if parsed_ollama_url.scheme not in {"http", "https"} or not parsed_ollama_url.netloc:
            raise ValueError("OLLAMA_BASE_URL must be an absolute HTTP(S) URL")

        ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:31b").strip()
        if not ollama_model:
            raise ValueError("OLLAMA_MODEL must not be empty")

        quality_mode = os.getenv("AI_FACTORY_QUALITY_MODE", "basic").strip().lower()
        if quality_mode not in {"basic", "pro"}:
            raise ValueError("AI_FACTORY_QUALITY_MODE must be 'basic' or 'pro'")

        ollama_quality_model = os.getenv(
            "OLLAMA_QUALITY_MODEL", ollama_model
        ).strip()
        if not ollama_quality_model:
            raise ValueError("OLLAMA_QUALITY_MODEL must not be empty")

        timeout_text = os.getenv("OLLAMA_TIMEOUT_SECONDS", "300")
        try:
            ollama_timeout_seconds = float(timeout_text)
        except ValueError as exc:
            raise ValueError("OLLAMA_TIMEOUT_SECONDS must be a number") from exc
        if not 1 <= ollama_timeout_seconds <= 1800:
            raise ValueError("OLLAMA_TIMEOUT_SECONDS must be between 1 and 1800")

        service_token = optional_token("AI_FACTORY_SERVICE_TOKEN")
        review_token = optional_token("AI_FACTORY_REVIEW_TOKEN")
        if (
            service_token is not None
            and review_token is not None
            and service_token == review_token
        ):
            raise ValueError(
                "AI_FACTORY_SERVICE_TOKEN and AI_FACTORY_REVIEW_TOKEN must differ"
            )

        return cls(
            host=os.getenv("AI_FACTORY_HOST", "127.0.0.1"),
            port=port,
            host_url=os.getenv(
                "AI_FACTORY_HOST_URL", "http://127.0.0.1:8000"
            ).rstrip("/"),
            n8n_url=os.getenv(
                "AI_FACTORY_N8N_URL", "http://host.docker.internal:8000"
            ).rstrip("/"),
            provider=provider,
            ollama_base_url=ollama_base_url,
            ollama_model=ollama_model,
            quality_mode=quality_mode,
            ollama_quality_model=ollama_quality_model,
            ollama_timeout_seconds=ollama_timeout_seconds,
            data_dir=Path(
                os.getenv("AI_FACTORY_DATA_DIR", str(REPOSITORY_ROOT / "data"))
            ),
            artifact_dir=Path(
                os.getenv(
                    "AI_FACTORY_ARTIFACT_DIR",
                    str(REPOSITORY_ROOT / "artifacts"),
                )
            ),
            service_token=service_token,
            review_token=review_token,
            service_token_expires_at=optional_expiry(
                "AI_FACTORY_SERVICE_TOKEN_EXPIRES_AT"
            ),
            review_token_expires_at=optional_expiry(
                "AI_FACTORY_REVIEW_TOKEN_EXPIRES_AT"
            ),
        )
