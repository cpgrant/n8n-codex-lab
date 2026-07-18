"""Database engine foundation and legacy SQLite schema helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine import make_url

SCHEMA_VERSION = 5


def create_database_engine(database_url: str) -> Engine:
    """Create a synchronous SQLAlchemy engine for an approved backend."""
    url = make_url(database_url)
    backend = url.get_backend_name()
    if backend not in {"sqlite", "postgresql"}:
        raise ValueError("database URL must use SQLite or PostgreSQL")

    options: dict[str, Any] = {"pool_pre_ping": True}
    if backend == "sqlite":
        if url.database and url.database != ":memory:":
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)
        options["connect_args"] = {"timeout": 5.0}

    engine = create_engine(url, **options)
    if backend == "sqlite":

        @event.listens_for(engine, "connect")
        def configure_sqlite(dbapi_connection: Any, _: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA busy_timeout = 5000")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.close()

    return engine


def check_database_connection(engine: Engine) -> None:
    """Raise when the configured database cannot execute a trivial query."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def engine_for_target(target: Path | str | Engine) -> Engine:
    """Return a shared engine or create one for a legacy path/URL target."""
    if isinstance(target, Engine):
        return target
    if isinstance(target, Path):
        return create_database_engine(f"sqlite:///{target}")
    if "://" not in target:
        return create_database_engine(f"sqlite:///{Path(target)}")
    return create_database_engine(target)


def sqlite_path_for_target(target: Path | str | Engine) -> Path | None:
    """Preserve the legacy repository.database_path compatibility surface."""
    if isinstance(target, Path):
        return target
    engine = engine_for_target(target)
    if engine.dialect.name != "sqlite" or not engine.url.database:
        return None
    return Path(engine.url.database)


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database(database_path: Path) -> None:
    with connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS strategy_runs (
                run_id TEXT PRIMARY KEY,
                status TEXT NOT NULL CHECK (status IN (
                    'received', 'generating', 'awaiting_review', 'approved',
                    'artifact_created', 'rejected', 'failed'
                )),
                brief_json TEXT NOT NULL,
                strategy_json TEXT,
                error_code TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS idempotency_requests (
                operation TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                state TEXT NOT NULL CHECK (state IN ('pending', 'completed')),
                response_status INTEGER,
                response_json TEXT,
                run_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (operation, idempotency_key),
                FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS run_reviews (
                run_id TEXT PRIMARY KEY,
                decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
                reviewer TEXT NOT NULL,
                comment TEXT,
                decided_at TEXT NOT NULL,
                draft_checksum TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS run_artifacts (
                run_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                media_type TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS run_quality_reports (
                run_id TEXT PRIMARY KEY,
                report_json TEXT NOT NULL,
                draft_checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES strategy_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS run_quality_artifacts (
                run_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                media_type TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES run_quality_reports(run_id)
            );
            """
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO schema_version (version, applied_at)
            VALUES (?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            """,
            [(version,) for version in range(1, SCHEMA_VERSION + 1)],
        )
