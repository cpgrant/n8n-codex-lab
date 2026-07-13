from ai_factory.artifacts import sha256_text
from ai_factory.database import initialize_database
from ai_factory.providers import FakeStrategyProvider
from ai_factory.quality_artifacts import QualityMarkdownArtifactStore
from ai_factory.quality_service import QualityReportService
from ai_factory.repository import RunRepository
from ai_factory.schemas import QualityArtifactMetadata, QualityReport
from ai_factory.service import StrategyService


def test_quality_markdown_is_advisory_atomic_and_checksum_protected(
    tmp_path, brief, response_fixture
):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = StrategyService(
        repository, FakeStrategyProvider(response_fixture)
    ).create_run(brief)
    store = QualityMarkdownArtifactStore(tmp_path / "artifacts")

    created = QualityReportService(
        repository, mode="basic", artifact_store=store
    ).create_report(run.run_id)

    metadata = QualityArtifactMetadata.model_validate(created.quality_artifact)
    path = store.path_for(run.run_id, metadata)
    content = path.read_text(encoding="utf-8")
    assert path.parent.name == "quality-reports"
    assert metadata.filename == f"quality-report-{run.run_id}.md"
    assert metadata.checksum == sha256_text(content)
    assert "not an approval" in content
    assert "cannot approve, reject, or rewrite" in content
    assert "## Scorecard" in content
    assert not list(path.parent.glob("*.tmp"))


def test_quality_markdown_escapes_untrusted_report_text(
    tmp_path, brief, response_fixture
):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = StrategyService(
        repository, FakeStrategyProvider(response_fixture)
    ).create_run(brief)
    store = QualityMarkdownArtifactStore(tmp_path / "artifacts")
    service = QualityReportService(
        repository, mode="basic", artifact_store=store
    )
    created = service.create_report(run.run_id)
    report = dict(created.quality_report)
    report["strengths"] = ["[unsafe](https://example.invalid) # heading"]

    content = store.render(QualityReport.model_validate(report))

    assert "\\[unsafe\\]\\(https://example\\.invalid\\) \\# heading" in content
