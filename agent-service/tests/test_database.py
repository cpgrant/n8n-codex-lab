import sqlite3

from ai_factory.database import SCHEMA_VERSION, initialize_database


def test_schema_v2_is_initialized_and_repeatable(tmp_path):
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
    assert versions == [(1,), (SCHEMA_VERSION,)]
    assert {"strategy_runs", "idempotency_requests"} <= tables
