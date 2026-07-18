import sqlite3

import pytest

from ai_factory.data_migration import (
    DataMigrationError,
    _fingerprint,
    main,
    read_sqlite_snapshot,
    validate_artifacts,
)
from ai_factory.database import initialize_database


def test_sqlite_snapshot_counts_and_fingerprints_are_stable(tmp_path, brief):
    from ai_factory.repository import RunRepository

    database_path = tmp_path / "source.db"
    initialize_database(database_path)
    RunRepository(database_path).create(brief)

    first = read_sqlite_snapshot(database_path)
    second = read_sqlite_snapshot(database_path)

    assert first.counts["strategy_runs"] == 1
    assert first.counts["idempotency_requests"] == 0
    assert first.fingerprints == second.fingerprints
    assert first.rows == second.rows


def test_snapshot_rejects_missing_schema(tmp_path):
    database_path = tmp_path / "incomplete.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE strategy_runs (run_id TEXT PRIMARY KEY)")

    with pytest.raises(DataMigrationError, match="missing required tables"):
        read_sqlite_snapshot(database_path)


def test_fingerprint_detects_value_changes():
    original = _fingerprint(({"id": "one", "value": 1},))
    changed = _fingerprint(({"id": "one", "value": 2},))

    assert original.startswith("sha256:")
    assert original != changed


def test_artifact_validation_rejects_missing_file(tmp_path):
    database_path = tmp_path / "source.db"
    initialize_database(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO strategy_runs (
                run_id, status, brief_json, created_at, updated_at
            ) VALUES ('00000000-0000-0000-0000-000000000001', 'approved',
                      '{}', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """
        )
        connection.execute(
            """
            INSERT INTO run_artifacts (
                run_id, filename, media_type, checksum, created_at
            ) VALUES ('00000000-0000-0000-0000-000000000001',
                      'strategy-00000000-0000-0000-0000-000000000001.md',
                      'text/markdown', :checksum, '2026-01-01T00:00:00Z')
            """,
            {"checksum": "sha256:" + "a" * 64},
        )

    snapshot = read_sqlite_snapshot(database_path)
    with pytest.raises(DataMigrationError, match="is missing"):
        validate_artifacts(snapshot, tmp_path / "artifacts")


def test_cli_requires_target_url(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("AI_FACTORY_POSTGRES_MIGRATION_URL", raising=False)

    with pytest.raises(SystemExit) as stopped:
        main(
            [
                "plan",
                "--source",
                str(tmp_path / "source.db"),
                "--artifact-dir",
                str(tmp_path / "artifacts"),
            ]
        )

    assert stopped.value.code == 1
    assert "AI_FACTORY_POSTGRES_MIGRATION_URL is required" in capsys.readouterr().err
