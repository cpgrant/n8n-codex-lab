from datetime import UTC, datetime, timedelta
import stat

import pytest

from ai_factory.artifacts import MarkdownArtifactStore
from ai_factory.backup import (
    BackupError,
    create_backup,
    expired_backups,
    main,
    restore_test,
    verify_backup,
)
from ai_factory.database import initialize_database
from ai_factory.providers import FakeStrategyProvider
from ai_factory.quality_artifacts import QualityMarkdownArtifactStore
from ai_factory.quality_service import QualityReportService
from ai_factory.repository import RunRepository
from ai_factory.review_service import ReviewService
from ai_factory.schemas import ReviewRequest
from ai_factory.service import StrategyService


def populated_factory(tmp_path, brief, response_fixture):
    data_dir = tmp_path / "data"
    artifact_dir = tmp_path / "artifacts"
    database_path = data_dir / "ai-strategy-factory.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = StrategyService(
        repository, FakeStrategyProvider(response_fixture)
    ).create_run(brief)
    QualityReportService(
        repository,
        artifact_store=QualityMarkdownArtifactStore(artifact_dir),
    ).create_report(run.run_id)
    ReviewService(
        repository, MarkdownArtifactStore(artifact_dir)
    ).review_run(
        run.run_id,
        ReviewRequest(
            decision="approved",
            reviewer="synthetic-backup-reviewer",
            comment="Synthetic backup fixture.",
        ),
    )
    return database_path, artifact_dir


def test_backup_creation_verification_and_restore(
    tmp_path, brief, response_fixture
):
    database_path, artifact_dir = populated_factory(
        tmp_path, brief, response_fixture
    )
    backup = create_backup(
        database_path,
        artifact_dir,
        tmp_path / "backups",
        created_at=datetime(2026, 7, 16, 9, 0, tzinfo=UTC),
    )

    expected = {
        "runs": 1,
        "strategy_artifacts": 1,
        "quality_artifacts": 1,
    }
    assert verify_backup(backup) == expected
    assert restore_test(backup) == expected
    assert (backup / "manifest.json").is_file()
    assert not (backup / "data" / "ai-strategy-factory.db-wal").exists()
    assert not (backup / "data" / "ai-strategy-factory.db-shm").exists()
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o700
        for path in [
            backup.parent,
            backup,
            *(item for item in backup.rglob("*") if item.is_dir()),
        ]
    )
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o600
        for path in backup.rglob("*")
        if path.is_file()
    )


def test_backup_verification_rejects_tampered_artifact(
    tmp_path, brief, response_fixture
):
    database_path, artifact_dir = populated_factory(
        tmp_path, brief, response_fixture
    )
    backup = create_backup(
        database_path, artifact_dir, tmp_path / "backups"
    )
    strategy_artifact = next((backup / "artifacts").glob("strategy-*.md"))
    strategy_artifact.write_text("tampered\n", encoding="utf-8")

    with pytest.raises(BackupError, match="checksum mismatch"):
        verify_backup(backup)


def test_backup_requires_an_existing_database(tmp_path):
    with pytest.raises(BackupError, match="does not exist"):
        create_backup(
            tmp_path / "missing.db",
            tmp_path / "artifacts",
            tmp_path / "backups",
        )


def test_expired_backup_audit_never_deletes(
    tmp_path, brief, response_fixture
):
    database_path, artifact_dir = populated_factory(
        tmp_path, brief, response_fixture
    )
    created_at = datetime(2026, 6, 1, 9, 0, tzinfo=UTC)
    backup = create_backup(
        database_path,
        artifact_dir,
        tmp_path / "backups",
        created_at=created_at,
    )

    expired = expired_backups(
        tmp_path / "backups",
        retention_days=30,
        now=created_at + timedelta(days=31),
    )

    assert expired == [backup]
    assert backup.is_dir()


def test_sqlite_backup_command_fails_closed_for_postgresql(monkeypatch, capsys):
    monkeypatch.setenv(
        "AI_FACTORY_DATABASE_URL",
        "postgresql+psycopg://ai_factory:synthetic@127.0.0.1:5432/ai_factory",
    )

    with pytest.raises(SystemExit) as stopped:
        main(["create"])

    assert stopped.value.code == 1
    assert "P1.4" in capsys.readouterr().err
