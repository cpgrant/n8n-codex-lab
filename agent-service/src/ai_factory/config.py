"""Environment-backed service configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    host_url: str = "http://127.0.0.1:8000"
    n8n_url: str = "http://host.docker.internal:8000"
    provider: str = "fake"
    data_dir: Path = REPOSITORY_ROOT / "data"
    artifact_dir: Path = REPOSITORY_ROOT / "artifacts"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "ai-strategy-factory.db"

    @classmethod
    def from_env(cls) -> "Settings":
        port_text = os.getenv("AI_FACTORY_PORT", "8000")
        try:
            port = int(port_text)
        except ValueError as exc:
            raise ValueError("AI_FACTORY_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("AI_FACTORY_PORT must be between 1 and 65535")

        provider = os.getenv("AI_FACTORY_PROVIDER", "fake").strip().lower()
        if provider not in {"fake", "openai"}:
            raise ValueError("AI_FACTORY_PROVIDER must be 'fake' or 'openai'")

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
            data_dir=Path(
                os.getenv("AI_FACTORY_DATA_DIR", str(REPOSITORY_ROOT / "data"))
            ),
            artifact_dir=Path(
                os.getenv(
                    "AI_FACTORY_ARTIFACT_DIR",
                    str(REPOSITORY_ROOT / "artifacts"),
                )
            ),
        )
