import sqlite3

from ai_factory.database import SCHEMA_VERSION, initialize_database


def test_current_schema_is_initialized_and_repeatable(tmp_path):
    database_path = tmp_path / "runs.db"

    initialize_database(database_path)
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        versions = connection.execute(
            "SELECT version FROM schema_version ORDER BY version"
        ).fetchall()
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert versions == [(version,) for version in range(1, SCHEMA_VERSION + 1)]
    assert {
        "strategy_runs",
        "idempotency_requests",
        "run_reviews",
        "run_artifacts",
        "run_quality_reports",
    } <= tables
