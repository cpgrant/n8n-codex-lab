import sqlite3

from sqlalchemy import inspect

from ai_factory.database import (
    SCHEMA_VERSION,
    check_database_connection,
    create_database_engine,
    initialize_database,
)
from ai_factory.migrations import upgrade_database


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
        "run_quality_artifacts",
    } <= tables


def test_portable_engine_connects_to_sqlite(tmp_path):
    database_path = tmp_path / "nested" / "portable.db"
    engine = create_database_engine(f"sqlite:///{database_path}")

    check_database_connection(engine)

    assert database_path.exists()
    engine.dispose()


def test_versioned_migration_creates_current_schema_on_fresh_sqlite(tmp_path):
    database_path = tmp_path / "migrated.db"
    database_url = f"sqlite:///{database_path}"

    upgrade_database(database_url)
    upgrade_database(database_url)

    engine = create_database_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        versions = connection.exec_driver_sql(
            "SELECT version FROM schema_version ORDER BY version"
        ).fetchall()
        alembic_revision = connection.exec_driver_sql(
            "SELECT version_num FROM alembic_version"
        ).scalar_one()
    engine.dispose()

    assert versions == [(version,) for version in range(1, SCHEMA_VERSION + 1)]
    assert alembic_revision == "0001_current_factory_schema"
    assert {
        "strategy_runs",
        "idempotency_requests",
        "run_reviews",
        "run_artifacts",
        "run_quality_reports",
        "run_quality_artifacts",
    } <= tables
