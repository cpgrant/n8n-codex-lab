"""Local synthetic factory backup creation and integrity verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

MANIFEST_NAME = "manifest.json"
BACKUP_FORMAT_VERSION = "0.1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BACKUP_ROOT = REPOSITORY_ROOT / "backups" / "ai-strategy-factory"


class BackupError(RuntimeError):
    """Raised when backup creation or verification fails safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise BackupError(f"unsafe backup manifest path: {value}")
    return relative


def _copy_artifacts(source: Path, target: Path) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise BackupError(f"artifact symlinks are not supported: {relative}")
        if path.is_dir():
            continue
        if path.name == ".gitkeep":
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def _sqlite_backup(source: Path, target: Path) -> None:
    if not source.is_file():
        raise BackupError(f"factory database does not exist: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_uri = f"{source.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(source_uri, uri=True) as source_connection:
            with sqlite3.connect(target) as target_connection:
                source_connection.backup(target_connection)
                target_connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                target_connection.execute("PRAGMA journal_mode=DELETE")
                result = target_connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()
    except sqlite3.Error as exc:
        raise BackupError("SQLite online backup failed") from exc
    if result is None or result[0] != "ok":
        raise BackupError("SQLite backup failed its integrity check")
    for suffix in ("-shm", "-wal"):
        Path(f"{target}{suffix}").unlink(missing_ok=True)


def _inventory(snapshot_root: Path) -> dict[str, dict[str, object]]:
    inventory: dict[str, dict[str, object]] = {}
    for path in sorted(snapshot_root.rglob("*")):
        if path.is_symlink():
            raise BackupError(
                f"backup inventory contains a symlink: "
                f"{path.relative_to(snapshot_root)}"
            )
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        relative = path.relative_to(snapshot_root).as_posix()
        inventory[relative] = {
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
        }
    return inventory


def _write_manifest(
    snapshot_root: Path, created_at: datetime
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "format_version": BACKUP_FORMAT_VERSION,
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "database": "data/ai-strategy-factory.db",
        "artifacts": "artifacts",
        "files": _inventory(snapshot_root),
    }
    manifest_path = snapshot_root / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(manifest_path, 0o600)
    return manifest


def create_backup(
    database_path: Path,
    artifact_dir: Path,
    backup_root: Path,
    *,
    created_at: datetime | None = None,
) -> Path:
    """Create one immutable local backup using SQLite's online backup API."""

    timestamp = created_at or datetime.now(UTC)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise BackupError("backup timestamp must include a timezone")
    backup_root.mkdir(parents=True, exist_ok=True)
    os.chmod(backup_root, 0o700)
    name = timestamp.astimezone(UTC).strftime(
        "factory-backup-%Y%m%dT%H%M%S%fZ"
    )
    target = backup_root / name
    temporary = backup_root / f".{name}.tmp-{uuid4().hex}"
    if target.exists():
        raise BackupError(f"backup already exists: {target}")
    try:
        temporary.mkdir(mode=0o700)
        _sqlite_backup(
            database_path, temporary / "data" / "ai-strategy-factory.db"
        )
        _copy_artifacts(artifact_dir, temporary / "artifacts")
        _write_manifest(temporary, timestamp.astimezone(UTC))
        for path in temporary.rglob("*"):
            if path.is_dir():
                os.chmod(path, 0o700)
            elif path.is_file():
                os.chmod(path, 0o600)
        os.replace(temporary, target)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return target


def _load_manifest(snapshot_root: Path) -> dict[str, object]:
    manifest_path = snapshot_root / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BackupError("backup manifest is missing or invalid") from exc
    if manifest.get("format_version") != BACKUP_FORMAT_VERSION:
        raise BackupError("unsupported backup format version")
    if not isinstance(manifest.get("files"), dict):
        raise BackupError("backup manifest file inventory is invalid")
    return manifest


def _verify_manifest_files(
    snapshot_root: Path, manifest: dict[str, object]
) -> None:
    files = manifest["files"]
    assert isinstance(files, dict)
    expected = set(files)
    actual = set(_inventory(snapshot_root))
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise BackupError(
            f"backup inventory mismatch; missing={missing}, "
            f"unexpected={unexpected}"
        )
    for relative_text, metadata in files.items():
        if not isinstance(relative_text, str) or not isinstance(metadata, dict):
            raise BackupError("backup manifest file entry is invalid")
        relative = _safe_relative_path(relative_text)
        path = snapshot_root / relative
        expected_hash = metadata.get("sha256")
        expected_size = metadata.get("size_bytes")
        if _sha256(path) != expected_hash or path.stat().st_size != expected_size:
            raise BackupError(f"backup checksum mismatch: {relative_text}")


def _verify_database_and_artifacts(
    snapshot_root: Path, manifest: dict[str, object]
) -> dict[str, int]:
    database_relative = manifest.get("database")
    artifacts_relative = manifest.get("artifacts")
    if not isinstance(database_relative, str) or not isinstance(
        artifacts_relative, str
    ):
        raise BackupError("backup manifest locations are invalid")
    database_path = snapshot_root / _safe_relative_path(database_relative)
    artifacts_root = snapshot_root / _safe_relative_path(artifacts_relative)
    try:
        with sqlite3.connect(database_path) as connection:
            integrity = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()
            if integrity is None or integrity[0] != "ok":
                raise BackupError("restored SQLite database is not integral")
            run_count = connection.execute(
                "SELECT COUNT(*) FROM strategy_runs"
            ).fetchone()[0]
            strategy_artifacts = connection.execute(
                "SELECT filename, checksum FROM run_artifacts"
            ).fetchall()
            quality_artifacts = connection.execute(
                "SELECT filename, checksum FROM run_quality_artifacts"
            ).fetchall()
    except sqlite3.Error as exc:
        raise BackupError("backup SQLite validation failed") from exc

    artifact_records = [
        (artifacts_root / filename, checksum)
        for filename, checksum in strategy_artifacts
    ]
    artifact_records.extend(
        (artifacts_root / "quality-reports" / filename, checksum)
        for filename, checksum in quality_artifacts
    )
    for path, expected_checksum in artifact_records:
        if not path.is_file():
            raise BackupError(
                f"database references missing artifact: {path.name}"
            )
        if f"sha256:{_sha256(path)}" != expected_checksum:
            raise BackupError(
                f"database artifact checksum mismatch: {path.name}"
            )
    return {
        "runs": int(run_count),
        "strategy_artifacts": len(strategy_artifacts),
        "quality_artifacts": len(quality_artifacts),
    }


def verify_backup(snapshot_root: Path) -> dict[str, int]:
    """Verify the manifest, SQLite integrity, and recorded artifact checksums."""

    manifest = _load_manifest(snapshot_root)
    _verify_manifest_files(snapshot_root, manifest)
    return _verify_database_and_artifacts(snapshot_root, manifest)


def restore_test(snapshot_root: Path) -> dict[str, int]:
    """Copy a backup into temporary restore storage and verify the copy."""

    manifest = _load_manifest(snapshot_root)
    with tempfile.TemporaryDirectory(prefix="ai-factory-restore-test-") as value:
        restored = Path(value) / "restored"
        shutil.copytree(snapshot_root, restored)
        _verify_manifest_files(restored, manifest)
        return _verify_database_and_artifacts(restored, manifest)


def expired_backups(
    backup_root: Path,
    *,
    retention_days: int,
    now: datetime | None = None,
) -> list[Path]:
    """Return expired backup directories without deleting them."""

    if retention_days < 1:
        raise BackupError("backup retention must be at least one day")
    reference = now or datetime.now(UTC)
    if reference.tzinfo is None or reference.utcoffset() is None:
        raise BackupError("retention reference time must include a timezone")
    cutoff = reference.astimezone(UTC) - timedelta(days=retention_days)
    expired: list[Path] = []
    if not backup_root.exists():
        return expired
    for path in sorted(backup_root.glob("factory-backup-*")):
        if not path.is_dir():
            continue
        try:
            manifest = _load_manifest(path)
            created_at = datetime.fromisoformat(
                str(manifest["created_at"]).replace("Z", "+00:00")
            )
        except (BackupError, KeyError, ValueError) as exc:
            raise BackupError(
                f"cannot audit backup retention for {path.name}"
            ) from exc
        if created_at < cutoff:
            expired.append(path)
    return expired


def _settings_paths() -> tuple[Path, Path]:
    from .config import Settings

    settings = Settings.from_env()
    if settings.database_backend != "sqlite":
        raise BackupError(
            "PostgreSQL backup support is not implemented until Platform P1.4"
        )
    return settings.database_path, settings.artifact_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stage 9.3-lite local synthetic factory backup tool."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument(
        "--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT
    )

    for command in ("verify", "restore-test"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("backup", type=Path)

    audit_parser = subparsers.add_parser("audit-expired")
    audit_parser.add_argument(
        "--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT
    )
    audit_parser.add_argument("--retention-days", type=int, default=30)

    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            database_path, artifact_dir = _settings_paths()
            backup = create_backup(
                database_path, artifact_dir, args.backup_root
            )
            print(backup)
        elif args.command == "verify":
            counts = verify_backup(args.backup)
            print(json.dumps(counts, sort_keys=True))
        elif args.command == "restore-test":
            counts = restore_test(args.backup)
            print(json.dumps(counts, sort_keys=True))
        else:
            for path in expired_backups(
                args.backup_root, retention_days=args.retention_days
            ):
                print(path)
    except BackupError as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
