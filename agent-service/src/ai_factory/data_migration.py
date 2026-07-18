"""Dry-run-first SQLite to PostgreSQL migration and reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from sqlalchemy import Engine, inspect, text

from .database import create_database_engine

TARGET_URL_ENV = "AI_FACTORY_POSTGRES_MIGRATION_URL"


class DataMigrationError(RuntimeError):
    """Raised when migration safety or reconciliation checks fail."""


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[str, ...]
    primary_key: tuple[str, ...]


TABLES = (
    TableSpec(
        "strategy_runs",
        (
            "run_id",
            "status",
            "brief_json",
            "strategy_json",
            "error_code",
            "error_message",
            "created_at",
            "updated_at",
        ),
        ("run_id",),
    ),
    TableSpec(
        "run_quality_reports",
        ("run_id", "report_json", "draft_checksum", "created_at"),
        ("run_id",),
    ),
    TableSpec(
        "run_quality_artifacts",
        ("run_id", "filename", "media_type", "checksum", "created_at"),
        ("run_id",),
    ),
    TableSpec(
        "run_reviews",
        (
            "run_id",
            "decision",
            "reviewer",
            "comment",
            "decided_at",
            "draft_checksum",
        ),
        ("run_id",),
    ),
    TableSpec(
        "run_artifacts",
        ("run_id", "filename", "media_type", "checksum", "created_at"),
        ("run_id",),
    ),
    TableSpec(
        "idempotency_requests",
        (
            "operation",
            "idempotency_key",
            "request_hash",
            "state",
            "response_status",
            "response_json",
            "run_id",
            "created_at",
            "updated_at",
        ),
        ("operation", "idempotency_key"),
    ),
)


@dataclass(frozen=True)
class DatabaseSnapshot:
    rows: dict[str, tuple[dict[str, Any], ...]]
    counts: dict[str, int]
    fingerprints: dict[str, str]


def _fingerprint(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        encoded = json.dumps(
            dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        digest.update(encoded)
        digest.update(b"\n")
    return f"sha256:{digest.hexdigest()}"


def _file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _snapshot(rows: dict[str, tuple[dict[str, Any], ...]]) -> DatabaseSnapshot:
    return DatabaseSnapshot(
        rows=rows,
        counts={name: len(values) for name, values in rows.items()},
        fingerprints={name: _fingerprint(values) for name, values in rows.items()},
    )


def read_sqlite_snapshot(database_path: Path) -> DatabaseSnapshot:
    """Read a consistent online SQLite snapshot without modifying the source."""

    if not database_path.is_file():
        raise DataMigrationError(f"SQLite source does not exist: {database_path}")
    try:
        source_uri = f"{database_path.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(source_uri, uri=True) as source:
            with sqlite3.connect(":memory:") as snapshot:
                source.backup(snapshot)
                integrity = snapshot.execute("PRAGMA integrity_check").fetchone()
                if integrity is None or integrity[0] != "ok":
                    raise DataMigrationError("SQLite source failed its integrity check")
                foreign_key_errors = snapshot.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                if foreign_key_errors:
                    raise DataMigrationError(
                        "SQLite source contains foreign-key violations"
                    )
                existing_tables = {
                    row[0]
                    for row in snapshot.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                expected_tables = {spec.name for spec in TABLES}
                missing = sorted(expected_tables - existing_tables)
                if missing:
                    raise DataMigrationError(
                        f"SQLite source is missing required tables: {missing}"
                    )
                rows: dict[str, tuple[dict[str, Any], ...]] = {}
                for spec in TABLES:
                    columns = ", ".join(spec.columns)
                    order = ", ".join(spec.primary_key)
                    cursor = snapshot.execute(
                        f"SELECT {columns} FROM {spec.name} ORDER BY {order}"
                    )
                    rows[spec.name] = tuple(
                        dict(zip(spec.columns, values, strict=True))
                        for values in cursor.fetchall()
                    )
    except sqlite3.Error as exc:
        raise DataMigrationError("SQLite source could not be read") from exc
    return _snapshot(rows)


def validate_artifacts(
    snapshot: DatabaseSnapshot, artifact_dir: Path
) -> dict[str, int]:
    """Verify every database-referenced artifact before migration."""

    groups = (
        ("strategy_artifacts", snapshot.rows["run_artifacts"], artifact_dir),
        (
            "quality_artifacts",
            snapshot.rows["run_quality_artifacts"],
            artifact_dir / "quality-reports",
        ),
    )
    counts: dict[str, int] = {}
    for label, rows, root in groups:
        counts[label] = len(rows)
        for row in rows:
            filename = str(row["filename"])
            if Path(filename).name != filename:
                raise DataMigrationError(
                    f"artifact metadata contains an unsafe filename: {filename}"
                )
            path = root / filename
            if not path.is_file():
                raise DataMigrationError(
                    f"artifact referenced by the database is missing: {filename}"
                )
            if _file_checksum(path) != row["checksum"]:
                raise DataMigrationError(
                    f"artifact checksum does not match the database: {filename}"
                )
    return counts


def _validate_postgresql_target(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        raise DataMigrationError("migration target must use PostgreSQL")
    try:
        tables = set(inspect(engine).get_table_names())
        required = {"alembic_version", *(spec.name for spec in TABLES)}
        missing = sorted(required - tables)
        if missing:
            raise DataMigrationError(
                f"PostgreSQL target is missing migrated tables: {missing}"
            )
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one_or_none()
        if revision != "0001_current_factory_schema":
            raise DataMigrationError(
                "PostgreSQL target is not at revision 0001_current_factory_schema"
            )
    except DataMigrationError:
        raise
    except Exception as exc:
        raise DataMigrationError("PostgreSQL target could not be inspected") from exc


def read_target_snapshot(engine: Engine) -> DatabaseSnapshot:
    _validate_postgresql_target(engine)
    rows: dict[str, tuple[dict[str, Any], ...]] = {}
    try:
        with engine.connect() as connection:
            for spec in TABLES:
                columns = ", ".join(spec.columns)
                order = ", ".join(spec.primary_key)
                result = connection.execute(
                    text(f"SELECT {columns} FROM {spec.name} ORDER BY {order}")
                ).mappings()
                rows[spec.name] = tuple(dict(row) for row in result)
    except Exception as exc:
        raise DataMigrationError("PostgreSQL target data could not be read") from exc
    return _snapshot(rows)


def _comparison(
    source: DatabaseSnapshot, target: DatabaseSnapshot
) -> dict[str, dict[str, object]]:
    return {
        spec.name: {
            "source_count": source.counts[spec.name],
            "target_count": target.counts[spec.name],
            "count_match": source.counts[spec.name] == target.counts[spec.name],
            "fingerprint_match": (
                source.fingerprints[spec.name] == target.fingerprints[spec.name]
            ),
        }
        for spec in TABLES
    }


def plan_migration(
    source_path: Path, target_url: str, artifact_dir: Path | None = None
) -> dict[str, object]:
    source = read_sqlite_snapshot(source_path)
    artifact_counts = (
        validate_artifacts(source, artifact_dir) if artifact_dir else None
    )
    engine = create_database_engine(target_url)
    try:
        target = read_target_snapshot(engine)
    finally:
        engine.dispose()
    target_empty = all(count == 0 for count in target.counts.values())
    return {
        "mode": "dry-run",
        "source_counts": source.counts,
        "target_counts": target.counts,
        "target_empty": target_empty,
        "eligible_to_apply": target_empty,
        "artifact_counts": artifact_counts,
        "writes_performed": False,
    }


def reconcile(
    source_path: Path, target_url: str, artifact_dir: Path | None = None
) -> dict[str, object]:
    source = read_sqlite_snapshot(source_path)
    artifact_counts = (
        validate_artifacts(source, artifact_dir) if artifact_dir else None
    )
    engine = create_database_engine(target_url)
    try:
        target = read_target_snapshot(engine)
    finally:
        engine.dispose()
    tables = _comparison(source, target)
    matched = all(
        value["count_match"] and value["fingerprint_match"]
        for value in tables.values()
    )
    return {
        "matched": matched,
        "artifact_counts": artifact_counts,
        "tables": tables,
    }


def apply_migration(
    source_path: Path,
    target_url: str,
    *,
    confirm_empty_target: bool,
    artifact_dir: Path | None = None,
) -> dict[str, object]:
    if not confirm_empty_target:
        raise DataMigrationError(
            "apply requires --confirm-empty-target after reviewing a dry run"
        )
    source = read_sqlite_snapshot(source_path)
    artifact_counts = (
        validate_artifacts(source, artifact_dir) if artifact_dir else None
    )
    engine = create_database_engine(target_url)
    try:
        _validate_postgresql_target(engine)
        with engine.begin() as connection:
            for spec in TABLES:
                count = connection.execute(
                    text(f"SELECT COUNT(*) FROM {spec.name}")
                ).scalar_one()
                if count != 0:
                    raise DataMigrationError(
                        f"PostgreSQL target is not empty: {spec.name} has {count} rows"
                    )
            for spec in TABLES:
                values = source.rows[spec.name]
                if not values:
                    continue
                columns = ", ".join(spec.columns)
                placeholders = ", ".join(f":{column}" for column in spec.columns)
                connection.execute(
                    text(
                        f"INSERT INTO {spec.name} ({columns}) "
                        f"VALUES ({placeholders})"
                    ),
                    list(values),
                )
        target = read_target_snapshot(engine)
    except DataMigrationError:
        raise
    except Exception as exc:
        raise DataMigrationError(
            "PostgreSQL import failed; the target transaction was rolled back"
        ) from exc
    finally:
        engine.dispose()
    tables = _comparison(source, target)
    matched = all(
        value["count_match"] and value["fingerprint_match"]
        for value in tables.values()
    )
    if not matched:
        raise DataMigrationError("PostgreSQL import failed reconciliation")
    return {
        "mode": "apply",
        "matched": True,
        "artifact_counts": artifact_counts,
        "tables": tables,
    }


def _target_url() -> str:
    value = os.getenv(TARGET_URL_ENV, "").strip()
    if not value:
        raise DataMigrationError(f"{TARGET_URL_ENV} is required")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run-first SQLite to PostgreSQL migration tool."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "apply", "reconcile"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--source", type=Path, required=True)
        command_parser.add_argument("--artifact-dir", type=Path, required=True)
        if command == "apply":
            command_parser.add_argument(
                "--confirm-empty-target", action="store_true"
            )
    args = parser.parse_args(argv)
    try:
        target_url = _target_url()
        if args.command == "plan":
            result = plan_migration(args.source, target_url, args.artifact_dir)
        elif args.command == "apply":
            result = apply_migration(
                args.source,
                target_url,
                confirm_empty_target=args.confirm_empty_target,
                artifact_dir=args.artifact_dir,
            )
        else:
            result = reconcile(args.source, target_url, args.artifact_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.command == "reconcile" and not result["matched"]:
            return 1
    except DataMigrationError as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
