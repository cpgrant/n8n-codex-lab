"""Small SQLite connection and schema initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 4


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
            """
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO schema_version (version, applied_at)
            VALUES (?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            """,
            [(version,) for version in range(1, SCHEMA_VERSION + 1)],
        )
