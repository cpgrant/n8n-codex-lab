"""Programmatic Alembic helpers for AI Factory database schemas."""

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config

AGENT_SERVICE_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_CONFIG_PATH = AGENT_SERVICE_ROOT / "alembic.ini"
MIGRATION_ROOT = AGENT_SERVICE_ROOT / "migrations"


def migration_config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option("script_location", str(MIGRATION_ROOT))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def upgrade_database(database_url: str, revision: str = "head") -> None:
    command.upgrade(migration_config(database_url), revision)


def main() -> None:
    database_url = os.getenv("AI_FACTORY_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("AI_FACTORY_DATABASE_URL is required")
    upgrade_database(database_url)


if __name__ == "__main__":
    main()
